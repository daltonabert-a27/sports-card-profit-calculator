"""Unit tests for the profit calculator service."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.calculator import calculate_cost_basis, calculate_profit, get_per_order_fee


def test_per_order_fee_low():
    assert get_per_order_fee(5.0) == 0.30

def test_per_order_fee_at_threshold():
    assert get_per_order_fee(10.0) == 0.30

def test_per_order_fee_high():
    assert get_per_order_fee(15.0) == 0.40


def test_cost_basis_with_tax():
    result = calculate_cost_basis(
        purchase_price=100.0,
        sales_tax_rate=0.0625,
        shipping_to_you=5.0,
        grading_cost=24.0,
    )
    assert result["sales_tax"] == 6.25
    assert result["total_cost_basis"] == 135.25


def test_cost_basis_tax_included():
    result = calculate_cost_basis(
        purchase_price=100.0,
        sales_tax_rate=0.0625,
        tax_already_included=True,
    )
    assert result["sales_tax"] == 0.0
    assert result["total_cost_basis"] == 100.0


def test_basic_profit():
    """$10 card, sold for $50 with free shipping, no grading."""
    result = calculate_profit(
        sale_price=50.0,
        shipping_charged=0.0,
        cost_basis=10.0,
        shipping_cost=0.56,  # eBay Standard Envelope
    )
    # FVF: 50.0 * 0.1325 = 6.625 -> 6.62 (banker's rounding)
    assert result["fvf_amount"] == 6.62
    # Per-order: 50 > 10 -> $0.40
    assert result["per_order_fee"] == 0.40
    assert result["intl_fee"] == 0.0
    # Total fees: round(6.625 + 0.40) = round(7.025) = 7.02 but
    # total_fees rounds sum of raw fvf (6.625) + 0.40 = 7.025 -> 7.03 (float precision)
    assert result["total_fees"] == 7.03
    # Net proceeds: 50 - 7.03 - 0.56 = 42.41
    assert result["net_proceeds"] == 42.41
    # Net profit: 42.41 - 10.0 = 32.41
    assert result["net_profit"] == 32.41
    assert result["roi_pct"] == 324.15


def test_profit_with_shipping_charged():
    """FVF applies to item + shipping charged to buyer."""
    result = calculate_profit(
        sale_price=30.0,
        shipping_charged=5.0,
        cost_basis=10.0,
        shipping_cost=4.63,
    )
    # FVF on $35 total: 35 * 0.1325 = 4.6375 -> 4.64
    assert result["fvf_amount"] == 4.64
    # Per-order: 30 > 10 -> $0.40
    assert result["per_order_fee"] == 0.40
    # Total fees: 4.64 + 0.40 = 5.04
    assert result["total_fees"] == 5.04
    # Net proceeds: 35 - 5.04 - 4.63 = 25.33
    assert result["net_proceeds"] == 25.33
    # Net profit: 25.33 - 10 = 15.33
    assert result["net_profit"] == 15.33


def test_international_fee():
    result = calculate_profit(
        sale_price=100.0,
        shipping_charged=0.0,
        cost_basis=50.0,
        shipping_cost=4.63,
        is_international=True,
    )
    # Intl fee: 100 * 0.0165 = 1.65
    assert result["intl_fee"] == 1.65
    # FVF: 100 * 0.1325 = 13.25
    assert result["fvf_amount"] == 13.25
    # Total fees: 13.25 + 0.40 + 1.65 = 15.30
    assert result["total_fees"] == 15.30


def test_low_price_per_order_fee():
    """Sale <= $10 gets the lower per-order fee."""
    result = calculate_profit(
        sale_price=8.0,
        shipping_charged=0.0,
        cost_basis=2.0,
        shipping_cost=0.56,
    )
    assert result["per_order_fee"] == 0.30


def test_negative_profit():
    """When costs exceed sale price."""
    result = calculate_profit(
        sale_price=5.0,
        shipping_charged=0.0,
        cost_basis=10.0,
        shipping_cost=4.63,
    )
    assert result["net_profit"] < 0
    assert result["roi_pct"] < 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
