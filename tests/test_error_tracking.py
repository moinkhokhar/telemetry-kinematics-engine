from src.core.error_tracking import ErrorTracker
from src.core.exceptions import ChecksumMismatchError


def test_error_tracker_captures_exception() -> None:
    tracker = ErrorTracker()
    error = ChecksumMismatchError("CRC failed for payload")

    report = tracker.capture_exception(error, error_code="ERR_CRC_FAILED", context={"seq": 105})

    assert report.error_code == "ERR_CRC_FAILED"
    assert report.error_type == "ChecksumMismatchError"
    assert report.context["seq"] == 105
    assert tracker.total_incidents == 1

    incidents = tracker.get_latest_incidents()
    assert len(incidents) == 1
    assert incidents[0]["code"] == "ERR_CRC_FAILED"
