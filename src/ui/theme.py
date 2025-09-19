# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.

import tkinter as tk
from tkinter import ttk

def ApplyTheme(root: tk.Tk):
    colors = {
        "Navy": "#0B2545",
        "Blue": "#13315C",
        "Blue2": "#1D3557",
        "Orange": "#F26419",
        "TextOnDark": "#F5F7FA",
        "TextOnLight": "#0B2545",
        "Surface": "#E8EEF2",
        "White": "#FFFFFF",
        "Border": "#D1D9E0",
        "Selection": "#F7A26E",
        "Disabled": "#A8B3BF",
    }

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # App background and default colors
    root.configure(bg=colors["Navy"])
    style.configure(
        ".",
        background=colors["Orange"],
        foreground=colors["TextOnLight"],
    )

    # Labels
    style.configure("TLabel", background=colors["Surface"], foreground=colors["TextOnLight"])

    # Entries
    style.configure("TEntry", fieldbackground=colors["White"], foreground=colors["TextOnLight"])
    style.map(
        "TEntry",
        foreground=[("disabled", colors["Disabled"])],
        fieldbackground=[("disabled", "#F3F6F8")],
        bordercolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
        lightcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
        darkcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
    )

    # Combobox (keeps same field look as Entry)
    style.configure("TCombobox", fieldbackground=colors["White"], foreground=colors["TextOnLight"])
    style.map(
        "TCombobox",
        foreground=[("disabled", colors["Disabled"])],
        fieldbackground=[("readonly", "#F6F8FB"), ("disabled", "#F3F6F8")],
        bordercolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
        lightcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
        darkcolor=[("focus", colors["Orange"]), ("!focus", colors["Border"])],
    )

    # Primary button (your app uses Gill.TButton)
    style.configure(
        "Gill.TButton",
        background=colors["Navy"],
        foreground=colors["White"],
        borderwidth=0,
        padding=(12, 6),
    )
    style.map(
        "Gill.TButton",
        background=[("active", colors["Selection"]), ("pressed", colors["Orange"]), ("disabled", "#F0B995")],
        foreground=[("disabled", "#FFFFFF")],
    )

    # Notebook (tabs)
    style.configure("Gill.TNotebook", background=colors["Surface"], borderwidth=0)
    style.configure(
        "Gill.TNotebook.Tab",
        background=colors["Blue"],
        foreground=colors["TextOnDark"],
        padding=(14, 8),
    )
    style.map(
        "Gill.TNotebook.Tab",
        background=[("selected", colors["Navy"]), ("active", colors["Blue2"])],
        foreground=[("selected", colors["TextOnDark"]), ("disabled", colors["Disabled"])],
    )

    # Treeview (table)
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
    style.map(
        "Gill.Treeview.Heading",
        background=[("active", colors["Blue"])],
        relief=[("pressed", "groove")],
    )

    # Scrollbars (subtle to match Surface)
    style.configure("Vertical.TScrollbar", background=colors["Surface"], troughcolor=colors["Surface"], bordercolor=colors["Surface"])
    style.configure("Horizontal.TScrollbar", background=colors["Surface"], troughcolor=colors["Surface"], bordercolor=colors["Surface"])

    # Checkbutton / Radiobutton to fit scheme
    style.configure("TCheckbutton", background=colors["Surface"], foreground=colors["TextOnLight"])
    style.configure("TRadiobutton", background=colors["Surface"], foreground=colors["TextOnLight"])

    # Separators
    style.configure("TSeparator", background=colors["Border"])

    return colors
