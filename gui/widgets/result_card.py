"""Styled result display panel for showing calculation outputs."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ResultCard(ttk.Frame):
    def __init__(self, parent, label_text="", bootstyle="default", font_size=14):
        super().__init__(parent, padding=10)
        self._label = ttk.Label(
            self,
            text=label_text,
            font=("-size", 10),
            bootstyle="secondary",
        )
        self._label.pack(anchor=W)

        self._value = ttk.Label(
            self,
            text="--",
            font=("-size", font_size, "-weight", "bold"),
            bootstyle=bootstyle,
        )
        self._value.pack(anchor=W, pady=(2, 0))

    def set_value(self, text: str, bootstyle: str | None = None):
        self._value.config(text=text)
        if bootstyle:
            self._value.config(bootstyle=bootstyle)

    def set_label(self, text: str):
        self._label.config(text=text)
