"""CSV export service for inventory, sales, and comps data."""

import csv
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def export_inventory(conn, filepath=None) -> str:
    """Export full inventory with purchase/sale details to CSV."""
    _ensure_data_dir()
    if filepath is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(DATA_DIR, f"inventory_{ts}.csv")

    cursor = conn.execute("""
        SELECT
            c.card_id, c.description, c.player_name, c.year, c.set_name,
            c.card_number, c.parallel, c.sport, c.is_graded, c.grading_company,
            c.grade, c.status,
            p.purchase_date, p.purchase_price, p.sales_tax_paid, p.shipping_paid,
            p.grading_cost, p.total_cost_basis, p.source AS purchase_source,
            s.sale_date, s.sale_price, s.shipping_charged, s.shipping_cost,
            s.total_fees, s.net_proceeds, s.platform
        FROM cards c
        LEFT JOIN purchases p ON c.card_id = p.card_id
        LEFT JOIN sales s ON c.card_id = s.card_id
        ORDER BY c.created_at DESC
    """)

    rows = cursor.fetchall()
    if not rows:
        return ""

    headers = [desc[0] for desc in cursor.description]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(list(row))

    return filepath


def export_sales(conn, filepath=None) -> str:
    """Export all sales with calculated profit to CSV."""
    _ensure_data_dir()
    if filepath is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(DATA_DIR, f"sales_{ts}.csv")

    cursor = conn.execute("""
        SELECT
            s.card_id, c.description, c.player_name, c.sport,
            p.purchase_price, p.total_cost_basis,
            s.sale_date, s.sale_price, s.shipping_charged, s.shipping_cost,
            s.ebay_fvf_amount, s.ebay_per_order_fee, s.ebay_intl_fee_amount,
            s.total_fees, s.net_proceeds,
            ROUND(s.net_proceeds - p.total_cost_basis, 2) AS net_profit,
            CASE WHEN p.total_cost_basis > 0
                 THEN ROUND((s.net_proceeds - p.total_cost_basis) / p.total_cost_basis * 100, 2)
                 ELSE 0 END AS roi_pct,
            s.platform
        FROM sales s
        JOIN cards c ON s.card_id = c.card_id
        LEFT JOIN purchases p ON s.card_id = p.card_id
        ORDER BY s.sale_date DESC
    """)

    rows = cursor.fetchall()
    if not rows:
        return ""

    headers = [desc[0] for desc in cursor.description]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(list(row))

    return filepath


def export_comps(conn, filepath=None) -> str:
    """Export all sold comps to CSV."""
    _ensure_data_dir()
    if filepath is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(DATA_DIR, f"comps_{ts}.csv")

    cursor = conn.execute("""
        SELECT search_query, title, sold_price, shipping_price, sold_date,
               condition, item_url, source, fetched_at
        FROM comps
        ORDER BY fetched_at DESC
    """)

    rows = cursor.fetchall()
    if not rows:
        return ""

    headers = [desc[0] for desc in cursor.description]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(list(row))

    return filepath
