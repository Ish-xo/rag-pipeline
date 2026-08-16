import time
from typing import Dict

class PipelineTimer:
    def __init__(self):
        self.timestamps: Dict[str, float] = {}

    def record(self, stage: str):
        """Record the current time for a given stage."""
        self.timestamps[stage] = time.time()

    def get_latency(self, start_stage: str, end_stage: str) -> float:
        """Get latency in milliseconds between two stages."""
        if start_stage in self.timestamps and end_stage in self.timestamps:
            return (self.timestamps[end_stage] - self.timestamps[start_stage]) * 1000.0
        return 0.0

    def get_waterfall(self) -> Dict[str, float]:
        """Return the complete latency waterfall."""
        stages = ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"]
        waterfall = {}
        prev_time = None
        prev_stage = None
        for stage in stages:
            if stage in self.timestamps:
                current = self.timestamps[stage]
                if prev_time is not None:
                    waterfall[f"{prev_stage} -> {stage}"] = (current - prev_time) * 1000.0
                prev_time = current
                prev_stage = stage
        return waterfall
