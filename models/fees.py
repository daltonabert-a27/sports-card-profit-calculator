"""Fee structure data models."""

from dataclasses import dataclass


@dataclass
class FeeProfile:
    profile_name: str = "eBay Standard (No Store)"
    platform: str = "eBay"
    fvf_rate: float = 0.1325
    fvf_cap_amount: float = 7500.00
    fvf_rate_above_cap: float = 0.0235
    per_order_fee_low: float = 0.30
    per_order_fee_high: float = 0.40
    per_order_threshold: float = 10.00
    intl_fee_rate: float = 0.0165


@dataclass
class ShippingOption:
    method_name: str = ""
    carrier: str = ""
    cost: float = 0.0
    max_weight_oz: float | None = None
    max_value: float | None = None
    graded_eligible: bool = True
    notes: str = ""
