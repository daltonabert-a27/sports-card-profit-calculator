"""Break-even Analysis tab - graded vs raw comparison."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from database.repository import GradingRepository, ShippingRepository, FeeProfileRepository
from services.breakeven import multi_service_breakeven
from gui.widgets.currency_entry import CurrencyEntry

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class BreakevenTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=15)
        self.conn = conn
        self.settings = settings
        self.grading_repo = GradingRepository(conn)
        self.shipping_repo = ShippingRepository(conn)
        self.fee_repo = FeeProfileRepository(conn)

        self.grading_services = self.grading_repo.get_all_active()
        self.shipping_options = self.shipping_repo.get_all_active()
        self.fee_profiles = self.fee_repo.get_all()
        self.grading_check_vars = []

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=X, pady=(0, 10))

        # Left: inputs
        left = ttk.Labelframe(top, text="  Card Details  ", padding=15)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))

        self.raw_cost = CurrencyEntry(left, "Raw Card Cost Basis:")
        self.raw_cost.pack(fill=X, pady=2)

        self.raw_market = CurrencyEntry(left, "Raw Market Value (sell now):")
        self.raw_market.pack(fill=X, pady=2)

        self.graded_market = CurrencyEntry(left, "Expected Graded Value:")
        self.graded_market.pack(fill=X, pady=2)

        grade_frame = ttk.Frame(left)
        grade_frame.pack(fill=X, pady=2)
        ttk.Label(grade_frame, text="Expected Grade:", width=28, anchor=W).pack(side=LEFT)
        self.expected_grade = ttk.StringVar(value="10")
        ttk.Combobox(
            grade_frame, textvariable=self.expected_grade,
            values=["10", "9.5", "9", "8.5", "8", "7", "6", "Authentic"],
            width=10,
        ).pack(side=LEFT)

        # Shipping selections
        ship_frame = ttk.Frame(left)
        ship_frame.pack(fill=X, pady=2)
        ttk.Label(ship_frame, text="Raw Shipping Cost:", width=28, anchor=W).pack(side=LEFT)
        self.raw_ship_var = ttk.DoubleVar(value=0.56)
        ttk.Entry(ship_frame, textvariable=self.raw_ship_var, width=8, justify=RIGHT).pack(side=LEFT)
        ttk.Label(ship_frame, text="  (eBay Std Envelope)").pack(side=LEFT)

        ship2 = ttk.Frame(left)
        ship2.pack(fill=X, pady=2)
        ttk.Label(ship2, text="Graded Shipping Cost:", width=28, anchor=W).pack(side=LEFT)
        self.graded_ship_var = ttk.DoubleVar(value=4.63)
        ttk.Entry(ship2, textvariable=self.graded_ship_var, width=8, justify=RIGHT).pack(side=LEFT)
        ttk.Label(ship2, text="  (USPS Ground Advantage)").pack(side=LEFT)

        ttk.Button(
            left, text="Analyze Break-even", bootstyle="success",
            command=self._analyze, padding=(20, 8),
        ).pack(fill=X, pady=(10, 0))

        # Right: grading services to compare
        right = ttk.Labelframe(top, text="  Grading Services to Compare  ", padding=15)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        # Select all / none
        sel_frame = ttk.Frame(right)
        sel_frame.pack(fill=X, pady=(0, 5))
        ttk.Button(sel_frame, text="Select All", bootstyle="info-outline",
                   command=lambda: self._set_all_checks(True)).pack(side=LEFT, padx=(0, 5))
        ttk.Button(sel_frame, text="Select None", bootstyle="secondary-outline",
                   command=lambda: self._set_all_checks(False)).pack(side=LEFT)

        # Grading checkboxes
        check_canvas = ttk.Canvas(right, highlightthickness=0, height=180)
        check_scroll = ttk.Scrollbar(right, orient=VERTICAL, command=check_canvas.yview)
        check_frame = ttk.Frame(check_canvas)
        check_frame.bind("<Configure>", lambda e: check_canvas.configure(scrollregion=check_canvas.bbox("all")))
        check_canvas.create_window((0, 0), window=check_frame, anchor=NW)
        check_canvas.configure(yscrollcommand=check_scroll.set)
        check_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        check_scroll.pack(side=RIGHT, fill=Y)

        for gs in self.grading_services:
            var = ttk.BooleanVar(value=True)
            label = f"{gs['company']} - {gs['tier_name']} (${gs['cost_per_card']:.2f}, ~{gs['turnaround_days']}d)"
            ttk.Checkbutton(check_frame, text=label, variable=var).pack(anchor=W, pady=1)
            self.grading_check_vars.append((var, gs))

        # Results section
        results_frame = ttk.Labelframe(self, text="  Results  ", padding=10)
        results_frame.pack(fill=BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(
            results_frame,
            columns=("service", "cost", "raw_profit", "graded_profit", "extra_profit",
                     "grading_roi", "breakeven", "verdict"),
            show="headings",
            height=8,
        )
        cols = [
            ("service", "Grading Service", 180),
            ("cost", "Grading Cost", 90),
            ("raw_profit", "Raw Profit", 90),
            ("graded_profit", "Graded Profit", 100),
            ("extra_profit", "Extra Profit", 90),
            ("grading_roi", "Grading ROI", 90),
            ("breakeven", "Breakeven Price", 110),
            ("verdict", "Verdict", 80),
        ]
        for col_id, heading, width in cols:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=CENTER)

        tree_scroll = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        tree_scroll.pack(side=RIGHT, fill=Y)

        # Chart area (if matplotlib available)
        if HAS_MATPLOTLIB:
            self.chart_frame = ttk.Labelframe(self, text="  Profit Comparison Chart  ", padding=5)
            self.chart_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
            self.fig = Figure(figsize=(8, 2.5), dpi=80)
            self.fig.patch.set_facecolor("#303030")
            self.chart_canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
            self.chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def _set_all_checks(self, value: bool):
        for var, _ in self.grading_check_vars:
            var.set(value)

    def _analyze(self):
        raw_cost = self.raw_cost.get()
        raw_market = self.raw_market.get()
        graded_market = self.graded_market.get()
        grade = self.expected_grade.get()

        selected = [gs for var, gs in self.grading_check_vars if var.get()]
        if not selected:
            return

        grading_options = [
            {"company": gs["company"], "tier": gs["tier_name"], "cost": gs["cost_per_card"]}
            for gs in selected
        ]

        fp = next((f for f in self.fee_profiles if f["is_default"]), self.fee_profiles[0] if self.fee_profiles else {})

        results = multi_service_breakeven(
            raw_cost_basis=raw_cost,
            raw_market_value=raw_market,
            graded_market_value=graded_market,
            expected_grade=grade,
            grading_options=grading_options,
            fvf_rate=fp.get("fvf_rate", 0.1325),
            raw_shipping_cost=self.raw_ship_var.get(),
            graded_shipping_cost=self.graded_ship_var.get(),
        )

        # Populate tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in results:
            tag = "grade" if r["recommendation"] == "GRADE" else "raw"
            self.tree.insert("", END, values=(
                f"{r['grading_company']} - {r.get('tier', '')}",
                f"${r['grading_cost']:.2f}",
                f"${r['raw_profit']:.2f}",
                f"${r['graded_profit']:.2f}",
                f"${r['grading_extra_profit']:.2f}",
                f"{r['grading_roi_pct']:.1f}%",
                f"${r['breakeven_graded_price']:.2f}",
                r["recommendation"],
            ), tags=(tag,))

        self.tree.tag_configure("grade", foreground="#00bc8c")
        self.tree.tag_configure("raw", foreground="#f0ad4e")

        # Update chart
        if HAS_MATPLOTLIB:
            self._update_chart(results)

    def _update_chart(self, results):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#303030")

        labels = [f"{r['grading_company']}\n{r.get('tier', '')}" for r in results]
        raw_profits = [r["raw_profit"] for r in results]
        graded_profits = [r["graded_profit"] for r in results]

        x = range(len(labels))
        width = 0.35

        bars1 = ax.bar([i - width / 2 for i in x], raw_profits, width, label="Raw", color="#f0ad4e", alpha=0.8)
        bars2 = ax.bar([i + width / 2 for i in x], graded_profits, width, label="Graded", color="#00bc8c", alpha=0.8)

        ax.set_ylabel("Profit ($)", color="white", fontsize=9)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=7, color="white")
        ax.tick_params(axis="y", colors="white")
        ax.legend(fontsize=8, facecolor="#404040", edgecolor="#606060", labelcolor="white")
        ax.axhline(y=0, color="white", linewidth=0.5, alpha=0.3)

        self.fig.tight_layout()
        self.chart_canvas.draw()
