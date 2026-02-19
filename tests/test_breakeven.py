"""Unit tests for breakeven analysis service."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.breakeven import graded_vs_raw_breakeven, multi_service_breakeven


def test_grading_profitable():
    """When graded value is much higher than raw, grading should be recommended."""
    result = graded_vs_raw_breakeven(
        raw_cost_basis=10.0,
        grading_cost=24.0,
        grading_company="PSA",
        expected_grade="10",
        raw_market_value=30.0,
        graded_market_value=150.0,
    )
    assert result["recommendation"] == "GRADE"
    assert result["graded_profit"] > result["raw_profit"]
    assert result["grading_extra_profit"] > 0


def test_sell_raw_when_grading_not_worth_it():
    """When graded value isn't much higher, selling raw is better."""
    result = graded_vs_raw_breakeven(
        raw_cost_basis=10.0,
        grading_cost=24.0,
        grading_company="PSA",
        expected_grade="9",
        raw_market_value=20.0,
        graded_market_value=25.0,
    )
    assert result["recommendation"] == "SELL RAW"


def test_breakeven_price_is_above_raw():
    """Breakeven graded price should be higher than raw market value."""
    result = graded_vs_raw_breakeven(
        raw_cost_basis=5.0,
        grading_cost=24.0,
        grading_company="PSA",
        expected_grade="10",
        raw_market_value=15.0,
        graded_market_value=80.0,
    )
    assert result["breakeven_graded_price"] > 15.0


def test_multi_service_sorted_by_profit():
    options = [
        {"company": "CGC", "tier": "Economy", "cost": 15.0},
        {"company": "PSA", "tier": "Value", "cost": 24.0},
        {"company": "BGS", "tier": "Standard", "cost": 35.0},
    ]
    results = multi_service_breakeven(
        raw_cost_basis=10.0,
        raw_market_value=20.0,
        graded_market_value=100.0,
        expected_grade="10",
        grading_options=options,
    )
    profits = [r["graded_profit"] for r in results]
    assert profits == sorted(profits, reverse=True)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
