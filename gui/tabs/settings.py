"""Settings tab - configure fees, API credentials, and defaults."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox


class SettingsTab(ttk.Frame):
    def __init__(self, parent, conn, settings):
        super().__init__(parent, padding=15)
        self.conn = conn
        self.settings = settings

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        # Scrollable content
        canvas = ttk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        container = scroll_frame

        # --- eBay API Section ---
        api_frame = ttk.LabelFrame(container, text="  eBay API Credentials  ", padding=15)
        api_frame.pack(fill=X, pady=(0, 10), padx=5)

        ttk.Label(api_frame, text="Get credentials at developer.ebay.com", bootstyle="secondary").pack(anchor=W, pady=(0, 5))

        row = ttk.Frame(api_frame)
        row.pack(fill=X, pady=2)
        ttk.Label(row, text="Client ID (App ID):", width=22, anchor=W).pack(side=LEFT)
        self.api_client_id = ttk.StringVar()
        ttk.Entry(row, textvariable=self.api_client_id, width=50).pack(side=LEFT, fill=X, expand=True)

        row2 = ttk.Frame(api_frame)
        row2.pack(fill=X, pady=2)
        ttk.Label(row2, text="Client Secret (Cert ID):", width=22, anchor=W).pack(side=LEFT)
        self.api_client_secret = ttk.StringVar()
        ttk.Entry(row2, textvariable=self.api_client_secret, width=50, show="*").pack(side=LEFT, fill=X, expand=True)

        row3 = ttk.Frame(api_frame)
        row3.pack(fill=X, pady=2)
        ttk.Label(row3, text="Environment:", width=22, anchor=W).pack(side=LEFT)
        self.api_env = ttk.StringVar(value="PRODUCTION")
        ttk.Combobox(
            row3, textvariable=self.api_env,
            values=["PRODUCTION", "SANDBOX"], state="readonly", width=15,
        ).pack(side=LEFT)

        # --- Fee Defaults Section ---
        fee_frame = ttk.LabelFrame(container, text="  Default Fee Rates  ", padding=15)
        fee_frame.pack(fill=X, pady=(0, 10), padx=5)

        self.fvf_rate = self._make_setting_row(fee_frame, "FVF Rate (%):", 13.25)
        self.per_order_low = self._make_setting_row(fee_frame, "Per-Order Fee (<=$10):", 0.30, prefix="$")
        self.per_order_high = self._make_setting_row(fee_frame, "Per-Order Fee (>$10):", 0.40, prefix="$")
        self.intl_rate = self._make_setting_row(fee_frame, "International Fee (%):", 1.65)

        # --- Tax Section ---
        tax_frame = ttk.LabelFrame(container, text="  Sales Tax  ", padding=15)
        tax_frame.pack(fill=X, pady=(0, 10), padx=5)

        self.tax_rate = self._make_setting_row(tax_frame, "Default Tax Rate (%):", 6.25)

        # --- Buttons ---
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=10, padx=5)

        ttk.Button(
            btn_frame, text="Save Settings", bootstyle="success",
            command=self._save_settings, padding=(20, 8),
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            btn_frame, text="Reset to Defaults", bootstyle="warning-outline",
            command=self._reset_defaults,
        ).pack(side=LEFT)

    def _make_setting_row(self, parent, label, default, prefix=""):
        row = ttk.Frame(parent)
        row.pack(fill=X, pady=2)
        ttk.Label(row, text=label, width=25, anchor=W).pack(side=LEFT)
        if prefix:
            ttk.Label(row, text=prefix).pack(side=LEFT)
        var = ttk.DoubleVar(value=default)
        ttk.Entry(row, textvariable=var, width=10, justify=RIGHT).pack(side=LEFT)
        return var

    def _load_settings(self):
        self.api_client_id.set(self.settings.get("ebay_client_id", ""))
        self.api_client_secret.set(self.settings.get("ebay_client_secret", ""))
        self.api_env.set(self.settings.get("ebay_environment", "PRODUCTION"))

        fvf = self.settings.get("fvf_rate", "0.1325")
        self.fvf_rate.set(float(fvf) * 100)

        self.per_order_low.set(float(self.settings.get("per_order_fee_low", "0.30")))
        self.per_order_high.set(float(self.settings.get("per_order_fee_high", "0.40")))

        intl = self.settings.get("intl_fee_rate", "0.0165")
        self.intl_rate.set(float(intl) * 100)

        tax = self.settings.get("sales_tax_rate", "0.0625")
        self.tax_rate.set(float(tax) * 100)

    def _save_settings(self):
        self.settings.set("ebay_client_id", self.api_client_id.get())
        self.settings.set("ebay_client_secret", self.api_client_secret.get())
        self.settings.set("ebay_environment", self.api_env.get())
        self.settings.set("fvf_rate", str(self.fvf_rate.get() / 100))
        self.settings.set("per_order_fee_low", str(self.per_order_low.get()))
        self.settings.set("per_order_fee_high", str(self.per_order_high.get()))
        self.settings.set("intl_fee_rate", str(self.intl_rate.get() / 100))
        self.settings.set("sales_tax_rate", str(self.tax_rate.get() / 100))

        Messagebox.show_info("Settings saved successfully.", title="Settings Saved")

    def _reset_defaults(self):
        self.fvf_rate.set(13.25)
        self.per_order_low.set(0.30)
        self.per_order_high.set(0.40)
        self.intl_rate.set(1.65)
        self.tax_rate.set(6.25)
