"""Real-time stream health and ingestion metrics."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class StreamMetrics:
    """Tracks operational statistics for decoded telemetry streams."""

    total_frames_received: int = 0
    valid_frames_decoded: int = 0
    crc_errors: int = 0
    invalid_headers: int = 0
    dropped_frames: int = 0
    last_sequence_id: int = -1

    def record_frame(
        self, sequence_id: int, is_valid: bool, error_type: Optional[str] = None
    ) -> None:
        """Updates stream metrics based on decoded packet validity."""
        self.total_frames_received += 1
        if is_valid:
            self.valid_frames_decoded += 1
            if self.last_sequence_id >= 0 and sequence_id > (self.last_sequence_id + 1):
                self.dropped_frames += sequence_id - self.last_sequence_id - 1
            self.last_sequence_id = sequence_id
        else:
            if error_type == "crc":
                self.crc_errors += 1
            elif error_type == "header":
                self.invalid_headers += 1

    @property
    def packet_loss_rate(self) -> float:
        """Calculates percentage packet loss across observed frame sequence."""
        total_expected = self.valid_frames_decoded + self.dropped_frames
        if total_expected == 0:
            return 0.0
        return (self.dropped_frames / total_expected) * 100.0

    @property
    def health_summary(self) -> Dict[str, float | int]:
        """Returns structured dictionary of stream health indicators."""
        return {
            "total_received": self.total_frames_received,
            "valid_decoded": self.valid_frames_decoded,
            "dropped": self.dropped_frames,
            "crc_errors": self.crc_errors,
            "loss_rate_pct": round(self.packet_loss_rate, 2),
        }
