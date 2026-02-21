-- Optional: alpha testing usage events (env-gated in app).
-- Run this on the external DB if you enable PROXYFORGE_ALPHA_LOGGING=1.
CREATE TABLE IF NOT EXISTS alpha_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    page VARCHAR(128) DEFAULT NULL,
    detail VARCHAR(512) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_created (created_at),
    INDEX idx_event (event_type)
);
