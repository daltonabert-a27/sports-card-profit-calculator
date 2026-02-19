"""Deal Analyzer tab - compare offers against cost basis."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from database.repository import ShippingRepository, FeeProfileRepository
from services.deal_analyzer import compare_offers
from services.calculator import calculate_cost_basis
from gui.widgets.currency_entry import CurrencyEntry


class DealAnalyzerTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=15)
        self.conn = conn
        self.settings = settings
        self.shipping_repo = ShippingRepository(conn)
        self.fee_repo = FeeProfileRepository(conn)

        self.shipping_options = self.shipping_repo.get_all_active()
        self.fee_profiles = self.fee_repo.get_all()
        self.offer_rows = []

        self._build_ui()

    def _build_ui(self):
        # Top section: cost basis inputs
        top = ttk.LabelFrame(self, text="  Card Cost Basis  ", padding=15)
        top.pack(fill=X, pady=(0, 10))

        row1 = ttk.Frame(top)
        row1.pack(fill=X, pady=2)

        self.purchase_price = CurrencyEntry(row1, "Purchase Price:")
        self.purchase_price.pack(side=LEFT, padx=(0, 20))

        self.shipping_paid = CurrencyEntry(row1, "Shipping Paid:")
        self.shipping_paid.pack(side=LEFT, padx=(0, 20))

        self.grading_cost = CurrencyEntry(row1, "Grading Cost:")
        self.grading_cost.pack(side=LEFT)

        row2 = ttk.Frame(top)
        row2.pack(fill=X, pady=2)

        tax_frame = ttk.Frame(row2)
        tax_frame.pack(side=LEFT, padx=(0, 20))
        ttk.Label(tax_frame, text="Sales Tax Rate:", width=28, anchor=W).pack(side=LEFT)
        self.tax_rate_var = ttk.DoubleVar(value=6.25)
        ttk.Entry(tax_frame, textvariable=self.tax_rate_var, width=8, justify=RIGHT).pack(side=LEFT)
        ttk.Label(tax_frame, text="%").pack(side=LEFT, padx=2)

        self.tax_included = ttk.BooleanVar(value=False)
        ttk.Checkbutton(
            row2, text="Tax already included",
            variable=self.tax_included, bootstyle="round-toggle",
        ).pack(side=LEFT, padx=(0, 20))

        # Fee profile
        fee_frame = ttk.Frame(row2)
        fee_frame.pack(side=LEFT)
        ttk.Label(fee_frame, text="Fee Profile:").pack(side=LEFT, padx=(0, 5))
        self.fee_profile_var = ttk.StringVar()
        fee_choices = [f["profile_name"] for f in self.fee_profiles]
        if fee_choices:
            default = next((f["profile_name"] for f in self.fee_profiles if f["is_default"]), fee_choices[0])
            self.fee_profile_var.set(default)
        ttk.Combobox(
            fee_frame, textvariable=self.fee_profile_var,
            values=fee_choices, state="readonly", width=25,
        ).pack(side=LEFT)

        # Middle: offers section
        offers_frame = ttk.LabelFrame(self, text="  Offers to Compare  ", padding=15)
        offers_frame.pack(fill=X, pady=(0, 10))

        # Offer header
        header = ttk.Frame(offers_frame)
        header.pack(fill=X, pady=(0, 5))
        ttk.Label(header, text="Offer Price", width=15, font=("-weight", "bold")).pack(side=LEFT, padx=5)
        ttk.Label(header, text="Shipping Method", width=30, font=("-weight", "bold")).pack(side=LEFT, padx=5)
        ttk.Label(header, text="Ship Charged", width=12, font=("-weight", "bold")).pack(side=LEFT, padx=5)
        ttk.Label(header, text="Intl?", width=6, font=("-weight", "bold")).pack(side=LEFT, padx=5)
        ttk.Label(header, text="", width=8).pack(side=LEFT, padx=5)

        self.offers_container = ttk.Frame(offers_frame)
        self.offers_container.pack(fill=X)

        # Add initial offer row
        self._add_offer_row()

        btn_frame = ttk.Frame(offers_frame)
        btn_frame.pack(fill=X, pady=(10, 0))
        ttk.Button(
            btn_frame, text="+ Add Offer", bootstyle="info-outline",
            command=self._add_offer_row,
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            btn_frame, text="Analyze Offers", bootstyle="success",
            command=self._analyze, padding=(20, 8),
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            btn_frame, text="Clear All", bootstyle="secondary-outline",
            command=self._clear,
        ).pack(side=LEFT)

        # Bottom: results table
        self.results_frame = ttk.LabelFrame(self, text="  Analysis Results  ", padding=15)
        self.results_frame.pack(fill=BOTH, expand=True)

        self.results_tree = ttk.Treeview(
            self.results_frame,
            columns=("offer", "fees", "ship_cost", "net_proceeds", "net_profit", "margin", "roi", "verdict"),
            show="headings",
            height=8,
        )
        self.results_tree.heading("offer", text="Offer Price")
        self.results_tree.heading("fees", text="Total Fees")
        self.results_tree.heading("ship_cost", text="Ship Cost")
        self.results_tree.heading("net_proceeds", text="Net Proceeds")
        self.results_tree.heading("net_profit", text="Net Profit")
        self.results_tree.heading("margin", text="Margin %")
        self.results_tree.heading("roi", text="ROI %")
        self.results_tree.heading("verdict", text="Verdict")

        for col in ("offer", "fees", "ship_cost", "net_proceeds", "net_profit", "margin", "roi"):
            self.results_tree.column(col, width=100, anchor=CENTER)
        self.results_tree.column("verdict", width=80, anchor=CENTER)

        scrollbar = ttk.Scrollbar(self.results_frame, orient=VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _add_offer_row(self):
        row_frame = ttk.Frame(self.offers_container)
        row_frame.pack(fill=X, pady=2)

        # Offer price
        price_var = ttk.DoubleVar(value=0.0)
        price_frame = ttk.Frame(row_frame, width=120)
        price_frame.pack(side=LEFT, padx=5)
        ttk.Label(price_frame, text="$").pack(side=LEFT)
        ttk.Entry(price_frame, textvariable=price_var, width=10, justify=RIGHT).pack(side=LEFT)

        # Shipping method
        ship_var = ttk.StringVar()
        ship_choices = [f"{s['method_name']} (${s['cost']:.2f})" for s in self.shipping_options]
        if ship_choices:
            ship_var.set(ship_choices[0])
        ship_combo = ttk.Combobox(
            row_frame, textvariable=ship_var,
            values=ship_choices, state="readonly", width=28,
        )
        ship_combo.pack(side=LEFT, padx=5)

        # Shipping charged to buyer
        charge_var = ttk.DoubleVar(value=0.0)
        charge_frame = ttk.Frame(row_frame)
        charge_frame.pack(side=LEFT, padx=5)
        ttk.Label(charge_frame, text="$").pack(side=LEFT)
        ttk.Entry(charge_frame, textvariable=charge_var, width=8, justify=RIGHT).pack(side=LEFT)

        # International toggle
        intl_var = ttk.BooleanVar(value=False)
        ttk.Checkbutton(row_frame, variable=intl_var, bootstyle="round-toggle").pack(side=LEFT, padx=5)

        # Remove button
        remove_btn = ttk.Button(
            row_frame, text="X", bootstyle="danger-outline", width=3,
            command=lambda: self._remove_offer_row(row_frame, row_data),
        )
        remove_btn.pack(side=LEFT, padx=5)

        row_data = {
            "frame": row_frame,
            "price_var": price_var,
            "ship_combo": ship_combo,
            "charge_var": charge_var,
            "intl_var": intl_var,
        }
        self.offer_rows.append(row_data)

    def _remove_offer_row(self, frame, row_data):
        if len(self.offer_rows) <= 1:
            return
        frame.destroy()
        self.offer_rows.remove(row_data)

    def _get_fee_profile(self) -> dict:
        name = self.fee_profile_var.get()
        for fp in self.fee_profiles:
            if fp["profile_name"] == name:
                return fp
        return self.fee_profiles[0] if self.fee_profiles else {}

    def _analyze(self):
        # Calculate cost basis
        cb = calculate_cost_basis(
            purchase_price=self.purchase_price.get(),
            sales_tax_rate=self.tax_rate_var.get() / 100.0,
            tax_already_included=self.tax_included.get(),
            shipping_to_you=self.shipping_paid.get(),
            grading_cost=self.grading_cost.get(),
        )
        cost_basis = cb["total_cost_basis"]

        fp = self._get_fee_profile()

        # Build offers list
        offers = []
        for row in self.offer_rows:
            try:
                price = float(row["price_var"].get())
            except (ValueError, ttk.TclError):
                price = 0.0

            ship_idx = row["ship_combo"].current()
            ship_cost = self.shipping_options[ship_idx]["cost"] if 0 <= ship_idx < len(self.shipping_options) else 0.0

            try:
                ship_charged = float(row["charge_var"].get())
            except (ValueError, ttk.TclError):
                ship_charged = 0.0

            offers.append({
                "price": price,
                "shipping_cost": ship_cost,
                "shipping_charged": ship_charged,
                "is_international": row["intl_var"].get(),
                "label": f"${price:.2f}",
            })

        if not offers:
            return

        results = compare_offers(
            offers=offers,
            cost_basis=cost_basis,
            fvf_rate=fp.get("fvf_rate", 0.1325),
            fvf_cap=fp.get("fvf_cap_amount", 7500.0),
            fvf_rate_above_cap=fp.get("fvf_rate_above_cap", 0.0235),
            per_order_threshold=fp.get("per_order_threshold", 10.0),
            per_order_fee_low=fp.get("per_order_fee_low", 0.30),
            per_order_fee_high=fp.get("per_order_fee_high", 0.40),
            intl_fee_rate=fp.get("intl_fee_rate", 0.0165),
        )

        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Populate results
        for i, r in enumerate(results):
            verdict_text = r["recommendation"]
            tag = "profit" if r["net_profit"] > 0 else "loss"

            self.results_tree.insert("", END, values=(
                f"${r['offer_price']:.2f}",
                f"${r['total_fees']:.2f}",
                f"${r['shipping_cost']:.2f}",
                f"${r['net_proceeds']:.2f}",
                f"${r['net_profit']:.2f}",
                f"{r['profit_margin_pct']:.1f}%",
                f"{r['roi_pct']:.1f}%",
                verdict_text,
            ), tags=(tag,))

        self.results_tree.tag_configure("profit", foreground="#00bc8c")
        self.results_tree.tag_configure("loss", foreground="#e74c3c")

    def _clear(self):
        self.purchase_price.set(0.0)
        self.shipping_paid.set(0.0)
        self.grading_cost.set(0.0)
        self.tax_rate_var.set(6.25)
        self.tax_included.set(False)

        # Remove all offer rows except first
        while len(self.offer_rows) > 1:
            row = self.offer_rows[-1]
            row["frame"].destroy()
            self.offer_rows.pop()

        # Reset first row
        if self.offer_rows:
            row = self.offer_rows[0]
            row["price_var"].set(0.0)
            row["charge_var"].set(0.0)
            row["intl_var"].set(False)
            if row["ship_combo"]["values"]:
                row["ship_combo"].current(0)

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
