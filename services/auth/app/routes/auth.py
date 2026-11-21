from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mlp_common.jwt_utils import verify_token

from ..config import Settings
from ..db import get_db
from ..models import User
from ..quota import get_usage
from ..schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from ..security import create_access_token, hash_password, verify_password
from ..rate_limit import rate_limit_dependency

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(rate_limit_dependency)])
settings = Settings()


def current_user_id(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    payload = verify_token(authorization.removeprefix("Bearer ").strip(), settings.JWT_SECRET)
    user = db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = User(id=uuid4(), email=str(payload.email).lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    token = create_access_token(user.id, settings.JWT_SECRET, settings.TOKEN_TTL_MINUTES)
    return TokenResponse(access_token=token)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id, settings.JWT_SECRET, settings.TOKEN_TTL_MINUTES)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user_id), db: Session = Depends(get_db)):
    _, limit = get_usage(db, user.id, settings.FREE_MODEL_LIMIT)
    return UserOut(id=user.id, email=user.email, plan=user.plan, models_trained=user.models_trained,
                   models_reserved=user.models_reserved, limit=limit)
