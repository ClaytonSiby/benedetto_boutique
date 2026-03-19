web: bash prestart.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
worker: celery -A app.worker.celery_app worker --loglevel=info
