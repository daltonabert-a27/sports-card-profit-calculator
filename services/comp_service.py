"""Comp aggregation service — median, average, stats from any source."""

import statistics
from database.repository import CompRepository


class CompService:
    def __init__(self, conn):
        self.repo = CompRepository(conn)

    def add_manual_comp(self, search_query: str, title: str, sold_price: float,
                        shipping_price: float = 0.0, sold_date: str = "",
                        condition: str = "", item_url: str = "", card_id: str | None = None):
        self.repo.add({
            "search_query": search_query,
            "card_id": card_id,
            "title": title,
            "sold_price": sold_price,
            "shipping_price": shipping_price,
            "sold_date": sold_date,
            "condition": condition,
            "item_url": item_url,
            "source": "manual",
        })

    def get_comp_stats(self, query: str, days: int = 90) -> dict:
        comps = self.repo.get_by_query(query, days)
        if not comps:
            return {
                "count": 0,
                "median": 0.0,
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "comps": [],
            }

        prices = [c["sold_price"] for c in comps]
        return {
            "count": len(prices),
            "median": round(statistics.median(prices), 2),
            "average": round(statistics.mean(prices), 2),
            "min": round(min(prices), 2),
            "max": round(max(prices), 2),
            "comps": comps,
        }

    def get_all_comps(self) -> list[dict]:
        return self.repo.get_all()
