"""ROI Tracker tab - placeholder for v0.1."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ROITrackerTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=20)
        self.conn = conn
        self.settings = settings

        ttk.Label(
            self,
            text="ROI Tracker",
            font=("-size", 16, "-weight", "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            self,
            text="Log purchases and sales, track cumulative portfolio ROI and profit/loss per card.",
            wraplength=600,
        ).pack(pady=(0, 20))

        ttk.Label(
            self,
            text="Coming in v0.6",
            font=("-size", 12),
            bootstyle="secondary",
        ).pack(expand=True)
