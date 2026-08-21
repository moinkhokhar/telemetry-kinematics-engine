from src.api.health import get_health_payload, metrics_collector


def test_health_payload_generation() -> None:
    metrics_collector.record_frame(sequence_id=0, is_valid=True)
    metrics_collector.record_frame(sequence_id=1, is_valid=True)

    payload = get_health_payload()
    assert payload["status"] == "healthy"
    assert payload["metrics"]["valid_decoded"] >= 2
    assert "loss_rate_pct" in payload["metrics"]
