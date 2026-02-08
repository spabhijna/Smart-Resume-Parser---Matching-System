from dataclasses import dataclass


@dataclass
class ExtractedField:
    value: any
    confidence: float  # 0.0 → 1.0
    source: str  # "rule" | "ml"
