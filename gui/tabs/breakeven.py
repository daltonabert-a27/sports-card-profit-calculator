"""Break-even Analysis tab - placeholder for v0.1."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class BreakevenTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=20)
        self.conn = conn
        self.settings = settings

        ttk.Label(
            self,
            text="Break-even Analysis",
            font=("-size", 16, "-weight", "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            self,
            text="Compare graded vs raw scenarios - find the sale price where grading becomes profitable.",
            wraplength=600,
        ).pack(pady=(0, 20))

        ttk.Label(
            self,
            text="Coming in v0.5",
            font=("-size", 12),
            bootstyle="secondary",
        ).pack(expand=True)
