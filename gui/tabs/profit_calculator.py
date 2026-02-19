"""Profit Calculator tab - placeholder for v0.1."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ProfitCalculatorTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=20)
        self.conn = conn
        self.settings = settings

        ttk.Label(
            self,
            text="Profit Calculator",
            font=("-size", 16, "-weight", "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            self,
            text="Calculate net profit on sports card sales factoring in eBay fees, "
                 "shipping, grading costs, and sales tax.",
            wraplength=600,
        ).pack(pady=(0, 20))

        ttk.Label(
            self,
            text="Coming in v0.2",
            font=("-size", 12),
            bootstyle="secondary",
        ).pack(expand=True)
