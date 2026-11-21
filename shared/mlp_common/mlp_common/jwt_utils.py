from datetime import datetime, timezone
from typing import Any

import jwt
from fastapi import Header, HTTPException


def verify_token(token: str, secret: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token")
    exp = payload.get("exp")
    if exp is not None and datetime.fromtimestamp(exp, tz=timezone.utc) <= datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    raise RuntimeError("get_current_user_id requires service secret configuration")
