"""Break-even analysis: graded vs raw comparison."""

from services.calculator import calculate_profit


def graded_vs_raw_breakeven(
    raw_cost_basis: float,
    grading_cost: float,
    grading_company: str,
    expected_grade: str,
    raw_market_value: float,
    graded_market_value: float,
    fvf_rate: float = 0.1325,
    per_order_fee_low: float = 0.30,
    per_order_fee_high: float = 0.40,
    per_order_threshold: float = 10.0,
    raw_shipping_cost: float = 0.56,
    graded_shipping_cost: float = 4.63,
) -> dict:
    """Compare selling raw now vs grading then selling.

    Returns profit for both scenarios plus the breakeven graded sale price.
    """
    # Scenario A: Sell raw
    raw_result = calculate_profit(
        sale_price=raw_market_value,
        shipping_charged=0.0,
        cost_basis=raw_cost_basis,
        shipping_cost=raw_shipping_cost,
        fvf_rate=fvf_rate,
        per_order_fee_low=per_order_fee_low,
        per_order_fee_high=per_order_fee_high,
        per_order_threshold=per_order_threshold,
    )
    raw_profit = raw_result["net_profit"]

    # Scenario B: Grade then sell
    graded_cost_basis = raw_cost_basis + grading_cost
    graded_result = calculate_profit(
        sale_price=graded_market_value,
        shipping_charged=0.0,
        cost_basis=graded_cost_basis,
        shipping_cost=graded_shipping_cost,
        fvf_rate=fvf_rate,
        per_order_fee_low=per_order_fee_low,
        per_order_fee_high=per_order_fee_high,
        per_order_threshold=per_order_threshold,
    )
    graded_profit = graded_result["net_profit"]

    # Breakeven: find graded sale price where graded_profit == raw_profit
    # graded_sale * (1 - fvf_rate) - per_order_fee - graded_shipping - graded_cost_basis = raw_profit
    per_order = per_order_fee_high  # conservative estimate
    breakeven_graded_price = (
        (raw_profit + per_order + graded_shipping_cost + graded_cost_basis)
        / (1 - fvf_rate)
    )

    grading_extra_profit = graded_profit - raw_profit
    grading_roi = (grading_extra_profit / grading_cost * 100) if grading_cost > 0 else 0.0

    return {
        "raw_profit": round(raw_profit, 2),
        "raw_net_proceeds": raw_result["net_proceeds"],
        "raw_total_fees": raw_result["total_fees"],
        "graded_profit": round(graded_profit, 2),
        "graded_net_proceeds": graded_result["net_proceeds"],
        "graded_total_fees": graded_result["total_fees"],
        "grading_extra_profit": round(grading_extra_profit, 2),
        "grading_roi_pct": round(grading_roi, 2),
        "breakeven_graded_price": round(max(breakeven_graded_price, 0), 2),
        "recommendation": "GRADE" if graded_profit > raw_profit else "SELL RAW",
        "grading_company": grading_company,
        "expected_grade": expected_grade,
        "grading_cost": grading_cost,
        "raw_cost_basis": raw_cost_basis,
        "graded_cost_basis": round(graded_cost_basis, 2),
    }


def multi_service_breakeven(
    raw_cost_basis: float,
    raw_market_value: float,
    graded_market_value: float,
    expected_grade: str,
    grading_options: list[dict],
    **kwargs,
) -> list[dict]:
    """Compare breakeven across multiple grading services/tiers.

    grading_options: list of dicts with keys: company, tier, cost
    """
    results = []
    for opt in grading_options:
        result = graded_vs_raw_breakeven(
            raw_cost_basis=raw_cost_basis,
            grading_cost=opt["cost"],
            grading_company=opt["company"],
            expected_grade=expected_grade,
            raw_market_value=raw_market_value,
            graded_market_value=graded_market_value,
            **kwargs,
        )
        result["tier"] = opt.get("tier", "")
        results.append(result)

    return sorted(results, key=lambda r: r["graded_profit"], reverse=True)
