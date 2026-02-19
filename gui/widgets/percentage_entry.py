"""Custom entry widget for percentage values."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class PercentageEntry(ttk.Frame):
    def __init__(self, parent, label_text="", default=0.0, **kwargs):
        super().__init__(parent)
        self._var = ttk.DoubleVar(value=default)

        if label_text:
            ttk.Label(self, text=label_text, width=28, anchor=W).pack(side=LEFT, padx=(0, 5))

        self._entry = ttk.Entry(self, textvariable=self._var, width=10, justify=RIGHT, **kwargs)
        self._entry.pack(side=LEFT, padx=(0, 2))
        ttk.Label(self, text="%").pack(side=LEFT)

    def get(self) -> float:
        """Return the percentage as a decimal (e.g., 13.25 -> 0.1325)."""
        try:
            return float(self._var.get()) / 100.0
        except (ValueError, ttk.TclError):
            return 0.0

    def get_display(self) -> float:
        """Return the raw display value (e.g., 13.25)."""
        try:
            return float(self._var.get())
        except (ValueError, ttk.TclError):
            return 0.0

    def set(self, value: float):
        """Set from display value (e.g., 13.25 for 13.25%)."""
        self._var.set(value)

    @property
    def var(self):
        return self._var
