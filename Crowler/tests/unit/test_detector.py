import pytest
from zerocrawl.engine.detector import detect_js_required

STATIC_HTML = "<html><body><h1>Hello</h1><p>" + "Lorem ipsum " * 60 + "</p></body></html>"
NEXTJS_HTML = "<html><body><div id='__NEXT_DATA__'>{}</div><div id='root'></div></body></html>"
CAPTCHA_HTML = "<html><body><div class='g-recaptcha'></div>captcha-challenge here</body></html>"

def test_static_not_js_required():
    r = detect_js_required(STATIC_HTML, 200)
    assert r["needs_browser"] is False

def test_nextjs_detected():
    r = detect_js_required(NEXTJS_HTML, 200)
    assert r["needs_browser"] is True

def test_captcha_detected():
    r = detect_js_required(CAPTCHA_HTML, 200)
    assert r["has_captcha"] is True

def test_403_is_blocked():
    r = detect_js_required(STATIC_HTML, 403)
    assert r["is_blocked"] is True

def test_empty_body():
    r = detect_js_required("", 200)
    assert r["needs_browser"] is True
