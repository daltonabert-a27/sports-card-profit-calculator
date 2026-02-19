"""Settings tab - placeholder for v0.1."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class SettingsTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=20)
        self.conn = conn
        self.settings = settings

        ttk.Label(
            self,
            text="Settings",
            font=("-size", 16, "-weight", "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            self,
            text="Configure fee rates, tax rates, shipping costs, grading costs, and eBay API credentials.",
            wraplength=600,
        ).pack(pady=(0, 20))

        ttk.Label(
            self,
            text="Coming in v0.4",
            font=("-size", 12),
            bootstyle="secondary",
        ).pack(expand=True)
