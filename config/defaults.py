"""Default configuration values for fees, tax, grading, and shipping."""

# eBay Fee Defaults (2025-2026 - Trading Cards category)
DEFAULT_FVF_RATE = 0.1325              # 13.25% Final Value Fee (includes payment processing)
DEFAULT_FVF_CAP = 7500.00             # Tiered rate applies above this amount
DEFAULT_FVF_RATE_ABOVE_CAP = 0.0235   # 2.35% above cap
DEFAULT_PER_ORDER_FEE_LOW = 0.30      # Orders <= $10
DEFAULT_PER_ORDER_FEE_HIGH = 0.40     # Orders > $10
DEFAULT_PER_ORDER_THRESHOLD = 10.00   # Threshold between low/high per-order fee
DEFAULT_INTL_FEE_RATE = 0.0165        # 1.65% international fee

# Tax Defaults
DEFAULT_SALES_TAX_RATE = 0.0625       # Illinois state rate 6.25%

# Shipping Defaults
DEFAULT_SHIPPING_OPTIONS = [
    {
        "method_name": "eBay Standard Envelope - 1oz",
        "carrier": "eBay",
        "cost": 0.56,
        "max_weight_oz": 1.0,
        "max_value": 20.00,
        "graded_eligible": False,
        "notes": "Raw cards only, max 3 cards",
    },
    {
        "method_name": "eBay Standard Envelope - 2oz",
        "carrier": "eBay",
        "cost": 1.03,
        "max_weight_oz": 2.0,
        "max_value": 20.00,
        "graded_eligible": False,
        "notes": "Raw cards only, max 8 cards",
    },
    {
        "method_name": "eBay Standard Envelope - 3oz",
        "carrier": "eBay",
        "cost": 1.30,
        "max_weight_oz": 3.0,
        "max_value": 20.00,
        "graded_eligible": False,
        "notes": "Raw cards only, max 15 cards",
    },
    {
        "method_name": "USPS Ground Advantage - 4oz (Commercial)",
        "carrier": "USPS",
        "cost": 4.63,
        "max_weight_oz": 4.0,
        "max_value": None,
        "graded_eligible": True,
        "notes": "Bubble mailer, graded or raw",
    },
    {
        "method_name": "USPS Ground Advantage - 8oz (Commercial)",
        "carrier": "USPS",
        "cost": 5.13,
        "max_weight_oz": 8.0,
        "max_value": None,
        "graded_eligible": True,
        "notes": "Small box, multiple graded cards",
    },
    {
        "method_name": "USPS Ground Advantage - 4oz (Retail)",
        "carrier": "USPS",
        "cost": 7.30,
        "max_weight_oz": 4.0,
        "max_value": None,
        "graded_eligible": True,
        "notes": "At post office counter",
    },
]

# Grading Service Defaults (2025-2026)
DEFAULT_GRADING_SERVICES = [
    {"company": "PSA", "tier": "Value", "cost": 24.00, "days": 150, "max_value": 499},
    {"company": "PSA", "tier": "Regular", "cost": 40.00, "days": 30, "max_value": 999},
    {"company": "PSA", "tier": "Express", "cost": 75.00, "days": 5, "max_value": 2499},
    {"company": "PSA", "tier": "Super Express", "cost": 150.00, "days": 2, "max_value": 4999},
    {"company": "BGS", "tier": "Base", "cost": 14.95, "days": 70, "max_value": 499},
    {"company": "BGS", "tier": "Standard", "cost": 35.00, "days": 20, "max_value": 999},
    {"company": "SGC", "tier": "Regular", "cost": 24.00, "days": 15, "max_value": 499},
    {"company": "SGC", "tier": "Express", "cost": 50.00, "days": 5, "max_value": 2499},
    {"company": "CGC", "tier": "Bulk (25+)", "cost": 12.00, "days": 42, "max_value": 250},
    {"company": "CGC", "tier": "Economy", "cost": 15.00, "days": 30, "max_value": 250},
    {"company": "CGC", "tier": "Standard", "cost": 18.00, "days": 20, "max_value": 499},
]

# Default Fee Profile
DEFAULT_FEE_PROFILES = [
    {
        "profile_name": "eBay Standard (No Store)",
        "platform": "eBay",
        "fvf_rate": 0.1325,
        "fvf_cap_amount": 7500.00,
        "fvf_rate_above_cap": 0.0235,
        "per_order_fee_low": 0.30,
        "per_order_fee_high": 0.40,
        "per_order_threshold": 10.00,
        "intl_fee_rate": 0.0165,
        "is_default": True,
    },
    {
        "profile_name": "eBay Basic Store",
        "platform": "eBay",
        "fvf_rate": 0.1275,
        "fvf_cap_amount": 7500.00,
        "fvf_rate_above_cap": 0.0235,
        "per_order_fee_low": 0.30,
        "per_order_fee_high": 0.40,
        "per_order_threshold": 10.00,
        "intl_fee_rate": 0.0165,
        "is_default": False,
    },
]
