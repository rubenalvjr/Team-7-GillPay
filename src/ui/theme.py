# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Theme

# PURPOSE: Centralized GillPay UI theme and widget styles for Tk/ttk.

# INPUT: Tk root window.

# PROCESS: Configure ttk styles (entries, comboboxes, buttons, notebook,
# treeview, etc.) and return a color map.

# OUTPUT: Dict of theme colors to be reused by the application.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.


"""GillPay theme: shared colors and ttk style configuration.

This module defines the GillPay color palette and a helper to apply a consistent
ttk styling across the app. Call `ApplyTheme(root)` once after creating the Tk
root to set up styles used by the GUI (e.g., `Gill.TButton`, `Gill.Treeview`).
"""

import tkinter as tk
from tkinter import ttk

# Base palette used throughout the UI.
COLORS = {
    "Navy": "#0B2545",
    "Blue": "#13315C",
    "Blue2": "#1D3557",
    "Orange": "#F26419",
    "TextOnDark": "#F5F7FA",
    "TextOnLight": "#0B2545",
    "Surface": "#E8EEF2",
    "White": "#FFFFFF",
    "Black": "#000000",
    "Border": "#D1D9E0",
    "Selection": "#F7A26E",
    "Disabled": "#A8B3BF",
}


def ApplyTheme(root: tk.Tk) -> dict[str, str]:
    """Configure ttk styles for GillPay and return the color palette.

    Sets the theme to "clam" when available, applies style rules for common
    widgets (Entry, Combobox, Buttons, Notebook, Treeview, etc.), and returns
    the color map so callers can reuse consistent colors.

    Args:
        root: The Tk root window (or a widget associated with the root).

    Returns:
        dict[str, str]: The GillPay color palette (hex strings by name).
    """
    colors = {
        "Navy": "#0B2545",
        "Blue": "#13315C",
        "Blue2": "#1D3557",
        "Orange": "#F26419",
        "TextOnDark": "#F5F7FA",
        "TextOnLight": "#0B2545",
        "Surface": "#E8EEF2",
        "White": "#FFFFFF",
        "Black": "#000000",
        "Border": "#D1D9E0",
        "Selection": "#F7A26E",
        "Disabled": "#A8B3BF",
    }

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=colors["Navy"])
    style.configure(".", background=colors["Orange"],
                    foreground=colors["TextOnLight"])

    style.configure("TLabel", background=colors["Surface"],
                    foreground=colors["TextOnLight"])

    style.configure("TEntry", fieldbackground=colors["White"],
                    foreground=colors["TextOnLight"])
    style.map(
        "TEntry",
        foreground=[("disabled", colors["Disabled"])],
        fieldbackground=[("disabled", "#F3F6F8")],
        bordercolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
        lightcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
        darkcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
    )

    style.configure("TCombobox", fieldbackground=colors["White"],
                    foreground=colors["TextOnLight"])
    style.map(
        "TCombobox",
        foreground=[("disabled", colors["Disabled"])],
        fieldbackground=[("readonly", "#F6F8FB"), ("disabled", "#F3F6F8")],
        bordercolor=[("focus", colors["White"]), ("!focus", colors["Border"])],
        lightcolor=[("focus", colors["White"]), ("!focus", colors["Border"])],
        darkcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
    )

    style.configure(
        "Gill.DateEntry",
        fieldbackground=colors["White"],
        foreground=colors["TextOnLight"],
        background=colors["Orange"],
        arrowcolor=colors["Black"],
    )
    style.map(
        "Gill.DateEntry",
        background=[
            ("pressed", colors["Orange"]),
            ("active", colors["Orange"]),
            ("focus", colors["Orange"]),
            ("readonly", colors["Orange"]),
            ("!disabled", colors["Orange"]),
        ],
        fieldbackground=[("readonly", "#F6F8FB"), ("disabled", "#F3F6F8")],
        arrowcolor=[
            ("disabled", colors["Disabled"]),
            ("!disabled", colors["Black"]),
            ("active", colors["Black"]),
            ("focus", colors["Black"]),
        ],
    )

    style.configure("TMenubutton", background=colors["Orange"],
                    arrowcolor=colors["Black"])
    style.map(
        "TMenubutton",
        background=[
            ("pressed", colors["Orange"]),
            ("active", colors["Orange"]),
            ("focus", colors["Orange"]),
            ("!disabled", colors["Orange"]),
        ],
        arrowcolor=[
            ("disabled", colors["Disabled"]),
            ("!disabled", colors["Black"]),
            ("active", colors["Black"]),
            ("focus", colors["Black"]),
        ],
    )

    style.configure("Gill.TButton", background=colors["Navy"],
                    foreground=colors["White"], borderwidth=0, padding=(12, 6))
    style.map(
        "Gill.TButton",
        background=[("active", colors["Selection"]),
                    ("pressed", colors["Orange"]), ("disabled", "#F0B995")],
        foreground=[("disabled", "#FFFFFF")],
    )

    style.configure("Gill.TNotebook", background=colors["Surface"],
                    borderwidth=0)
    style.configure("Gill.TNotebook.Tab", background=colors["Blue"],
                    foreground=colors["TextOnDark"], padding=(14, 8))
    style.map(
        "Gill.TNotebook.Tab",
        background=[("selected", colors["Navy"]), ("active", colors["Blue2"])],
        foreground=[("selected", colors["TextOnDark"]),
                    ("disabled", colors["Disabled"])],
        padding=[("selected", (14, 8)), ("active", (14, 8)),
                 ("!selected", (12, 6))],
    )

    style.configure(
        "Gill.Treeview",
        background=colors["White"],
        foreground=colors["TextOnLight"],
        fieldbackground=colors["White"],
        rowheight=24,
        bordercolor=colors["Border"],
        borderwidth=1,
    )
    style.map(
        "Gill.Treeview",
        background=[("selected", colors["Selection"])],
        foreground=[("selected", colors["TextOnLight"])],
    )
    style.configure(
        "Gill.Treeview.Heading",
        background=colors["Navy"],
        foreground=colors["TextOnDark"],
        relief="flat",
        padding=(6, 4),
    )
    style.map("Gill.Treeview.Heading", background=[("active", colors["Blue"])],
              relief=[("pressed", "groove")])

    style.configure(
        "Visualize.TButton",
        background=colors["Navy"],
        foreground=colors["White"],
        font=("Segoe UI", 11, "bold"),
        padding=(14, 8),
        borderwidth=0,
    )
    style.map(
        "Visualize.TButton",
        background=[("active", colors["Blue2"]), ("pressed", colors["Orange"]),
                    ("disabled", colors["Disabled"])],
        foreground=[("disabled", colors["White"])],
    )

    style.configure("Vertical.TScrollbar", background=colors["Surface"],
                    troughcolor=colors["Surface"],
                    bordercolor=colors["Surface"])
    style.configure("Horizontal.TScrollbar", background=colors["Surface"],
                    troughcolor=colors["Surface"],
                    bordercolor=colors["Surface"])

    style.configure("TCheckbutton", background=colors["Surface"],
                    foreground=colors["TextOnLight"])
    style.configure("TRadiobutton", background=colors["Surface"],
                    foreground=colors["TextOnLight"])

    style.configure("TSeparator", background=colors["Border"])

    return colors
