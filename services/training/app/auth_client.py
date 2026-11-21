from uuid import UUID

import httpx

from .config import Settings

settings = Settings()


def reserve_quota(user_id: UUID | str) -> bool:
    response = httpx.post(
        f"{settings.AUTH_URL}/internal/quota/reserve",
        headers={"X-Internal-Key": settings.INTERNAL_API_KEY},
        json={"user_id": str(user_id)},
        timeout=5,
    )
    if response.status_code == 403:
        return False
    response.raise_for_status()
    return bool(response.json().get("allowed"))


def release_quota(user_id: UUID | str) -> None:
    response = httpx.post(
        f"{settings.AUTH_URL}/internal/quota/release",
        headers={"X-Internal-Key": settings.INTERNAL_API_KEY},
        json={"user_id": str(user_id)},
        timeout=5,
    )
    response.raise_for_status()
