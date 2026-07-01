import pytest
from zerocrawl.anti_detection.headers import get_headers, get_random_profile_name
from zerocrawl.anti_detection.fingerprint import get_curl_cffi_target
from zerocrawl.anti_detection.session import generate_fingerprint_profile, SessionPool

def test_get_headers_chrome120():
    headers = get_headers("chrome120")
    assert "User-Agent" in headers
    assert "Chrome/120" in headers["User-Agent"]
    assert "Accept" in headers
    assert "Sec-Fetch-Dest" in headers

def test_get_headers_firefox():
    headers = get_headers("firefox121")
    assert "Firefox/121" in headers["User-Agent"]

def test_get_headers_fallback():
    headers = get_headers("nonexistent_browser")
    assert "Chrome/120" in headers["User-Agent"]

def test_curl_cffi_target():
    assert get_curl_cffi_target("chrome120") == "chrome120"
    assert get_curl_cffi_target("safari17") == "safari17_2"
    assert get_curl_cffi_target("unknown") == "chrome120"

def test_fingerprint_profile():
    p = generate_fingerprint_profile()
    assert p.profile_id
    assert p.platform in ("Windows", "macOS", "Linux")
    assert p.screen_width > 0
    assert p.hardware_concurrency in [2, 4, 8, 12, 16]

def test_fingerprint_deterministic_seed():
    p1 = generate_fingerprint_profile("test-id-123")
    p2 = generate_fingerprint_profile("test-id-123")
    assert p1.canvas_noise_seed == p2.canvas_noise_seed

def test_session_pool():
    pool = SessionPool(pool_size=1)
    p = pool.get_profile()
    assert p is not None
    assert not p.is_retired

def test_profile_retirement():
    p = generate_fingerprint_profile()
    p.max_requests = 2
    p.record_request(); p.record_request()
    assert p.is_retired
