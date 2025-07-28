from celery import Celery
from celery.schedules import crontab
import asyncio
import logging

from app.tasks.user_tasks import reset_monthly_usage

logger = logging.getLogger(__name__)

celery_app = Celery(
    "creatorhub",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True
)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # ✅ Run on 1st of every month at midnight (UTC)
    sender.add_periodic_task(
        crontab(day_of_month="1", hour="0", minute="0"),
        run_monthly_reset.s(),
        name="Reset monthly usage counters"
    )

@celery_app.task
def run_monthly_reset():
    """
    ✅ Fixed version: Reuses Celery’s running event loop instead of creating new ones.
    """
    try:
        logger.info("STAGE ✅: Running scheduled monthly reset task...")

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(reset_monthly_usage())

        logger.info("✅ Monthly usage counters reset successfully for all users.")
    except Exception as e:
        logger.error(f"❌ Monthly reset task failed: {e}")
