# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: GUI Charts (Matplotlib)

# PURPOSE: Themed Matplotlib figures for embedding in Tk-based GillPay UI.

# INPUT: Aggregated data (dicts/ordered dicts) from DAO- or service-layer calls.

# PROCESS: Build bar charts for expense by category, income by category,
# income vs expense by month, and net by month.

# OUTPUT: Matplotlib Figure objects suitable for mounting in Tk frames.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Charts for GillPay's Tkinter UI using Matplotlib, with theme-aware
styling."""

from __future__ import annotations

from typing import Dict, OrderedDict as OrderedDictType, List
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from datetime import datetime

# Toggle bubble hatch fill
USE_BUBBLES = True

# Theme (reuse from ui.theme if present)
try:
    from .theme import COLORS as THEME_COLORS
except Exception:
    try:
        from src.ui.theme import COLORS as THEME_COLORS
    except Exception:
        THEME_COLORS = {
            "Navy": "#0A192F",
            "Orange": "#F59E0B",
            "White": "#FFFFFF",
            "Surface": "#E8EEF2",
            "Border": "#D1D9E0",
            "TextOnLight": "#0B2545",
        }


# Helpers

def FmtMonthLabel(s: str, include_year: bool = False) -> str:
    """Convert 'YYYY-MM' or 'YYYY/MM' to 'April' or 'April YYYY'; fall back
    to input on parse failure."""
    t = str(s).strip().replace("/", "-")
    try:
        dt = datetime.strptime(t, "%Y-%m")
        return dt.strftime("%B %Y" if include_year else "%B")
    except ValueError:
        return str(s)


def Currency(v, _):
    """Y-axis currency tick formatter."""
    return f"${v:,.0f}"


def BarLabel(ax, bars, color: str, fontsize: int = 9, padding: int = 3):
    """Apply value labels above bars, with a fallback for older Matplotlib."""
    try:
        labels = [f"${b.get_height():,.0f}" for b in bars]
        ax.bar_label(bars, labels=labels, padding=padding, color=color,
                     fontsize=fontsize, zorder=4, clip=False)
    except AttributeError:
        for b in bars:
            h = b.get_height()
            if not h:
                continue
            x = b.get_x() + b.get_width() / 2
            y = b.get_y() + h
            va = "bottom" if h >= 0 else "top"
            ax.text(
                x,
                y + (padding if h >= 0 else -padding),
                f"${abs(h):,.0f}",
                ha="center",
                va=va,
                color=color,
                fontsize=fontsize,
                zorder=4,
                clip_on=False,
            )


def ApplyBubbles(bars, face, bubble_color, density="oo"):
    """Optional hatch/edge styling for bars."""
    if not USE_BUBBLES:
        return
    for b in bars:
        b.set_facecolor(face)
        b.set_edgecolor(bubble_color)
        b.set_linewidth(0.8)
        b.set_hatch(density)
        b.set_alpha(1.0)


# Charts (respect input order)

def BuildExpenseByCategoryFigure(
        Totals: Dict[str, float],
        Title: str = "Expenses by Category (Top 10)",
        top_n: int = 10,
) -> Figure:
    """Build a bar chart of top-N expense categories."""
    items = sorted(((k, abs(v)) for k, v in Totals.items() if abs(v) > 0),
                   key=lambda x: x[1], reverse=True)[:top_n]
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    fig = Figure(figsize=(10, 5), dpi=100, constrained_layout=True,
                 facecolor=THEME_COLORS["Navy"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS["Navy"])
    ax.set_axisbelow(True)

    x = list(range(len(values)))
    bars = ax.bar(x, values, color=THEME_COLORS["Orange"], edgecolor="none",
                  zorder=3, alpha=1.0)
    ax.set_xlim(-0.5, len(x) - 0.5)
    ApplyBubbles(bars, face=THEME_COLORS["Orange"],
                 bubble_color=THEME_COLORS["White"], density="O")

    ax.set_ylim(0, max(values or [1]) * 1.15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right",
                       color=THEME_COLORS["White"])
    ax.tick_params(axis="y", labelcolor=THEME_COLORS["White"])
    ax.yaxis.set_major_formatter(FuncFormatter(Currency))

    ax.set_title(Title, color=THEME_COLORS["White"])
    ax.grid(axis="y", alpha=0.25, color=THEME_COLORS["Surface"], zorder=0)
    for s in ax.spines.values():
        s.set_color(THEME_COLORS["Surface"])

    BarLabel(ax, bars, THEME_COLORS["White"])
    return fig


def BuildIncomeByCategoryFigure(
        Totals: Dict[str, float],
        Title: str = "Income by Category (Top 10)",
        top_n: int = 10,
) -> Figure:
    """Build a bar chart of top-N income categories."""
    items = sorted(((k, abs(v)) for k, v in Totals.items() if abs(v) > 0),
                   key=lambda x: x[1], reverse=True)[:top_n]
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    fig = Figure(figsize=(10, 5), dpi=100, constrained_layout=True,
                 facecolor=THEME_COLORS["Navy"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS["Navy"])
    ax.set_axisbelow(True)

    x = list(range(len(values)))
    bars = ax.bar(x, values, color=THEME_COLORS["Surface"], edgecolor="none",
                  zorder=3, alpha=1.0)
    ax.set_xlim(-0.5, len(x) - 0.5)
    ApplyBubbles(
        bars,
        face=THEME_COLORS["Surface"],
        bubble_color=THEME_COLORS.get("TextOnLight", "#0B2545"),
        density="o",
    )

    ax.set_ylim(0, max(values or [1]) * 1.15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, color=THEME_COLORS["White"])
    ax.tick_params(axis="y", labelcolor=THEME_COLORS["White"])
    ax.yaxis.set_major_formatter(FuncFormatter(Currency))

    ax.set_title(Title, color=THEME_COLORS["White"])
    ax.grid(axis="y", alpha=0.25, color=THEME_COLORS["Surface"], zorder=0)
    for s in ax.spines.values():
        s.set_color(THEME_COLORS["Surface"])

    BarLabel(ax, bars, THEME_COLORS["White"])
    return fig


def BuildIncomeExpenseByMonthFigure(
        Data: "OrderedDictType[str, Dict[str, float]]",
        Title: str = "Income vs Expense by Month",
) -> Figure:
    """Build a grouped bar chart for income vs expense by month."""
    months: List[str] = list(Data.keys())
    incomes = [Data[m].get("income", 0.0) for m in months]
    expenses = [Data[m].get("expense", 0.0) for m in months]

    fig = Figure(figsize=(10, 5), dpi=100, constrained_layout=True,
                 facecolor=THEME_COLORS["Navy"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS["Navy"])
    ax.set_axisbelow(True)

    x = list(range(len(months)))
    w = 0.42
    bars_inc = ax.bar(
        [i - w / 2 for i in x],
        incomes,
        width=w,
        label="Income",
        color=THEME_COLORS["Surface"],
        edgecolor="none",
        zorder=3,
        alpha=1.0,
    )
    bars_exp = ax.bar(
        [i + w / 2 for i in x],
        expenses,
        width=w,
        label="Expense",
        color=THEME_COLORS["Orange"],
        edgecolor="none",
        zorder=3,
        alpha=1.0,
    )
    ax.set_xlim(-0.5, len(x) - 0.5)

    ApplyBubbles(bars_inc, face=THEME_COLORS["Surface"],
                 bubble_color=THEME_COLORS.get("TextOnLight", "#0B2545"),
                 density="o")
    ApplyBubbles(bars_exp, face=THEME_COLORS["Orange"],
                 bubble_color=THEME_COLORS["White"], density="oo")

    ax.set_ylim(0, (max([*(incomes or [0]), *(expenses or [0])]) * 1.20) or 1)
    ax.set_xticks(x)
    ax.set_xticklabels([FmtMonthLabel(m, include_year=True) for m in months],
                       rotation=0, color=THEME_COLORS["White"])
    ax.legend(facecolor=THEME_COLORS["Surface"],
              edgecolor=THEME_COLORS["Surface"])

    ax.set_title(Title, color=THEME_COLORS["White"])
    ax.tick_params(axis="y", labelcolor=THEME_COLORS["White"])
    ax.yaxis.set_major_formatter(FuncFormatter(Currency))
    ax.grid(axis="y", alpha=0.25, color=THEME_COLORS["Surface"], zorder=0)
    for s in ax.spines.values():
        s.set_color(THEME_COLORS["Surface"])

    BarLabel(ax, bars_inc, THEME_COLORS["White"])
    BarLabel(ax, bars_exp, THEME_COLORS["White"])
    return fig


def BuildNetByMonthFigure(
        Data: "OrderedDictType[str, Dict[str, float]]",
        Title: str = "Net by Month",
) -> Figure:
    """Build a centered bar chart for monthly net totals."""
    months: List[str] = list(Data.keys())
    nets = [Data[m].get("net", 0.0) for m in months]

    fig = Figure(figsize=(10, 5), dpi=100, constrained_layout=True,
                 facecolor=THEME_COLORS["Navy"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS["Navy"])
    ax.set_axisbelow(True)

    x = list(range(len(months)))
    bars = ax.bar(x, nets, color=THEME_COLORS["Orange"], edgecolor="none",
                  zorder=3, alpha=1.0)
    ax.set_xlim(-0.5, len(x) - 0.5)
    ApplyBubbles(bars, face=THEME_COLORS["Orange"],
                 bubble_color=THEME_COLORS["White"], density="O")

    max_abs = max([abs(v) for v in nets] or [1])
    ax.set_ylim(-max_abs * 1.20, max_abs * 1.20)
    ax.axhline(0, linewidth=1, color=THEME_COLORS["Surface"], alpha=0.6,
               zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels([FmtMonthLabel(m, include_year=True) for m in months],
                       rotation=0, color=THEME_COLORS["White"])

    ax.set_title(Title, color=THEME_COLORS["White"])
    ax.tick_params(axis="y", labelcolor=THEME_COLORS["White"])
    ax.yaxis.set_major_formatter(FuncFormatter(Currency))
    ax.grid(axis="y", alpha=0.25, color=THEME_COLORS["Surface"], zorder=0)
    for s in ax.spines.values():
        s.set_color(THEME_COLORS["Surface"])

    BarLabel(ax, bars, THEME_COLORS["White"])
    return fig


# Tk embedding helper

def MountFigureInTk(FrameWidget, FigureObj: Figure):
    """Mount a Matplotlib Figure inside a Tk frame and keep it sized to fit."""
    for child in FrameWidget.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    try:
        FigureObj.set_constrained_layout(True)
    except Exception:
        pass

    canvas = FigureCanvasTkAgg(FigureObj, master=FrameWidget)
    widget = canvas.get_tk_widget()
    widget.pack(fill="both", expand=True)
    canvas.draw()

    FrameWidget._mpl_canvas = canvas
    FrameWidget._mpl_fig = FigureObj
    FrameWidget._mpl_after = None

    def DoResize():
        FrameWidget._mpl_after = None
        fig = FrameWidget._mpl_fig
        cvs = FrameWidget._mpl_canvas
        if not fig or not cvs:
            return
        w_px = max(200, FrameWidget.winfo_width())
        h_px = max(200, FrameWidget.winfo_height())
        dpi = float(fig.get_dpi() or 100.0)
        fig.set_size_inches(w_px / dpi, h_px / dpi, forward=True)
        cvs.draw_idle()

    def OnResize(_evt):
        if FrameWidget._mpl_after is not None:
            FrameWidget.after_cancel(FrameWidget._mpl_after)
        FrameWidget._mpl_after = FrameWidget.after(60, DoResize)

    FrameWidget.bind("<Configure>", OnResize)
    FrameWidget.after(0, DoResize)
    return canvas
