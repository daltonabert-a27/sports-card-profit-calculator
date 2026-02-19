"""Sold Comps tab - placeholder for v0.1."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class SoldCompsTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=20)
        self.conn = conn
        self.settings = settings

        ttk.Label(
            self,
            text="eBay Sold Comps",
            font=("-size", 16, "-weight", "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            self,
            text="Search eBay listings and log sold prices to compare against your cost.",
            wraplength=600,
        ).pack(pady=(0, 20))

        ttk.Label(
            self,
            text="Coming in v0.4",
            font=("-size", 12),
            bootstyle="secondary",
        ).pack(expand=True)
