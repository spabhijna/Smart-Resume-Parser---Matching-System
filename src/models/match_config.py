from dataclasses import dataclass


@dataclass
class MatchConfig:
    # Component weights (must sum to 1.0)
    required_weight: float = 0.60
    preferred_weight: float = 0.15
    experience_weight: float = 0.15
    education_weight: float = 0.10

    # Required skill behavior
    required_decay: float = 0.7
    min_required_floor: float = 0.2

    # Experience behavior
    under_exp_penalty: float = 0.3
    over_exp_decay: float = 0.15
    over_exp_floor: float = 0.6
