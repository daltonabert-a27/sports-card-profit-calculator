"""Profit Calculator tab - full implementation."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from database.repository import GradingRepository, ShippingRepository, FeeProfileRepository
from services.calculator import calculate_cost_basis, calculate_profit
from gui.widgets.currency_entry import CurrencyEntry
from gui.widgets.result_card import ResultCard


class ProfitCalculatorTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=15)
        self.conn = conn
        self.settings = settings
        self.grading_repo = GradingRepository(conn)
        self.shipping_repo = ShippingRepository(conn)
        self.fee_repo = FeeProfileRepository(conn)

        self._load_data()
        self._build_ui()

    def _load_data(self):
        self.shipping_options = self.shipping_repo.get_all_active()
        self.grading_services = self.grading_repo.get_all_active()
        self.grading_companies = self.grading_repo.get_companies()
        self.fee_profiles = self.fee_repo.get_all()

    def _build_ui(self):
        # Main split: left=inputs, right=results
        paned = ttk.Frame(self)
        paned.pack(fill=BOTH, expand=True)

        left = ttk.Labelframe(paned, text="  Inputs  ", padding=15)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))

        right = ttk.Labelframe(paned, text="  Results  ", padding=15)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        self._build_inputs(left)
        self._build_results(right)

    def _build_inputs(self, parent):
        # --- Cost Basis Section ---
        ttk.Label(parent, text="Cost Basis", font=("-size", 12, "-weight", "bold")).pack(anchor=W, pady=(0, 5))

        self.purchase_price = CurrencyEntry(parent, "Purchase Price:")
        self.purchase_price.pack(fill=X, pady=2)

        # Sales tax
        tax_frame = ttk.Frame(parent)
        tax_frame.pack(fill=X, pady=2)
        self.tax_included = ttk.BooleanVar(value=False)
        ttk.Label(tax_frame, text="Sales Tax:", width=28, anchor=W).pack(side=LEFT, padx=(0, 5))
        ttk.Checkbutton(
            tax_frame, text="Tax already included in price",
            variable=self.tax_included, bootstyle="round-toggle",
        ).pack(side=LEFT)

        tax_rate_frame = ttk.Frame(parent)
        tax_rate_frame.pack(fill=X, pady=2)
        ttk.Label(tax_rate_frame, text="Sales Tax Rate:", width=28, anchor=W).pack(side=LEFT, padx=(0, 5))
        self.tax_rate_var = ttk.DoubleVar(value=6.25)
        ttk.Entry(tax_rate_frame, textvariable=self.tax_rate_var, width=8, justify=RIGHT).pack(side=LEFT)
        ttk.Label(tax_rate_frame, text="% (IL default 6.25%)").pack(side=LEFT, padx=5)

        self.shipping_to_you = CurrencyEntry(parent, "Shipping Paid (to you):")
        self.shipping_to_you.pack(fill=X, pady=2)

        # Grading
        grade_frame = ttk.Frame(parent)
        grade_frame.pack(fill=X, pady=2)
        ttk.Label(grade_frame, text="Grading:", width=28, anchor=W).pack(side=LEFT, padx=(0, 5))
        self.grading_var = ttk.StringVar(value="None (Raw)")
        grading_choices = ["None (Raw)"] + [
            f"{g['company']} - {g['tier_name']} (${g['cost_per_card']:.2f})"
            for g in self.grading_services
        ]
        self.grading_combo = ttk.Combobox(
            grade_frame, textvariable=self.grading_var,
            values=grading_choices, state="readonly", width=30,
        )
        self.grading_combo.pack(side=LEFT)

        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=10)

        # --- Sale Section ---
        ttk.Label(parent, text="Sale Details", font=("-size", 12, "-weight", "bold")).pack(anchor=W, pady=(0, 5))

        self.sale_price = CurrencyEntry(parent, "Expected Sale Price:")
        self.sale_price.pack(fill=X, pady=2)

        # Shipping method
        ship_frame = ttk.Frame(parent)
        ship_frame.pack(fill=X, pady=2)
        ttk.Label(ship_frame, text="Shipping Method:", width=28, anchor=W).pack(side=LEFT, padx=(0, 5))
        self.shipping_method_var = ttk.StringVar()
        shipping_choices = [
            f"{s['method_name']} (${s['cost']:.2f})" for s in self.shipping_options
        ]
        if shipping_choices:
            self.shipping_method_var.set(shipping_choices[0])
        self.shipping_combo = ttk.Combobox(
            ship_frame, textvariable=self.shipping_method_var,
            values=shipping_choices, state="readonly", width=38,
        )
        self.shipping_combo.pack(side=LEFT)

        # Free shipping toggle
        free_ship_frame = ttk.Frame(parent)
        free_ship_frame.pack(fill=X, pady=2)
        self.free_shipping = ttk.BooleanVar(value=False)
        ttk.Label(free_ship_frame, text="", width=28).pack(side=LEFT, padx=(0, 5))
        ttk.Checkbutton(
            free_ship_frame, text="Free shipping (seller pays shipping)",
            variable=self.free_shipping, bootstyle="round-toggle",
        ).pack(side=LEFT)

        # Shipping charged to buyer
        self.shipping_charged = CurrencyEntry(parent, "Shipping Charged to Buyer:")
        self.shipping_charged.pack(fill=X, pady=2)

        # Fee profile
        fee_frame = ttk.Frame(parent)
        fee_frame.pack(fill=X, pady=2)
        ttk.Label(fee_frame, text="Fee Profile:", width=28, anchor=W).pack(side=LEFT, padx=(0, 5))
        self.fee_profile_var = ttk.StringVar()
        fee_choices = [f["profile_name"] for f in self.fee_profiles]
        if fee_choices:
            default = next((f["profile_name"] for f in self.fee_profiles if f["is_default"]), fee_choices[0])
            self.fee_profile_var.set(default)
        self.fee_combo = ttk.Combobox(
            fee_frame, textvariable=self.fee_profile_var,
            values=fee_choices, state="readonly", width=30,
        )
        self.fee_combo.pack(side=LEFT)

        # International
        intl_frame = ttk.Frame(parent)
        intl_frame.pack(fill=X, pady=2)
        self.is_international = ttk.BooleanVar(value=False)
        ttk.Label(intl_frame, text="", width=28).pack(side=LEFT, padx=(0, 5))
        ttk.Checkbutton(
            intl_frame, text="International sale (+1.65%)",
            variable=self.is_international, bootstyle="round-toggle",
        ).pack(side=LEFT)

        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=10)

        # Calculate button
        ttk.Button(
            parent, text="Calculate Profit", bootstyle="success",
            command=self._calculate, padding=(20, 10),
        ).pack(fill=X, pady=5)

        # Clear button
        ttk.Button(
            parent, text="Clear", bootstyle="secondary-outline",
            command=self._clear,
        ).pack(fill=X, pady=2)

    def _build_results(self, parent):
        # Scrollable results
        canvas = ttk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        container = scroll_frame

        # Cost basis results
        ttk.Label(container, text="Cost Breakdown", font=("-size", 12, "-weight", "bold")).pack(anchor=W, pady=(0, 5))

        self.res_purchase = ResultCard(container, "Purchase Price")
        self.res_purchase.pack(fill=X, pady=2)

        self.res_tax = ResultCard(container, "Sales Tax")
        self.res_tax.pack(fill=X, pady=2)

        self.res_grading = ResultCard(container, "Grading Cost")
        self.res_grading.pack(fill=X, pady=2)

        self.res_cost_basis = ResultCard(container, "Total Cost Basis", bootstyle="info", font_size=16)
        self.res_cost_basis.pack(fill=X, pady=2)

        ttk.Separator(container, orient=HORIZONTAL).pack(fill=X, pady=8)

        # Fee breakdown
        ttk.Label(container, text="Fee Breakdown", font=("-size", 12, "-weight", "bold")).pack(anchor=W, pady=(0, 5))

        self.res_fvf = ResultCard(container, "eBay FVF (13.25%)")
        self.res_fvf.pack(fill=X, pady=2)

        self.res_per_order = ResultCard(container, "Per-Order Fee")
        self.res_per_order.pack(fill=X, pady=2)

        self.res_intl = ResultCard(container, "International Fee")
        self.res_intl.pack(fill=X, pady=2)

        self.res_total_fees = ResultCard(container, "Total Fees", bootstyle="warning")
        self.res_total_fees.pack(fill=X, pady=2)

        self.res_shipping = ResultCard(container, "Shipping Cost (Your Cost)")
        self.res_shipping.pack(fill=X, pady=2)

        ttk.Separator(container, orient=HORIZONTAL).pack(fill=X, pady=8)

        # Profit results
        ttk.Label(container, text="Profit Summary", font=("-size", 12, "-weight", "bold")).pack(anchor=W, pady=(0, 5))

        self.res_net_proceeds = ResultCard(container, "Net Proceeds (after fees & shipping)")
        self.res_net_proceeds.pack(fill=X, pady=2)

        self.res_net_profit = ResultCard(container, "Net Profit", font_size=18)
        self.res_net_profit.pack(fill=X, pady=2)

        # Margin and ROI side by side
        metrics_frame = ttk.Frame(container)
        metrics_frame.pack(fill=X, pady=2)

        self.res_margin = ResultCard(metrics_frame, "Profit Margin", font_size=16)
        self.res_margin.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        self.res_roi = ResultCard(metrics_frame, "ROI", font_size=16)
        self.res_roi.pack(side=RIGHT, fill=X, expand=True, padx=(5, 0))

    def _get_selected_fee_profile(self) -> dict:
        name = self.fee_profile_var.get()
        for fp in self.fee_profiles:
            if fp["profile_name"] == name:
                return fp
        return self.fee_profiles[0] if self.fee_profiles else {}

    def _get_shipping_cost(self) -> float:
        idx = self.shipping_combo.current()
        if 0 <= idx < len(self.shipping_options):
            return self.shipping_options[idx]["cost"]
        return 0.0

    def _get_grading_cost(self) -> float:
        idx = self.grading_combo.current()
        if idx <= 0:
            return 0.0
        gs_idx = idx - 1
        if gs_idx < len(self.grading_services):
            return self.grading_services[gs_idx]["cost_per_card"]
        return 0.0

    def _calculate(self):
        purchase = self.purchase_price.get()
        tax_rate = self.tax_rate_var.get() / 100.0
        tax_included = self.tax_included.get()
        ship_to_you = self.shipping_to_you.get()
        grading_cost = self._get_grading_cost()

        sale_price = self.sale_price.get()
        shipping_cost = self._get_shipping_cost()
        free_ship = self.free_shipping.get()
        shipping_charged = 0.0 if free_ship else self.shipping_charged.get()

        fp = self._get_selected_fee_profile()
        is_intl = self.is_international.get()

        cb = calculate_cost_basis(
            purchase_price=purchase,
            sales_tax_rate=tax_rate,
            tax_already_included=tax_included,
            shipping_to_you=ship_to_you,
            grading_cost=grading_cost,
        )

        result = calculate_profit(
            sale_price=sale_price,
            shipping_charged=shipping_charged,
            cost_basis=cb["total_cost_basis"],
            shipping_cost=shipping_cost,
            fvf_rate=fp.get("fvf_rate", 0.1325),
            fvf_cap=fp.get("fvf_cap_amount", 7500.0),
            fvf_rate_above_cap=fp.get("fvf_rate_above_cap", 0.0235),
            per_order_threshold=fp.get("per_order_threshold", 10.0),
            per_order_fee_low=fp.get("per_order_fee_low", 0.30),
            per_order_fee_high=fp.get("per_order_fee_high", 0.40),
            is_international=is_intl,
            intl_fee_rate=fp.get("intl_fee_rate", 0.0165),
        )

        # Update cost basis results
        self.res_purchase.set_value(f"${purchase:.2f}")
        self.res_tax.set_value(f"${cb['sales_tax']:.2f}")
        self.res_grading.set_value(f"${grading_cost:.2f}")
        self.res_cost_basis.set_value(f"${cb['total_cost_basis']:.2f}")

        # Update fee results
        fvf_pct = fp.get("fvf_rate", 0.1325) * 100
        self.res_fvf.set_label(f"eBay FVF ({fvf_pct:.2f}%)")
        self.res_fvf.set_value(f"${result['fvf_amount']:.2f}")
        self.res_per_order.set_value(f"${result['per_order_fee']:.2f}")
        self.res_intl.set_value(f"${result['intl_fee']:.2f}")
        self.res_total_fees.set_value(f"${result['total_fees']:.2f}")
        self.res_shipping.set_value(f"${result['shipping_cost']:.2f}")

        # Update profit results
        self.res_net_proceeds.set_value(f"${result['net_proceeds']:.2f}")

        profit = result["net_profit"]
        profit_style = "success" if profit >= 0 else "danger"
        self.res_net_profit.set_value(f"${profit:.2f}", bootstyle=profit_style)

        margin = result["profit_margin_pct"]
        margin_style = "success" if margin >= 0 else "danger"
        self.res_margin.set_value(f"{margin:.1f}%", bootstyle=margin_style)

        roi = result["roi_pct"]
        roi_style = "success" if roi >= 0 else "danger"
        self.res_roi.set_value(f"{roi:.1f}%", bootstyle=roi_style)

    def _clear(self):
        self.purchase_price.set(0.0)
        self.shipping_to_you.set(0.0)
        self.sale_price.set(0.0)
        self.shipping_charged.set(0.0)
        self.tax_included.set(False)
        self.tax_rate_var.set(6.25)
        self.free_shipping.set(False)
        self.is_international.set(False)
        if self.grading_combo["values"]:
            self.grading_combo.current(0)
        if self.shipping_combo["values"]:
            self.shipping_combo.current(0)

        for rc in [
            self.res_purchase, self.res_tax, self.res_grading, self.res_cost_basis,
            self.res_fvf, self.res_per_order, self.res_intl, self.res_total_fees,
            self.res_shipping, self.res_net_proceeds, self.res_net_profit,
            self.res_margin, self.res_roi,
        ]:
            rc.set_value("--")
