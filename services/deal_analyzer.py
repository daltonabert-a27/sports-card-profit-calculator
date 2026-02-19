"""Deal analyzer / offer comparison service."""

from services.calculator import calculate_profit, get_per_order_fee


def analyze_offer(
    offer_price: float,
    cost_basis: float,
    shipping_cost: float = 0.0,
    shipping_charged_to_buyer: float = 0.0,
    fvf_rate: float = 0.1325,
    fvf_cap: float = 7500.0,
    fvf_rate_above_cap: float = 0.0235,
    per_order_threshold: float = 10.0,
    per_order_fee_low: float = 0.30,
    per_order_fee_high: float = 0.40,
    is_international: bool = False,
    intl_fee_rate: float = 0.0165,
) -> dict:
    """Analyze a single offer against cost basis. Returns NOI and profit metrics."""
    result = calculate_profit(
        sale_price=offer_price,
        shipping_charged=shipping_charged_to_buyer,
        cost_basis=cost_basis,
        shipping_cost=shipping_cost,
        fvf_rate=fvf_rate,
        fvf_cap=fvf_cap,
        fvf_rate_above_cap=fvf_rate_above_cap,
        per_order_threshold=per_order_threshold,
        per_order_fee_low=per_order_fee_low,
        per_order_fee_high=per_order_fee_high,
        is_international=is_international,
        intl_fee_rate=intl_fee_rate,
    )

    return {
        "offer_price": offer_price,
        "total_fees": result["total_fees"],
        "shipping_cost": result["shipping_cost"],
        "net_proceeds": result["net_proceeds"],
        "cost_basis": cost_basis,
        "net_profit": result["net_profit"],
        "profit_margin_pct": result["profit_margin_pct"],
        "roi_pct": result["roi_pct"],
        "recommendation": "ACCEPT" if result["net_profit"] > 0 else "REJECT",
    }


def compare_offers(
    offers: list[dict],
    cost_basis: float,
    fvf_rate: float = 0.1325,
    **kwargs,
) -> list[dict]:
    """Compare multiple offers side-by-side.

    Each offer dict should have:
        - price: float
        - shipping_cost: float (seller's cost)
        - shipping_charged: float (charged to buyer)
        - label: str (optional display label)
        - is_international: bool (optional)
    """
    results = []
    for offer in offers:
        result = analyze_offer(
            offer_price=offer["price"],
            cost_basis=cost_basis,
            shipping_cost=offer.get("shipping_cost", 0.0),
            shipping_charged_to_buyer=offer.get("shipping_charged", 0.0),
            fvf_rate=fvf_rate,
            is_international=offer.get("is_international", False),
            **kwargs,
        )
        result["label"] = offer.get("label", f"${offer['price']:.2f}")
        results.append(result)

    return sorted(results, key=lambda r: r["net_profit"], reverse=True)
