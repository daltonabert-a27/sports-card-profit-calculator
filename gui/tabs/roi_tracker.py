"""ROI Tracker tab - log purchases/sales, view inventory, portfolio summary."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import date

from database.repository import (
    CardRepository, PurchaseRepository, SaleRepository,
    ShippingRepository, FeeProfileRepository, GradingRepository,
)
from services.roi_tracker import ROITracker
from services.calculator import calculate_profit, get_per_order_fee

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ROITrackerTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=10)
        self.conn = conn
        self.settings = settings
        self.tracker = ROITracker(conn)
        self.cards_repo = CardRepository(conn)
        self.purchases_repo = PurchaseRepository(conn)
        self.sales_repo = SaleRepository(conn)
        self.shipping_repo = ShippingRepository(conn)
        self.fee_repo = FeeProfileRepository(conn)
        self.grading_repo = GradingRepository(conn)

        self._build_ui()
        self._refresh_all()

    # ── UI Construction ─────────────────────────────────────────────

    def _build_ui(self):
        # Top: Summary cards row
        self._build_summary_panel()

        # Middle: Buttons + filter row
        self._build_action_bar()

        # Main area: paned window with inventory table (left) and chart (right)
        paned = ttk.Panedwindow(self, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True, pady=(5, 0))

        self._build_inventory_table(paned)
        self._build_chart_panel(paned)

    def _build_summary_panel(self):
        frame = ttk.Labelframe(self, text="Portfolio Summary", padding=10)
        frame.pack(fill=X, pady=(0, 5))

        self.summary_vars = {}
        labels = [
            ("total_invested", "Total Invested"),
            ("total_revenue", "Total Revenue"),
            ("total_profit", "Total Profit"),
            ("overall_roi_pct", "Overall ROI"),
            ("cards_purchased", "Purchased"),
            ("cards_sold", "Sold"),
            ("cards_in_inventory", "In Inventory"),
            ("avg_profit_per_card", "Avg Profit/Card"),
        ]

        for i, (key, text) in enumerate(labels):
            col_frame = ttk.Frame(frame)
            col_frame.grid(row=0, column=i, padx=8, sticky="n")
            ttk.Label(col_frame, text=text, font=("-size", 9), bootstyle="secondary").pack()
            var = ttk.StringVar(value="--")
            self.summary_vars[key] = var
            style = "success" if key == "total_profit" else "primary"
            ttk.Label(col_frame, textvariable=var, font=("-size", 13, "-weight", "bold"),
                      bootstyle=style).pack()

        frame.columnconfigure(list(range(len(labels))), weight=1)

    def _build_action_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill=X, pady=5)

        ttk.Button(bar, text="+ Log Purchase", bootstyle="success",
                   command=self._open_purchase_dialog).pack(side=LEFT, padx=(0, 5))
        ttk.Button(bar, text="+ Log Sale", bootstyle="info",
                   command=self._open_sale_dialog).pack(side=LEFT, padx=(0, 5))
        ttk.Button(bar, text="Refresh", bootstyle="secondary-outline",
                   command=self._refresh_all).pack(side=LEFT, padx=(0, 15))

        # Status filter
        ttk.Label(bar, text="Filter:").pack(side=LEFT, padx=(10, 5))
        self.filter_var = ttk.StringVar(value="All")
        filter_combo = ttk.Combobox(bar, textvariable=self.filter_var, width=14,
                                     values=["All", "Inventory", "Sold", "At Grading"],
                                     state="readonly")
        filter_combo.pack(side=LEFT)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_inventory())

    def _build_inventory_table(self, paned):
        table_frame = ttk.Frame(paned)
        paned.add(table_frame, weight=3)

        cols = ("card_id", "description", "status", "cost_basis", "sale_price",
                "net_proceeds", "profit", "roi")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        headers = {
            "card_id": ("Card ID", 90),
            "description": ("Description", 180),
            "status": ("Status", 80),
            "cost_basis": ("Cost Basis", 85),
            "sale_price": ("Sale Price", 80),
            "net_proceeds": ("Net Proceeds", 90),
            "profit": ("Profit", 80),
            "roi": ("ROI %", 70),
        }
        for col, (heading, width) in headers.items():
            self.tree.heading(col, text=heading)
            anchor = W if col == "description" else CENTER
            self.tree.column(col, width=width, anchor=anchor, minwidth=50)

        scroll = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)

        # Tag styles for profit/loss rows
        self.tree.tag_configure("profit", foreground="#00bc8c")
        self.tree.tag_configure("loss", foreground="#e74c3c")
        self.tree.tag_configure("unsold", foreground="#adb5bd")

    def _build_chart_panel(self, paned):
        chart_frame = ttk.Labelframe(paned, text="Profit / Loss by Card", padding=5)
        paned.add(chart_frame, weight=2)

        self.fig = Figure(figsize=(4, 3), dpi=90, facecolor="#222222")
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    # ── Data Refresh ────────────────────────────────────────────────

    def _refresh_all(self):
        self._refresh_summary()
        self._refresh_inventory()
        self._refresh_chart()

    def _refresh_summary(self):
        summary = self.tracker.get_portfolio_summary()
        money_keys = ("total_invested", "total_revenue", "total_profit", "avg_profit_per_card")
        for key, var in self.summary_vars.items():
            val = summary.get(key, 0)
            if key in money_keys:
                var.set(f"${val:,.2f}")
            elif key == "overall_roi_pct":
                var.set(f"{val:,.1f}%")
            else:
                var.set(str(val))

        # Color the profit label
        profit = summary.get("total_profit", 0)
        style = "success" if profit >= 0 else "danger"
        for widget in self.summary_vars["total_profit"].trace_info():
            pass  # bootstyle set at build time; dynamic update below
        # Find the profit label widget and update its bootstyle
        summary_frame = self.winfo_children()[0]  # The Labelframe
        for col_frame in summary_frame.winfo_children():
            labels = col_frame.winfo_children()
            if len(labels) >= 2:
                header_text = labels[0].cget("text")
                if header_text == "Total Profit":
                    labels[1].configure(bootstyle=style)
                    break

    def _refresh_inventory(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.tracker.get_inventory_with_details()
        status_filter = self.filter_var.get()

        for row in rows:
            status = row.get("status", "Inventory")
            if status_filter != "All" and status != status_filter:
                continue

            cost_basis = row.get("total_cost_basis") or 0
            sale_price = row.get("sale_price")
            net_proceeds = row.get("net_proceeds")

            if net_proceeds is not None and cost_basis > 0:
                profit = net_proceeds - cost_basis
                roi = profit / cost_basis * 100
                tag = "profit" if profit >= 0 else "loss"
            else:
                profit = None
                roi = None
                tag = "unsold"

            values = (
                row.get("card_id", ""),
                row.get("description", ""),
                status,
                f"${cost_basis:,.2f}" if cost_basis else "--",
                f"${sale_price:,.2f}" if sale_price is not None else "--",
                f"${net_proceeds:,.2f}" if net_proceeds is not None else "--",
                f"${profit:,.2f}" if profit is not None else "--",
                f"{roi:,.1f}%" if roi is not None else "--",
            )
            self.tree.insert("", END, values=values, tags=(tag,))

    def _refresh_chart(self):
        self.ax.clear()
        rows = self.tracker.get_inventory_with_details()

        # Only cards that have been sold
        sold = [r for r in rows if r.get("net_proceeds") is not None and r.get("total_cost_basis")]
        if not sold:
            self.ax.set_facecolor("#222222")
            self.ax.text(0.5, 0.5, "No sold cards yet", ha="center", va="center",
                         color="#adb5bd", fontsize=11, transform=self.ax.transAxes)
            self.canvas.draw()
            return

        # Limit to most recent 15 for readability
        sold = sold[:15]
        labels = [r.get("card_id", "?")[-6:] for r in sold]
        profits = [round((r["net_proceeds"] or 0) - (r["total_cost_basis"] or 0), 2) for r in sold]
        colors = ["#00bc8c" if p >= 0 else "#e74c3c" for p in profits]

        self.ax.barh(labels, profits, color=colors)
        self.ax.set_facecolor("#222222")
        self.ax.tick_params(colors="#adb5bd", labelsize=8)
        self.ax.set_xlabel("Profit ($)", color="#adb5bd", fontsize=9)
        self.ax.axvline(0, color="#555555", linewidth=0.8)
        for spine in self.ax.spines.values():
            spine.set_color("#444444")
        self.fig.tight_layout()
        self.canvas.draw()

    # ── Log Purchase Dialog ─────────────────────────────────────────

    def _open_purchase_dialog(self):
        dlg = ttk.Toplevel(self)
        dlg.title("Log Purchase")
        dlg.geometry("480x580")
        dlg.resizable(False, False)
        dlg.grab_set()

        container = ttk.Frame(dlg, padding=15)
        container.pack(fill=BOTH, expand=True)

        ttk.Label(container, text="Log New Purchase", font=("-size", 14, "-weight", "bold")).pack(
            anchor=W, pady=(0, 10))

        fields = {}

        def add_field(label, default="", width=35):
            f = ttk.Frame(container)
            f.pack(fill=X, pady=3)
            ttk.Label(f, text=label, width=18, anchor=W).pack(side=LEFT)
            entry = ttk.Entry(f, width=width)
            entry.insert(0, default)
            entry.pack(side=LEFT, fill=X, expand=True)
            fields[label] = entry
            return entry

        add_field("Description *")
        add_field("Player Name")
        add_field("Year")
        add_field("Set Name")
        add_field("Card Number")

        # Sport dropdown
        sport_frame = ttk.Frame(container)
        sport_frame.pack(fill=X, pady=3)
        ttk.Label(sport_frame, text="Sport", width=18, anchor=W).pack(side=LEFT)
        sport_var = ttk.StringVar(value="Basketball")
        ttk.Combobox(sport_frame, textvariable=sport_var, width=33,
                     values=["Basketball", "Baseball", "Football", "Hockey", "Soccer", "Other"],
                     state="readonly").pack(side=LEFT)

        # Graded checkbox + fields
        graded_var = ttk.BooleanVar(value=False)
        graded_frame = ttk.Frame(container)
        graded_frame.pack(fill=X, pady=3)
        ttk.Checkbutton(graded_frame, text="Graded?", variable=graded_var,
                        bootstyle="round-toggle").pack(side=LEFT, padx=(0, 10))

        grading_company_var = ttk.StringVar()
        grade_var = ttk.StringVar()
        ttk.Label(graded_frame, text="Company:").pack(side=LEFT)
        ttk.Combobox(graded_frame, textvariable=grading_company_var, width=8,
                     values=self.grading_repo.get_companies(), state="readonly").pack(side=LEFT, padx=(0, 5))
        ttk.Label(graded_frame, text="Grade:").pack(side=LEFT)
        ttk.Entry(graded_frame, textvariable=grade_var, width=6).pack(side=LEFT)

        ttk.Separator(container).pack(fill=X, pady=8)

        add_field("Purchase Price *", "0.00")
        add_field("Sales Tax Paid", "0.00")
        add_field("Shipping Paid", "0.00")
        add_field("Grading Cost", "0.00")
        add_field("Purchase Date", date.today().isoformat())

        # Source dropdown
        source_frame = ttk.Frame(container)
        source_frame.pack(fill=X, pady=3)
        ttk.Label(source_frame, text="Source", width=18, anchor=W).pack(side=LEFT)
        source_var = ttk.StringVar(value="eBay")
        ttk.Combobox(source_frame, textvariable=source_var, width=33,
                     values=["eBay", "Card Show", "LCS", "Facebook", "COMC", "Other"],
                     state="readonly").pack(side=LEFT)

        add_field("Notes", "")

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(12, 0))
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary",
                   command=dlg.destroy).pack(side=RIGHT, padx=(5, 0))

        def save_purchase():
            desc = fields["Description *"].get().strip()
            if not desc:
                Messagebox.show_error("Description is required.", "Validation Error", parent=dlg)
                return
            try:
                price = float(fields["Purchase Price *"].get())
            except ValueError:
                Messagebox.show_error("Invalid purchase price.", "Validation Error", parent=dlg)
                return

            card_data = {
                "description": desc,
                "player_name": fields["Player Name"].get().strip() or None,
                "year": int(fields["Year"].get()) if fields["Year"].get().strip().isdigit() else None,
                "set_name": fields["Set Name"].get().strip() or None,
                "card_number": fields["Card Number"].get().strip() or None,
                "sport": sport_var.get(),
                "is_graded": graded_var.get(),
                "grading_company": grading_company_var.get() or None if graded_var.get() else None,
                "grade": grade_var.get().strip() or None if graded_var.get() else None,
                "status": "Inventory",
            }
            card_id = self.cards_repo.add(card_data)

            purchase_data = {
                "card_id": card_id,
                "purchase_date": fields["Purchase Date"].get().strip(),
                "purchase_price": price,
                "sales_tax_paid": float(fields["Sales Tax Paid"].get() or 0),
                "shipping_paid": float(fields["Shipping Paid"].get() or 0),
                "grading_cost": float(fields["Grading Cost"].get() or 0),
                "source": source_var.get(),
                "notes": fields["Notes"].get().strip() or None,
            }
            self.purchases_repo.add(purchase_data)

            dlg.destroy()
            self._refresh_all()

        ttk.Button(btn_frame, text="Save Purchase", bootstyle="success",
                   command=save_purchase).pack(side=RIGHT)

    # ── Log Sale Dialog ─────────────────────────────────────────────

    def _open_sale_dialog(self):
        # Get inventory cards to sell
        inventory_cards = self.cards_repo.get_all(status="Inventory")
        if not inventory_cards:
            Messagebox.show_info("No cards in inventory to sell.", "No Inventory", parent=self)
            return

        dlg = ttk.Toplevel(self)
        dlg.title("Log Sale")
        dlg.geometry("480x520")
        dlg.resizable(False, False)
        dlg.grab_set()

        container = ttk.Frame(dlg, padding=15)
        container.pack(fill=BOTH, expand=True)

        ttk.Label(container, text="Log Sale", font=("-size", 14, "-weight", "bold")).pack(
            anchor=W, pady=(0, 10))

        # Card selector
        card_frame = ttk.Frame(container)
        card_frame.pack(fill=X, pady=3)
        ttk.Label(card_frame, text="Select Card *", width=18, anchor=W).pack(side=LEFT)
        card_map = {f"{c['card_id']} - {c['description'][:40]}": c['card_id'] for c in inventory_cards}
        card_var = ttk.StringVar()
        ttk.Combobox(card_frame, textvariable=card_var, width=33,
                     values=list(card_map.keys()), state="readonly").pack(side=LEFT, fill=X, expand=True)

        fields = {}

        def add_field(label, default="", width=35):
            f = ttk.Frame(container)
            f.pack(fill=X, pady=3)
            ttk.Label(f, text=label, width=18, anchor=W).pack(side=LEFT)
            entry = ttk.Entry(f, width=width)
            entry.insert(0, default)
            entry.pack(side=LEFT, fill=X, expand=True)
            fields[label] = entry
            return entry

        add_field("Sale Price *", "0.00")
        add_field("Shipping Charged", "0.00")

        # Shipping method dropdown
        shipping_opts = self.shipping_repo.get_all_active()
        ship_frame = ttk.Frame(container)
        ship_frame.pack(fill=X, pady=3)
        ttk.Label(ship_frame, text="Shipping Method", width=18, anchor=W).pack(side=LEFT)
        ship_map = {s["method_name"]: s["cost"] for s in shipping_opts}
        ship_var = ttk.StringVar()
        ttk.Combobox(ship_frame, textvariable=ship_var, width=33,
                     values=list(ship_map.keys()), state="readonly").pack(side=LEFT, fill=X, expand=True)

        add_field("Shipping Cost", "0.00")

        # Auto-fill shipping cost when method selected
        def on_ship_select(e):
            method = ship_var.get()
            if method in ship_map:
                fields["Shipping Cost"].delete(0, "end")
                fields["Shipping Cost"].insert(0, f"{ship_map[method]:.2f}")
        ship_frame.winfo_children()[-1].bind("<<ComboboxSelected>>", on_ship_select)

        # Fee profile
        fee_profiles = self.fee_repo.get_all()
        fee_frame = ttk.Frame(container)
        fee_frame.pack(fill=X, pady=3)
        ttk.Label(fee_frame, text="Fee Profile", width=18, anchor=W).pack(side=LEFT)
        fee_map = {fp["profile_name"]: fp for fp in fee_profiles}
        fee_var = ttk.StringVar()
        default_fp = self.fee_repo.get_default()
        if default_fp:
            fee_var.set(default_fp["profile_name"])
        ttk.Combobox(fee_frame, textvariable=fee_var, width=33,
                     values=list(fee_map.keys()), state="readonly").pack(side=LEFT, fill=X, expand=True)

        # International toggle
        intl_var = ttk.BooleanVar(value=False)
        ttk.Checkbutton(container, text="International sale (+1.65%)", variable=intl_var,
                        bootstyle="round-toggle").pack(anchor=W, pady=3)

        add_field("Sale Date", date.today().isoformat())

        # Platform
        platform_frame = ttk.Frame(container)
        platform_frame.pack(fill=X, pady=3)
        ttk.Label(platform_frame, text="Platform", width=18, anchor=W).pack(side=LEFT)
        platform_var = ttk.StringVar(value="eBay")
        ttk.Combobox(platform_frame, textvariable=platform_var, width=33,
                     values=["eBay", "Facebook Marketplace", "COMC", "Card Show", "Other"],
                     state="readonly").pack(side=LEFT)

        add_field("Notes", "")

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(12, 0))
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary",
                   command=dlg.destroy).pack(side=RIGHT, padx=(5, 0))

        def save_sale():
            card_selection = card_var.get()
            if not card_selection or card_selection not in card_map:
                Messagebox.show_error("Please select a card.", "Validation Error", parent=dlg)
                return
            card_id = card_map[card_selection]

            try:
                sale_price = float(fields["Sale Price *"].get())
            except ValueError:
                Messagebox.show_error("Invalid sale price.", "Validation Error", parent=dlg)
                return

            shipping_charged = float(fields["Shipping Charged"].get() or 0)
            shipping_cost = float(fields["Shipping Cost"].get() or 0)

            # Get fee profile
            fp = fee_map.get(fee_var.get()) or default_fp or {}
            fvf_rate = fp.get("fvf_rate", 0.1325)
            intl_fee_rate = fp.get("intl_fee_rate", 0.0165)

            # Calculate fees using the calculator engine
            result = calculate_profit(
                sale_price=sale_price,
                shipping_charged=shipping_charged,
                cost_basis=0,  # we just need fees, not profit here
                shipping_cost=shipping_cost,
                fvf_rate=fvf_rate,
                fvf_cap=fp.get("fvf_cap_amount", 7500.0),
                fvf_rate_above_cap=fp.get("fvf_rate_above_cap", 0.0235),
                per_order_fee_low=fp.get("per_order_fee_low", 0.30),
                per_order_fee_high=fp.get("per_order_fee_high", 0.40),
                per_order_threshold=fp.get("per_order_threshold", 10.0),
                is_international=intl_var.get(),
                intl_fee_rate=intl_fee_rate,
            )

            sale_data = {
                "card_id": card_id,
                "sale_date": fields["Sale Date"].get().strip(),
                "sale_price": sale_price,
                "shipping_charged": shipping_charged,
                "shipping_cost": shipping_cost,
                "shipping_method": ship_var.get() or None,
                "ebay_fvf_rate": fvf_rate,
                "ebay_fvf_amount": result["fvf_amount"],
                "ebay_per_order_fee": result["per_order_fee"],
                "ebay_intl_fee_rate": intl_fee_rate if intl_var.get() else 0.0,
                "ebay_intl_fee_amount": result["intl_fee"],
                "total_fees": result["total_fees"],
                "net_proceeds": result["net_proceeds"],
                "platform": platform_var.get(),
                "notes": fields["Notes"].get().strip() or None,
            }
            self.sales_repo.add(sale_data)
            self.cards_repo.update_status(card_id, "Sold")

            dlg.destroy()
            self._refresh_all()

        ttk.Button(btn_frame, text="Save Sale", bootstyle="info",
                   command=save_sale).pack(side=RIGHT)
