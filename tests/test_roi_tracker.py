"""Unit tests for ROI tracker service."""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.schema import initialize_database
from services.roi_tracker import ROITracker


def _make_db():
    """Create an in-memory DB with schema initialized."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    initialize_database(conn)
    return conn


def _add_card(conn, card_id, description="Test Card", status="Inventory"):
    conn.execute(
        "INSERT INTO cards (card_id, description, status) VALUES (?, ?, ?)",
        (card_id, description, status),
    )
    conn.commit()


def _add_purchase(conn, card_id, price=10.0, tax=0.63, shipping=0.0, grading=0.0):
    conn.execute(
        """INSERT INTO purchases (card_id, purchase_date, purchase_price,
           sales_tax_paid, shipping_paid, grading_cost)
           VALUES (?, '2025-01-15', ?, ?, ?, ?)""",
        (card_id, price, tax, shipping, grading),
    )
    conn.commit()


def _add_sale(conn, card_id, sale_price=50.0, net_proceeds=42.0):
    conn.execute(
        """INSERT INTO sales (card_id, sale_date, sale_price, net_proceeds, total_fees)
           VALUES (?, '2025-02-01', ?, ?, ?)""",
        (card_id, sale_price, net_proceeds, sale_price - net_proceeds),
    )
    conn.commit()


def test_empty_portfolio():
    conn = _make_db()
    tracker = ROITracker(conn)
    summary = tracker.get_portfolio_summary()
    assert summary["total_invested"] == 0
    assert summary["total_revenue"] == 0
    assert summary["total_profit"] == 0
    assert summary["cards_purchased"] == 0
    assert summary["cards_sold"] == 0
    assert summary["cards_in_inventory"] == 0


def test_portfolio_with_purchases_only():
    conn = _make_db()
    _add_card(conn, "CARD-000001", status="Inventory")
    _add_purchase(conn, "CARD-000001", price=10.0, tax=0.63)

    _add_card(conn, "CARD-000002", status="Inventory")
    _add_purchase(conn, "CARD-000002", price=20.0, tax=1.25)

    tracker = ROITracker(conn)
    summary = tracker.get_portfolio_summary()

    assert summary["cards_purchased"] == 2
    assert summary["cards_sold"] == 0
    assert summary["cards_in_inventory"] == 2
    assert summary["total_invested"] == 31.88  # 10.63 + 21.25
    assert summary["total_revenue"] == 0
    assert summary["total_profit"] == -31.88


def test_portfolio_with_sale():
    conn = _make_db()
    _add_card(conn, "CARD-000001", status="Sold")
    _add_purchase(conn, "CARD-000001", price=10.0, tax=0.63)
    _add_sale(conn, "CARD-000001", sale_price=50.0, net_proceeds=42.0)

    tracker = ROITracker(conn)
    summary = tracker.get_portfolio_summary()

    assert summary["cards_purchased"] == 1
    assert summary["cards_sold"] == 1
    assert summary["cards_in_inventory"] == 0
    assert summary["total_invested"] == 10.63
    assert summary["total_revenue"] == 42.0
    assert summary["total_profit"] == 31.37
    assert summary["overall_roi_pct"] == 295.11  # (31.37 / 10.63) * 100
    assert summary["avg_profit_per_card"] == 31.37


def test_inventory_with_details():
    conn = _make_db()
    _add_card(conn, "CARD-000001", description="Jokic Prizm", status="Sold")
    _add_purchase(conn, "CARD-000001", price=10.0, tax=0.0)
    _add_sale(conn, "CARD-000001", sale_price=50.0, net_proceeds=42.0)

    _add_card(conn, "CARD-000002", description="LeBron Select", status="Inventory")
    _add_purchase(conn, "CARD-000002", price=25.0, tax=0.0)

    tracker = ROITracker(conn)
    rows = tracker.get_inventory_with_details()

    assert len(rows) == 2
    # Most recent first
    sold = [r for r in rows if r["status"] == "Sold"]
    unsold = [r for r in rows if r["status"] == "Inventory"]
    assert len(sold) == 1
    assert len(unsold) == 1
    assert sold[0]["net_proceeds"] == 42.0
    assert unsold[0]["sale_price"] is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
