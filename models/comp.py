"""Comparable sold listing data model."""

from dataclasses import dataclass


@dataclass
class SoldComp:
    search_query: str = ""
    card_id: str = ""
    title: str = ""
    sold_price: float = 0.0
    shipping_price: float = 0.0
    sold_date: str = ""
    condition: str = ""
    item_url: str = ""
    source: str = "manual"
