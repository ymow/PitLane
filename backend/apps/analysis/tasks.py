from celery import shared_task
from apps.analysis.fastf1_service import sync_session_data
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, queue='process')
def generate_session_analysis(self, session_id):
    """
    Celery task to trigger FastF1 analysis for a completed session.
    """
    logger.info(f"Task received: generate_session_analysis for session {session_id}")
    try:
        sync_session_data(session_id)
        return f"Analysis completed for {session_id}"
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise e
