"""Custom entry widget for dollar amounts."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CurrencyEntry(ttk.Frame):
    def __init__(self, parent, label_text="", default=0.0, **kwargs):
        super().__init__(parent)
        self._var = ttk.DoubleVar(value=default)

        if label_text:
            ttk.Label(self, text=label_text, width=28, anchor=W).pack(side=LEFT, padx=(0, 5))

        ttk.Label(self, text="$").pack(side=LEFT)
        self._entry = ttk.Entry(self, textvariable=self._var, width=12, justify=RIGHT, **kwargs)
        self._entry.pack(side=LEFT, padx=(0, 5))

    def get(self) -> float:
        try:
            return float(self._var.get())
        except (ValueError, ttk.TclError):
            return 0.0

    def set(self, value: float):
        self._var.set(value)

    @property
    def var(self):
        return self._var
