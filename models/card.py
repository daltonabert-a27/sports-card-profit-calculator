"""Card data model."""

from dataclasses import dataclass, field


@dataclass
class Card:
    card_id: str = ""
    description: str = ""
    year: int | None = None
    set_name: str = ""
    player_name: str = ""
    card_number: str = ""
    parallel: str = ""
    sport: str = "Basketball"
    is_graded: bool = False
    grading_company: str = ""
    grade: str = ""
    status: str = "Inventory"
    notes: str = ""
