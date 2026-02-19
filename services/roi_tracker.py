"""Portfolio ROI tracking service."""

from database.repository import CardRepository, PurchaseRepository, SaleRepository


class ROITracker:
    def __init__(self, conn):
        self.conn = conn
        self.cards = CardRepository(conn)
        self.purchases = PurchaseRepository(conn)
        self.sales = SaleRepository(conn)

    def get_portfolio_summary(self) -> dict:
        all_purchases = self.purchases.get_all()
        all_sales = self.sales.get_all()

        total_invested = sum(p["total_cost_basis"] for p in all_purchases)
        total_revenue = sum(s.get("net_proceeds", 0) or 0 for s in all_sales)
        total_profit = total_revenue - total_invested

        cards_purchased = len(all_purchases)
        cards_sold = len(all_sales)
        cards_in_inventory = cards_purchased - cards_sold

        overall_roi = (total_profit / total_invested * 100) if total_invested > 0 else 0.0
        avg_profit = (total_profit / cards_sold) if cards_sold > 0 else 0.0

        return {
            "total_invested": round(total_invested, 2),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "overall_roi_pct": round(overall_roi, 2),
            "cards_purchased": cards_purchased,
            "cards_sold": cards_sold,
            "cards_in_inventory": cards_in_inventory,
            "avg_profit_per_card": round(avg_profit, 2),
        }

    def get_inventory_with_details(self) -> list[dict]:
        """Get all cards with their purchase and sale details joined."""
        cursor = self.conn.execute("""
            SELECT
                c.card_id, c.description, c.sport, c.is_graded, c.grading_company,
                c.grade, c.status,
                p.purchase_price, p.total_cost_basis, p.purchase_date, p.source,
                s.sale_price, s.net_proceeds, s.sale_date, s.total_fees
            FROM cards c
            LEFT JOIN purchases p ON c.card_id = p.card_id
            LEFT JOIN sales s ON c.card_id = s.card_id
            ORDER BY c.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
