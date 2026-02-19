"""Main application window."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from database.connection import get_connection, close_connection
from database.schema import initialize_database
from config.settings import SettingsManager

from gui.tabs.profit_calculator import ProfitCalculatorTab
from gui.tabs.deal_analyzer import DealAnalyzerTab
from gui.tabs.sold_comps import SoldCompsTab
from gui.tabs.breakeven import BreakevenTab
from gui.tabs.roi_tracker import ROITrackerTab
from gui.tabs.settings import SettingsTab


class App(ttk.Window):
    def __init__(self):
        super().__init__(
            title="Sports Card Profit Calculator & Deal Analyzer",
            themename="darkly",
            size=(1100, 750),
            minsize=(900, 600),
        )

        # Initialize database
        self.conn = get_connection()
        initialize_database(self.conn)
        self.settings = SettingsManager(self.conn)
        self.settings.seed_defaults()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill=X)
        ttk.Label(
            header,
            text="Sports Card Profit Calculator",
            font=("-size", 18, "-weight", "bold"),
            bootstyle="inverse-primary",
            padding=(10, 5),
        ).pack(fill=X)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self, padding=5)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        self.tab_profit = ProfitCalculatorTab(self.notebook, self.conn, self.settings)
        self.tab_deals = DealAnalyzerTab(self.notebook, self.conn, self.settings)
        self.tab_comps = SoldCompsTab(self.notebook, self.conn, self.settings)
        self.tab_breakeven = BreakevenTab(self.notebook, self.conn, self.settings)
        self.tab_roi = ROITrackerTab(self.notebook, self.conn, self.settings)
        self.tab_settings = SettingsTab(self.notebook, self.conn, self.settings)

        self.notebook.add(self.tab_profit, text="  Profit Calculator  ")
        self.notebook.add(self.tab_deals, text="  Deal Analyzer  ")
        self.notebook.add(self.tab_comps, text="  Sold Comps  ")
        self.notebook.add(self.tab_breakeven, text="  Break-even  ")
        self.notebook.add(self.tab_roi, text="  ROI Tracker  ")
        self.notebook.add(self.tab_settings, text="  Settings  ")

    def _on_close(self):
        close_connection()
        self.destroy()
