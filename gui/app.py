"""Main application window."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog

from database.connection import get_connection, close_connection
from database.schema import initialize_database
from config.settings import SettingsManager
from services.csv_export import export_inventory, export_sales, export_comps

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

        self._build_menu()
        self._build_ui()
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Inventory (CSV)", command=self._export_inventory,
                              accelerator="Ctrl+E")
        file_menu.add_command(label="Export Sales (CSV)", command=self._export_sales)
        file_menu.add_command(label="Export Comps (CSV)", command=self._export_comps)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Ctrl+Q")

        # Navigate menu
        nav_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navigate", menu=nav_menu)
        nav_menu.add_command(label="Profit Calculator", command=lambda: self.notebook.select(0),
                             accelerator="Ctrl+1")
        nav_menu.add_command(label="Deal Analyzer", command=lambda: self.notebook.select(1),
                             accelerator="Ctrl+2")
        nav_menu.add_command(label="Sold Comps", command=lambda: self.notebook.select(2),
                             accelerator="Ctrl+3")
        nav_menu.add_command(label="Break-even", command=lambda: self.notebook.select(3),
                             accelerator="Ctrl+4")
        nav_menu.add_command(label="ROI Tracker", command=lambda: self.notebook.select(4),
                             accelerator="Ctrl+5")
        nav_menu.add_command(label="Settings", command=lambda: self.notebook.select(5),
                             accelerator="Ctrl+6")

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

    def _bind_shortcuts(self):
        self.bind("<Control-e>", lambda e: self._export_inventory())
        self.bind("<Control-q>", lambda e: self._on_close())
        self.bind("<Control-Key-1>", lambda e: self.notebook.select(0))
        self.bind("<Control-Key-2>", lambda e: self.notebook.select(1))
        self.bind("<Control-Key-3>", lambda e: self.notebook.select(2))
        self.bind("<Control-Key-4>", lambda e: self.notebook.select(3))
        self.bind("<Control-Key-5>", lambda e: self.notebook.select(4))
        self.bind("<Control-Key-6>", lambda e: self.notebook.select(5))

    def _export_inventory(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Inventory",
            initialfile="inventory.csv",
        )
        if filepath:
            result = export_inventory(self.conn, filepath)
            if result:
                Messagebox.ok(f"Inventory exported to:\n{result}", "Export Complete")
            else:
                Messagebox.show_info("No inventory data to export.", "Export")

    def _export_sales(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Sales",
            initialfile="sales.csv",
        )
        if filepath:
            result = export_sales(self.conn, filepath)
            if result:
                Messagebox.ok(f"Sales exported to:\n{result}", "Export Complete")
            else:
                Messagebox.show_info("No sales data to export.", "Export")

    def _export_comps(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Comps",
            initialfile="comps.csv",
        )
        if filepath:
            result = export_comps(self.conn, filepath)
            if result:
                Messagebox.ok(f"Comps exported to:\n{result}", "Export Complete")
            else:
                Messagebox.show_info("No comp data to export.", "Export")

    def _on_close(self):
        close_connection()
        self.destroy()
