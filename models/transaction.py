"""Purchase and sale transaction data models."""

from dataclasses import dataclass


@dataclass
class Purchase:
    card_id: str = ""
    purchase_date: str = ""
    purchase_price: float = 0.0
    sales_tax_paid: float = 0.0
    shipping_paid: float = 0.0
    grading_cost: float = 0.0
    grading_company: str = ""
    grading_tier: str = ""
    source: str = ""
    notes: str = ""

    @property
    def total_cost_basis(self) -> float:
        return self.purchase_price + self.sales_tax_paid + self.shipping_paid + self.grading_cost


@dataclass
class Sale:
    card_id: str = ""
    sale_date: str = ""
    sale_price: float = 0.0
    shipping_charged: float = 0.0
    shipping_cost: float = 0.0
    shipping_method: str = ""
    platform: str = "eBay"
    buyer_state: str = ""
    notes: str = ""
