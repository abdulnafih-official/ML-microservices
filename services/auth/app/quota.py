from uuid import UUID

from sqlalchemy import update
from sqlalchemy.orm import Session

from .models import User


def reserve_slot(db: Session, user_id: UUID, limit: int) -> bool:
    result = db.execute(
        update(User)
        .where(User.id == user_id, User.models_reserved < limit)
        .values(models_reserved=User.models_reserved + 1)
    )
    db.commit()
    return result.rowcount == 1


def release_slot(db: Session, user_id: UUID) -> None:
    user = db.get(User, user_id)
    if user and user.models_reserved > 0:
        user.models_reserved -= 1
        db.commit()


def get_usage(db: Session, user_id: UUID, limit: int) -> tuple[int, int]:
    user = db.get(User, user_id)
    return (user.models_reserved if user else 0), limit
