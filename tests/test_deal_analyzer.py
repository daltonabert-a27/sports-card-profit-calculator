"""Unit tests for deal analyzer service."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.deal_analyzer import analyze_offer, compare_offers


def test_accept_profitable_offer():
    result = analyze_offer(offer_price=50.0, cost_basis=10.0)
    assert result["net_profit"] > 0
    assert result["recommendation"] == "ACCEPT"


def test_reject_losing_offer():
    result = analyze_offer(offer_price=5.0, cost_basis=20.0, shipping_cost=4.63)
    assert result["net_profit"] < 0
    assert result["recommendation"] == "REJECT"


def test_compare_offers_sorted_by_profit():
    offers = [
        {"price": 30.0, "shipping_cost": 0.56},
        {"price": 50.0, "shipping_cost": 0.56},
        {"price": 20.0, "shipping_cost": 0.56},
    ]
    results = compare_offers(offers, cost_basis=10.0)
    profits = [r["net_profit"] for r in results]
    assert profits == sorted(profits, reverse=True)
    assert results[0]["offer_price"] == 50.0


def test_offer_with_shipping_charged():
    result = analyze_offer(
        offer_price=40.0,
        cost_basis=15.0,
        shipping_cost=4.63,
        shipping_charged_to_buyer=5.0,
    )
    # FVF on 45.0 total
    assert result["net_profit"] > 0


def test_international_offer():
    domestic = analyze_offer(offer_price=100.0, cost_basis=50.0, is_international=False)
    intl = analyze_offer(offer_price=100.0, cost_basis=50.0, is_international=True)
    assert intl["net_profit"] < domestic["net_profit"]
    assert intl["total_fees"] > domestic["total_fees"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
