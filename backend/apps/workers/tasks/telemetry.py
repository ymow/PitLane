"""Celery tasks for live session polling via OpenF1.

C3 · poll_live_session
  - Runs every minute via Celery Beat
  - Queries OpenF1 for sessions with known session_key in the ±4h window
  - Syncs status (SCHEDULED → ONGOING → COMPLETED) and actual_start/end timestamps
"""
import requests
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.racing.models import Session

logger = logging.getLogger(__name__)

OPENF1_BASE = "https://api.openf1.org/v1"

# OpenF1 status value → our Session.status choice
OPENF1_STATUS_MAP = {
    'Active': 'ONGOING',
    'Completed': 'COMPLETED',
    'Finished': 'COMPLETED',
    'Inactive': 'SCHEDULED',
}

# How far before/after scheduled_start to watch a session
WINDOW_BEFORE_HOURS = 2
WINDOW_AFTER_HOURS = 6


@shared_task
def poll_live_session():
    """Poll OpenF1 for sessions near the current time and sync their status.

    Deliberately lightweight: only fetches sessions that already have an
    openf1_session_key and are in the watch window (SCHEDULED or ONGOING).
    No-ops silently outside of race weekends.
    """
    now = timezone.now()
    window_start = now - timedelta(hours=WINDOW_AFTER_HOURS)
    window_end = now + timedelta(hours=WINDOW_BEFORE_HOURS)

    sessions = Session.objects.filter(
        openf1_session_key__isnull=False,
        status__in=['SCHEDULED', 'ONGOING'],
        scheduled_start__gte=window_start,
        scheduled_start__lte=window_end,
    ).select_related('race')

    if not sessions.exists():
        logger.debug("poll_live_session: no sessions in watch window.")
        return

    logger.info(f"poll_live_session: checking {sessions.count()} session(s).")
    for session in sessions:
        _sync_session_status(session)


def _sync_session_status(session: Session) -> None:
    """Fetch current status from OpenF1 for one session and persist changes."""
    session_key = session.openf1_session_key
    try:
        resp = requests.get(
            f"{OPENF1_BASE}/sessions",
            params={'session_key': session_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.warning(
            f"poll_live_session: OpenF1 request failed "
            f"(session_key={session_key}, session={session}): {e}"
        )
        return

    if not data:
        logger.debug(f"poll_live_session: empty response for session_key={session_key}")
        return

    item = data[0]
    openf1_status = item.get('status', '')
    new_status = OPENF1_STATUS_MAP.get(openf1_status)

    if not new_status:
        logger.debug(
            f"poll_live_session: unrecognised OpenF1 status '{openf1_status}' "
            f"(session_key={session_key})"
        )
        return

    if new_status == session.status:
        return  # No change, nothing to write

    now = timezone.now()
    update_fields = ['status', 'updated_at']

    if new_status == 'ONGOING' and not session.actual_start:
        session.actual_start = now
        update_fields.append('actual_start')

    if new_status == 'COMPLETED' and not session.actual_end:
        session.actual_end = now
        update_fields.append('actual_end')

    session.status = new_status
    session.save(update_fields=update_fields)

    logger.info(
        f"poll_live_session: {session} → {new_status} (openf1_key={session_key})"
    )
