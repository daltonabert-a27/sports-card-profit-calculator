"""CRUD operations for all database tables."""

import sqlite3


class GradingRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_all_active(self) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT * FROM grading_services WHERE is_active = 1 ORDER BY company, cost_per_card"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_company(self, company: str) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT * FROM grading_services WHERE company = ? AND is_active = 1 ORDER BY cost_per_card",
            (company,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_companies(self) -> list[str]:
        cursor = self._conn.execute(
            "SELECT DISTINCT company FROM grading_services WHERE is_active = 1 ORDER BY company"
        )
        return [row[0] for row in cursor.fetchall()]


class ShippingRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_all_active(self) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT * FROM shipping_options WHERE is_active = 1 ORDER BY cost"
        )
        return [dict(row) for row in cursor.fetchall()]


class FeeProfileRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_default(self) -> dict | None:
        cursor = self._conn.execute(
            "SELECT * FROM fee_profiles WHERE is_default = 1 LIMIT 1"
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        cursor = self._conn.execute("SELECT * FROM fee_profiles ORDER BY profile_name")
        return [dict(row) for row in cursor.fetchall()]


class CardRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add(self, card: dict) -> str:
        # Auto-generate card_id
        cursor = self._conn.execute("SELECT MAX(id) FROM cards")
        max_id = cursor.fetchone()[0] or 0
        card_id = f"CARD-{max_id + 1:06d}"

        self._conn.execute(
            """
            INSERT INTO cards (card_id, description, year, set_name, player_name,
                card_number, parallel, sport, is_graded, grading_company, grade, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card_id,
                card["description"],
                card.get("year"),
                card.get("set_name"),
                card.get("player_name"),
                card.get("card_number"),
                card.get("parallel"),
                card.get("sport", "Basketball"),
                int(card.get("is_graded", False)),
                card.get("grading_company"),
                card.get("grade"),
                card.get("status", "Inventory"),
                card.get("notes"),
            ),
        )
        self._conn.commit()
        return card_id

    def get_all(self, status: str | None = None) -> list[dict]:
        if status:
            cursor = self._conn.execute(
                "SELECT * FROM cards WHERE status = ? ORDER BY created_at DESC",
                (status,),
            )
        else:
            cursor = self._conn.execute(
                "SELECT * FROM cards ORDER BY created_at DESC"
            )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, card_id: str) -> dict | None:
        cursor = self._conn.execute(
            "SELECT * FROM cards WHERE card_id = ?", (card_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_status(self, card_id: str, status: str):
        self._conn.execute(
            "UPDATE cards SET status = ?, updated_at = datetime('now') WHERE card_id = ?",
            (status, card_id),
        )
        self._conn.commit()


class PurchaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add(self, purchase: dict):
        self._conn.execute(
            """
            INSERT INTO purchases (card_id, purchase_date, purchase_price, sales_tax_paid,
                shipping_paid, grading_cost, grading_company, grading_tier, source, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                purchase["card_id"],
                purchase["purchase_date"],
                purchase["purchase_price"],
                purchase.get("sales_tax_paid", 0.0),
                purchase.get("shipping_paid", 0.0),
                purchase.get("grading_cost", 0.0),
                purchase.get("grading_company"),
                purchase.get("grading_tier"),
                purchase.get("source"),
                purchase.get("notes"),
            ),
        )
        self._conn.commit()

    def get_all(self) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT * FROM purchases ORDER BY purchase_date DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_card(self, card_id: str) -> dict | None:
        cursor = self._conn.execute(
            "SELECT * FROM purchases WHERE card_id = ? ORDER BY purchase_date DESC LIMIT 1",
            (card_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


class SaleRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add(self, sale: dict):
        self._conn.execute(
            """
            INSERT INTO sales (card_id, sale_date, sale_price, shipping_charged,
                shipping_cost, shipping_method, ebay_fvf_rate, ebay_fvf_amount,
                ebay_per_order_fee, ebay_intl_fee_rate, ebay_intl_fee_amount,
                total_fees, net_proceeds, platform, buyer_state, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sale["card_id"],
                sale["sale_date"],
                sale["sale_price"],
                sale.get("shipping_charged", 0.0),
                sale.get("shipping_cost", 0.0),
                sale.get("shipping_method"),
                sale.get("ebay_fvf_rate", 0.1325),
                sale.get("ebay_fvf_amount"),
                sale.get("ebay_per_order_fee", 0.30),
                sale.get("ebay_intl_fee_rate", 0.0),
                sale.get("ebay_intl_fee_amount", 0.0),
                sale.get("total_fees"),
                sale.get("net_proceeds"),
                sale.get("platform", "eBay"),
                sale.get("buyer_state"),
                sale.get("notes"),
            ),
        )
        self._conn.commit()

    def get_all(self) -> list[dict]:
        cursor = self._conn.execute("SELECT * FROM sales ORDER BY sale_date DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_by_card(self, card_id: str) -> dict | None:
        cursor = self._conn.execute(
            "SELECT * FROM sales WHERE card_id = ? ORDER BY sale_date DESC LIMIT 1",
            (card_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


class CompRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add(self, comp: dict):
        self._conn.execute(
            """
            INSERT INTO comps (search_query, card_id, title, sold_price, shipping_price,
                sold_date, condition, item_url, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                comp["search_query"],
                comp.get("card_id"),
                comp["title"],
                comp["sold_price"],
                comp.get("shipping_price", 0.0),
                comp.get("sold_date"),
                comp.get("condition"),
                comp.get("item_url"),
                comp.get("source", "manual"),
            ),
        )
        self._conn.commit()

    def get_by_query(self, query: str, days: int = 90) -> list[dict]:
        cursor = self._conn.execute(
            """
            SELECT * FROM comps
            WHERE search_query LIKE ?
              AND fetched_at >= datetime('now', ?)
            ORDER BY sold_date DESC
            """,
            (f"%{query}%", f"-{days} days"),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_all(self) -> list[dict]:
        cursor = self._conn.execute("SELECT * FROM comps ORDER BY fetched_at DESC")
        return [dict(row) for row in cursor.fetchall()]
