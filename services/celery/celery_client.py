from celery import Celery
from celery.schedules import crontab

from config import settings

app = Celery(
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)

# app = Celery(
#     broker=f"redis://localhost:{settings.REDIS_PORT}/0",
#     backend=f"redis://localhost:{settings.REDIS_PORT}/0",
# )
