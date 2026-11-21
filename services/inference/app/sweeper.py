import asyncio
import os
import time

from .config import Settings


def sweep_once() -> int:
    settings = Settings()
    cutoff = time.time() - settings.CACHE_TTL_MINUTES * 60
    removed = 0
    if not os.path.isdir(settings.CACHE_DIR):
        return 0
    for name in os.listdir(settings.CACHE_DIR):
        path = os.path.join(settings.CACHE_DIR, name)
        if os.path.isfile(path) and os.stat(path).st_atime < cutoff:
            os.remove(path)
            removed += 1
    return removed


async def run_sweeper(interval_seconds: int = 60) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        sweep_once()
