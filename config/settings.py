"""Runtime settings manager backed by SQLite settings table."""

from config.defaults import (
    DEFAULT_FVF_RATE,
    DEFAULT_SALES_TAX_RATE,
    DEFAULT_INTL_FEE_RATE,
    DEFAULT_PER_ORDER_FEE_HIGH,
    DEFAULT_PER_ORDER_FEE_LOW,
    DEFAULT_PER_ORDER_THRESHOLD,
)

_DEFAULTS = {
    "fvf_rate": str(DEFAULT_FVF_RATE),
    "sales_tax_rate": str(DEFAULT_SALES_TAX_RATE),
    "intl_fee_rate": str(DEFAULT_INTL_FEE_RATE),
    "per_order_fee_low": str(DEFAULT_PER_ORDER_FEE_LOW),
    "per_order_fee_high": str(DEFAULT_PER_ORDER_FEE_HIGH),
    "per_order_threshold": str(DEFAULT_PER_ORDER_THRESHOLD),
    "ebay_client_id": "",
    "ebay_client_secret": "",
    "ebay_environment": "PRODUCTION",
}


class SettingsManager:
    def __init__(self, db_connection):
        self._conn = db_connection

    def get(self, key: str, default: str | None = None) -> str:
        cursor = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        if default is not None:
            return default
        return _DEFAULTS.get(key, "")

    def get_float(self, key: str) -> float:
        return float(self.get(key, "0"))

    def set(self, key: str, value: str):
        self._conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value)),
        )
        self._conn.commit()

    def seed_defaults(self):
        for key, value in _DEFAULTS.items():
            cursor = self._conn.execute(
                "SELECT 1 FROM settings WHERE key = ?", (key,)
            )
            if not cursor.fetchone():
                self._conn.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)", (key, value)
                )
        self._conn.commit()
