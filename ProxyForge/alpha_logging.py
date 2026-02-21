"""
Optional alpha-testing usage logging. Gated by env PROXYFORGE_ALPHA_LOGGING=1.
Writes anonymous events (page, feature) to DB table alpha_events for debugging and usage insight.
No PII is stored by default. Enable only on the hosted app when you want to collect feedback.
"""
import os
import uuid

_ENABLED = (os.environ.get("PROXYFORGE_ALPHA_LOGGING") or "").strip() in ("1", "true", "yes")


def _session_id():
    try:
        import streamlit as st
        if "alpha_session_id" not in st.session_state:
            st.session_state.alpha_session_id = str(uuid.uuid4())[:16]
        return st.session_state.alpha_session_id
    except Exception:
        return str(uuid.uuid4())[:16]


def log_event(event_type: str, page: str = None, detail: str = None):
    """Log one event to alpha_events if PROXYFORGE_ALPHA_LOGGING is set. Fails silently."""
    if not _ENABLED:
        return
    try:
        from database_utils import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alpha_events (session_id, event_type, page, detail) VALUES (%s, %s, %s, %s)",
            (_session_id(), event_type[:64], (page or "")[:128], (detail or "")[:512])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass  # Do not break the app if table missing or DB error


def log_page_view(page_name: str):
    """Convenience: log a page view (e.g. '40K Army Builder')."""
    log_event("page_view", page=page_name)


def log_feature(feature: str, detail: str = None):
    """Convenience: log a feature use (e.g. 'export_ros', 'add_unit')."""
    log_event("feature", page=feature, detail=detail)
