-- ZeroCrawl SQLite Schema

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    config JSON NOT NULL DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    webhook_url TEXT,
    webhook_secret TEXT,
    stats JSON DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id),
    url TEXT NOT NULL,
    url_fingerprint TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    result_id TEXT,
    error TEXT,
    queued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME
);

CREATE TABLE IF NOT EXISTS results (
    id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id),
    request_id TEXT REFERENCES requests(id),
    url TEXT NOT NULL,
    result JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cache (
    url_fingerprint TEXT PRIMARY KEY,
    result JSON NOT NULL,
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER DEFAULT 3600,
    expires_at DATETIME
);

CREATE TABLE IF NOT EXISTS domain_rules (
    domain TEXT PRIMARY KEY,
    preferred_mode TEXT,
    requires_js BOOLEAN DEFAULT 0,
    last_success_mode TEXT,
    avg_response_ms INTEGER,
    success_rate REAL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_requests_job_id ON requests(job_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_fingerprint ON requests(url_fingerprint);
CREATE INDEX IF NOT EXISTS idx_results_job_id ON results(job_id);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at);
