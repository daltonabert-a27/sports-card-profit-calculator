"""Sold Comps tab - search eBay and log sold prices."""

import webbrowser
import urllib.parse
from datetime import date

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from services.ebay_api import EbayApiClient
from services.comp_service import CompService


class SoldCompsTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=15)
        self.conn = conn
        self.settings = settings
        self.comp_service = CompService(conn)
        self._ebay_client = None

        self._build_ui()

    def _get_ebay_client(self) -> EbayApiClient | None:
        client_id = self.settings.get("ebay_client_id")
        client_secret = self.settings.get("ebay_client_secret")
        env = self.settings.get("ebay_environment", "PRODUCTION")
        if not client_id or not client_secret:
            return None
        return EbayApiClient(client_id, client_secret, env)

    def _build_ui(self):
        # Search bar
        search_frame = ttk.Labelframe(self, text="  Search  ", padding=10)
        search_frame.pack(fill=X, pady=(0, 10))

        input_row = ttk.Frame(search_frame)
        input_row.pack(fill=X)

        ttk.Label(input_row, text="Search:").pack(side=LEFT, padx=(0, 5))
        self.search_var = ttk.StringVar()
        self.search_entry = ttk.Entry(input_row, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=LEFT, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._search_ebay_active())

        ttk.Button(
            input_row, text="Search Active Listings", bootstyle="primary",
            command=self._search_ebay_active,
        ).pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            input_row, text="Open eBay Sold (Browser)", bootstyle="info-outline",
            command=self._open_ebay_sold_browser,
        ).pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            input_row, text="+ Add Manual Comp", bootstyle="success-outline",
            command=self._show_add_comp_dialog,
        ).pack(side=LEFT)

        # Stats panel
        stats_frame = ttk.Labelframe(self, text="  Comp Statistics  ", padding=10)
        stats_frame.pack(fill=X, pady=(0, 10))

        stats_row = ttk.Frame(stats_frame)
        stats_row.pack(fill=X)

        self.stat_count = ttk.Label(stats_row, text="Count: --", font=("-size", 11))
        self.stat_count.pack(side=LEFT, padx=15)
        self.stat_median = ttk.Label(stats_row, text="Median: --", font=("-size", 11, "-weight", "bold"))
        self.stat_median.pack(side=LEFT, padx=15)
        self.stat_avg = ttk.Label(stats_row, text="Average: --", font=("-size", 11))
        self.stat_avg.pack(side=LEFT, padx=15)
        self.stat_min = ttk.Label(stats_row, text="Min: --", font=("-size", 11))
        self.stat_min.pack(side=LEFT, padx=15)
        self.stat_max = ttk.Label(stats_row, text="Max: --", font=("-size", 11))
        self.stat_max.pack(side=LEFT, padx=15)

        ttk.Button(
            stats_row, text="Refresh Stats", bootstyle="secondary-outline",
            command=self._refresh_stats,
        ).pack(side=RIGHT)

        # Results table
        results_frame = ttk.Labelframe(self, text="  Results  ", padding=10)
        results_frame.pack(fill=BOTH, expand=True)

        self.tree = ttk.Treeview(
            results_frame,
            columns=("source", "title", "price", "shipping", "condition", "date", "url"),
            show="headings",
            height=12,
        )
        self.tree.heading("source", text="Source")
        self.tree.heading("title", text="Title")
        self.tree.heading("price", text="Price")
        self.tree.heading("shipping", text="Shipping")
        self.tree.heading("condition", text="Condition")
        self.tree.heading("date", text="Date")
        self.tree.heading("url", text="URL")

        self.tree.column("source", width=70, anchor=CENTER)
        self.tree.column("title", width=300)
        self.tree.column("price", width=80, anchor=E)
        self.tree.column("shipping", width=80, anchor=E)
        self.tree.column("condition", width=80, anchor=CENTER)
        self.tree.column("date", width=90, anchor=CENTER)
        self.tree.column("url", width=0, stretch=False)

        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Double-click to open URL
        self.tree.bind("<Double-1>", self._open_selected_url)

        # Status bar
        self.status_var = ttk.StringVar(value="Ready. Configure eBay API keys in Settings tab for active listing search.")
        ttk.Label(self, textvariable=self.status_var, bootstyle="secondary").pack(fill=X, pady=(5, 0))

    def _search_ebay_active(self):
        query = self.search_var.get().strip()
        if not query:
            return

        client = self._get_ebay_client()
        if not client:
            self.status_var.set("eBay API not configured. Add credentials in Settings tab.")
            Messagebox.show_warning(
                "eBay API credentials not configured.\n\n"
                "Go to Settings tab to enter your Client ID and Client Secret.\n\n"
                "You can still add manual comps or open eBay sold items in your browser.",
                title="API Not Configured",
            )
            return

        self.status_var.set(f"Searching eBay for: {query}...")

        def on_results(items):
            self.after(0, lambda: self._display_active_results(items, query))

        def on_error(error):
            self.after(0, lambda: self.status_var.set(f"Error: {error}"))

        client.search_items_async(
            query, on_results,
            category_id=EbayApiClient.TRADING_CARDS_CATEGORY,
            limit=50, error_callback=on_error,
        )

    def _display_active_results(self, items, query):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in items:
            self.tree.insert("", END, values=(
                "Active",
                item["title"],
                f"${item['price']:.2f}",
                "--",
                item.get("condition", ""),
                "--",
                item.get("item_url", ""),
            ))

        self.status_var.set(f"Found {len(items)} active listings for '{query}'. Double-click to open in browser.")

    def _open_ebay_sold_browser(self):
        query = self.search_var.get().strip()
        if not query:
            return
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.ebay.com/sch/i.html?_nkw={encoded}&LH_Complete=1&LH_Sold=1&_sacat=261328"
        webbrowser.open(url)
        self.status_var.set(f"Opened eBay sold listings for '{query}' in browser.")

    def _show_add_comp_dialog(self):
        dialog = ttk.Toplevel(self)
        dialog.title("Add Manual Comp")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=True)

        query = self.search_var.get().strip()

        ttk.Label(frame, text="Search Query:").pack(anchor=W)
        query_var = ttk.StringVar(value=query)
        ttk.Entry(frame, textvariable=query_var, width=40).pack(fill=X, pady=(0, 5))

        ttk.Label(frame, text="Listing Title:").pack(anchor=W)
        title_var = ttk.StringVar()
        ttk.Entry(frame, textvariable=title_var, width=40).pack(fill=X, pady=(0, 5))

        ttk.Label(frame, text="Sold Price ($):").pack(anchor=W)
        price_var = ttk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=price_var, width=15).pack(anchor=W, pady=(0, 5))

        ttk.Label(frame, text="Shipping Price ($):").pack(anchor=W)
        ship_var = ttk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=ship_var, width=15).pack(anchor=W, pady=(0, 5))

        ttk.Label(frame, text="Condition:").pack(anchor=W)
        cond_var = ttk.StringVar(value="Raw")
        ttk.Combobox(
            frame, textvariable=cond_var,
            values=["Raw", "Graded - PSA", "Graded - BGS", "Graded - SGC", "Graded - CGC", "Other"],
            state="readonly", width=20,
        ).pack(anchor=W, pady=(0, 5))

        ttk.Label(frame, text="Sold Date:").pack(anchor=W)
        date_var = ttk.StringVar(value=date.today().isoformat())
        ttk.Entry(frame, textvariable=date_var, width=15).pack(anchor=W, pady=(0, 10))

        def save():
            try:
                self.comp_service.add_manual_comp(
                    search_query=query_var.get(),
                    title=title_var.get() or "Manual Comp",
                    sold_price=float(price_var.get()),
                    shipping_price=float(ship_var.get()),
                    sold_date=date_var.get(),
                    condition=cond_var.get(),
                )
                self._refresh_stats()
                self._load_saved_comps(query_var.get())
                dialog.destroy()
            except Exception as e:
                Messagebox.show_error(str(e), title="Error")

        ttk.Button(frame, text="Save Comp", bootstyle="success", command=save).pack(fill=X, pady=(5, 0))

    def _refresh_stats(self):
        query = self.search_var.get().strip()
        if not query:
            return

        stats = self.comp_service.get_comp_stats(query)
        if stats["count"] == 0:
            self.stat_count.config(text="Count: 0")
            self.stat_median.config(text="Median: --")
            self.stat_avg.config(text="Average: --")
            self.stat_min.config(text="Min: --")
            self.stat_max.config(text="Max: --")
            return

        self.stat_count.config(text=f"Count: {stats['count']}")
        self.stat_median.config(text=f"Median: ${stats['median']:.2f}")
        self.stat_avg.config(text=f"Average: ${stats['average']:.2f}")
        self.stat_min.config(text=f"Min: ${stats['min']:.2f}")
        self.stat_max.config(text=f"Max: ${stats['max']:.2f}")

        self._load_saved_comps(query)

    def _load_saved_comps(self, query):
        for item in self.tree.get_children():
            self.tree.delete(item)

        comps = self.comp_service.get_comp_stats(query)["comps"]
        for comp in comps:
            self.tree.insert("", END, values=(
                comp.get("source", "manual").title(),
                comp["title"],
                f"${comp['sold_price']:.2f}",
                f"${comp.get('shipping_price', 0):.2f}",
                comp.get("condition", ""),
                comp.get("sold_date", ""),
                comp.get("item_url", ""),
            ))

    def _open_selected_url(self, event):
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], "values")
            if values and len(values) > 6 and values[6]:
                webbrowser.open(values[6])
