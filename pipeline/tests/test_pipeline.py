import pytest
from pipeline.core.status_sweep import calculate_status

def test_calculate_status_open():
    status = calculate_status("2099-12-31T00:00:00+00:00", "2020-01-01T00:00:00+00:00")
    assert status == "OPEN"

def test_calculate_status_closed():
    status = calculate_status("2020-12-31T00:00:00+00:00")
    assert status == "CLOSED"

def test_calculate_status_upcoming():
    # If reg_open is in the future
    status = calculate_status("2099-12-31", "2099-01-01")
    assert status == "UPCOMING"
