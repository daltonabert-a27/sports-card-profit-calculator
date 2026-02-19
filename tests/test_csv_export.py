"""Unit tests for CSV export service."""

import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.schema import initialize_database
from services.csv_export import export_inventory, export_sales, export_comps


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    initialize_database(conn)
    return conn


def _seed_data(conn):
    conn.execute(
        "INSERT INTO cards (card_id, description, status) VALUES ('CARD-000001', 'Test Card', 'Sold')"
    )
    conn.execute(
        """INSERT INTO purchases (card_id, purchase_date, purchase_price, sales_tax_paid)
           VALUES ('CARD-000001', '2025-01-15', 10.00, 0.63)"""
    )
    conn.execute(
        """INSERT INTO sales (card_id, sale_date, sale_price, net_proceeds, total_fees)
           VALUES ('CARD-000001', '2025-02-01', 50.00, 42.97, 7.03)"""
    )
    conn.execute(
        """INSERT INTO comps (search_query, title, sold_price, sold_date, source)
           VALUES ('test query', 'Comp Card', 45.00, '2025-01-20', 'manual')"""
    )
    conn.commit()


def test_export_inventory_creates_file():
    conn = _make_db()
    _seed_data(conn)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        path = tmp.name
    try:
        result = export_inventory(conn, path)
        assert result == path
        with open(path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2  # header + 1 data row
        assert "CARD-000001" in lines[1]
    finally:
        os.unlink(path)


def test_export_sales_creates_file():
    conn = _make_db()
    _seed_data(conn)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        path = tmp.name
    try:
        result = export_sales(conn, path)
        assert result == path
        with open(path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert "net_profit" in lines[0]
    finally:
        os.unlink(path)


def test_export_comps_creates_file():
    conn = _make_db()
    _seed_data(conn)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        path = tmp.name
    try:
        result = export_comps(conn, path)
        assert result == path
        with open(path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert "Comp Card" in lines[1]
    finally:
        os.unlink(path)


def test_export_empty_returns_empty_string():
    conn = _make_db()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        path = tmp.name
    try:
        assert export_inventory(conn, path) == ""
        assert export_sales(conn, path) == ""
        assert export_comps(conn, path) == ""
    finally:
        os.unlink(path)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
