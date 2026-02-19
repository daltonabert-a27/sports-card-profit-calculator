"""Core profit and fee calculation engine."""


def get_per_order_fee(sale_price: float, threshold: float = 10.0,
                      fee_low: float = 0.30, fee_high: float = 0.40) -> float:
    return fee_low if sale_price <= threshold else fee_high


def calculate_cost_basis(
    purchase_price: float,
    sales_tax_rate: float = 0.0625,
    tax_already_included: bool = False,
    shipping_to_you: float = 0.0,
    grading_cost: float = 0.0,
) -> dict:
    sales_tax = 0.0 if tax_already_included else purchase_price * sales_tax_rate
    total = purchase_price + sales_tax + shipping_to_you + grading_cost
    return {
        "purchase_price": purchase_price,
        "sales_tax": round(sales_tax, 2),
        "shipping_to_you": shipping_to_you,
        "grading_cost": grading_cost,
        "total_cost_basis": round(total, 2),
    }


def calculate_profit(
    sale_price: float,
    shipping_charged: float,
    cost_basis: float,
    shipping_cost: float,
    fvf_rate: float = 0.1325,
    fvf_cap: float = 7500.0,
    fvf_rate_above_cap: float = 0.0235,
    per_order_fee: float | None = None,
    per_order_threshold: float = 10.0,
    per_order_fee_low: float = 0.30,
    per_order_fee_high: float = 0.40,
    is_international: bool = False,
    intl_fee_rate: float = 0.0165,
) -> dict:
    """Calculate net profit on a card sale.

    eBay FVF applies to total_sale_amount (item price + shipping charged).
    Payment processing is bundled into the FVF — no separate PayPal fee.
    """
    total_sale_amount = sale_price + shipping_charged

    # Tiered FVF
    if total_sale_amount <= fvf_cap:
        fvf_amount = total_sale_amount * fvf_rate
    else:
        fvf_amount = (fvf_cap * fvf_rate) + (
            (total_sale_amount - fvf_cap) * fvf_rate_above_cap
        )

    # Per-order fee (auto-select if not provided)
    if per_order_fee is None:
        per_order_fee = get_per_order_fee(
            sale_price, per_order_threshold, per_order_fee_low, per_order_fee_high
        )

    # International fee
    intl_fee = total_sale_amount * intl_fee_rate if is_international else 0.0

    total_fees = fvf_amount + per_order_fee + intl_fee
    net_proceeds = total_sale_amount - total_fees - shipping_cost
    net_profit = net_proceeds - cost_basis
    profit_margin = (net_profit / sale_price * 100) if sale_price > 0 else 0.0
    roi = (net_profit / cost_basis * 100) if cost_basis > 0 else 0.0

    return {
        "sale_price": sale_price,
        "shipping_charged": shipping_charged,
        "total_sale_amount": round(total_sale_amount, 2),
        "fvf_amount": round(fvf_amount, 2),
        "per_order_fee": round(per_order_fee, 2),
        "intl_fee": round(intl_fee, 2),
        "total_fees": round(total_fees, 2),
        "shipping_cost": round(shipping_cost, 2),
        "cost_basis": round(cost_basis, 2),
        "net_proceeds": round(net_proceeds, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round(profit_margin, 2),
        "roi_pct": round(roi, 2),
    }
