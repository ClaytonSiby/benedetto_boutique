from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "b_boutique",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
    include=["app.worker.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    "app.worker.tasks.send_email": {"queue": "emails"},
    "app.worker.tasks.process_order": {"queue": "orders"},
    "app.worker.tasks.update_inventory": {"queue": "inventory"},
}
