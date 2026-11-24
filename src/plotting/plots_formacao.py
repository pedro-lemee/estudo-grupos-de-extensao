"""Figures for the 'Formação (Extensão vs. Poli)' front. Labels are in PT-BR, as required by the README."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

COLOR_EXT = "#0F4C81"  # extension
COLOR_DISC = "#C84B31"  # mandatory courses
COLOR_NEUTRAL = "#6B7280"


def _finish(fig, ax_list, path=None):
    for ax in np.atleast_1d(ax_list):
        sns.despine(ax=ax)
    fig.tight_layout()
    if path is not None:
        fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.show()


def plot_likert_comparison(df, path=None):
    """Side-by-side percentage bars for preparo_extensao vs preparo_disciplinas (scale 1-5)."""
    levels = [1, 2, 3, 4, 5]
    ext = df["preparo_extensao"].value_counts(normalize=True).reindex(levels, fill_value=0) * 100
    disc = df["preparo_disciplinas"].value_counts(normalize=True).reindex(levels, fill_value=0) * 100
    x = np.arange(len(levels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.2))
    b1 = ax.bar(x - width / 2, disc, width, color=COLOR_DISC, label="Disciplinas obrigatórias")
    b2 = ax.bar(x + width / 2, ext, width, color=COLOR_EXT, label="Grupo de extensão")
    ax.bar_label(b1, fmt="%.0f%%", padding=2, fontsize=8)
    ax.bar_label(b2, fmt="%.0f%%", padding=2, fontsize=8)
    ax.set(
        xticks=x,
        xticklabels=["1", "2", "3", "4", "5"],
        xlabel="Nota atribuída (escala de 1 a 5)",
        ylabel="% dos respondentes",
        title="Preparo profissional percebido: disciplinas vs. extensão (n = %d)" % len(df),
    )
    ax.margins(y=0.15)
    ax.legend(frameon=False)
    _finish(fig, ax, path)


def plot_delta_distribution(df, path=None):
    counts = df["delta_preparo"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 3.8))
    colors = [COLOR_DISC if v < 0 else (COLOR_NEUTRAL if v == 0 else COLOR_EXT) for v in counts.index]
    bars = ax.bar(counts.index.astype(str), counts.values, color=colors)
    ax.bar_label(bars, padding=2, fontsize=9)
    ax.set(
        xlabel="Ganho líquido (preparo na extensão − preparo nas disciplinas)",
        ylabel="Frequência (n)",
        title="Distribuição do ganho líquido de preparo",
    )
    ax.margins(y=0.15)
    _finish(fig, ax, path)


def plot_group_means(
    summary_ext,
    summary_disc,
    group_col,
    title,
    path=None,
    order=None,
    labels=("Grupo de extensão", "Disciplinas obrigatórias"),
    xlabel="Média na escala 1–5 (IC 95% bootstrap)",
):
    """Dot plot of two means (with bootstrap CIs) per group. By default: preparo_extensao vs preparo_disciplinas."""
    ext = summary_ext.set_index(group_col)
    disc = summary_disc.set_index(group_col)
    rows = order or list(ext.index)
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8, 0.55 * len(rows) + 1.6))
    for frame, color, label, offset in [
        (disc, COLOR_DISC, labels[1], 0.12),
        (ext, COLOR_EXT, labels[0], -0.12),
    ]:
        frame = frame.reindex(rows)
        ax.errorbar(
            frame["mean"],
            y + offset,
            xerr=[frame["mean"] - frame["ci_low"], frame["ci_high"] - frame["mean"]],
            fmt="o",
            color=color,
            capsize=3,
            label=label,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([f"{lab} (n={int(ext.loc[lab, 'n'])})" for lab in rows])
    ax.invert_yaxis()
    ax.set(xlim=(1, 5), xlabel=xlabel, title=title)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=2)
    _finish(fig, ax, path)


def plot_proportion_by_level(table, title, xlabel, ylabel, path=None, color=COLOR_EXT):
    """Point estimates with error bars for a proportion per ordered level. `table` has columns
    level, n, prop, ci_low, ci_high."""
    fig, ax = plt.subplots(figsize=(7.5, 4))
    x = np.arange(len(table))
    ax.errorbar(
        x,
        table["prop"] * 100,
        # clip: the Wilson bound can fall a hair below p = 1 because of floating-point error
        yerr=[np.clip(table["prop"] - table["ci_low"], 0, None) * 100, np.clip(table["ci_high"] - table["prop"], 0, None) * 100],
        fmt="o-",
        color=color,
        capsize=4,
    )
    for xi, (p, n) in enumerate(zip(table["prop"], table["n"])):
        ax.annotate(f"{p * 100:.0f}%\n(n={n})", (xi, p * 100), textcoords="offset points", xytext=(12, -4), fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(table["level"])
    ax.set(ylim=(0, 105), xlabel=xlabel, ylabel=ylabel, title=title)
    _finish(fig, ax, path)


def plot_stacked_percent(crosstab, title, xlabel, legend_title, path=None, cmap="Blues"):
    """Horizontal 100% stacked bars of a crosstab (rows = groups, columns = ordered levels)."""
    pct = crosstab.div(crosstab.sum(axis=1), axis=0) * 100
    colors = sns.color_palette(cmap, n_colors=pct.shape[1] + 1)[1:]
    fig, ax = plt.subplots(figsize=(8.5, 0.55 * len(pct) + 1.8))
    left = np.zeros(len(pct))
    for color, col in zip(colors, pct.columns):
        bars = ax.barh(np.arange(len(pct)), pct[col], left=left, color=color, label=str(col))
        for rect, value in zip(bars, pct[col]):
            if value >= 7:
                ax.text(rect.get_x() + rect.get_width() / 2, rect.get_y() + rect.get_height() / 2,
                        f"{value:.0f}", ha="center", va="center", fontsize=8,
                        color="white" if col == pct.columns[-1] or col == pct.columns[-2] else "black")
        left += pct[col].to_numpy()
    ax.set_yticks(np.arange(len(pct)))
    ax.set_yticklabels([f"{idx} (n={int(crosstab.loc[idx].sum())})" for idx in pct.index])
    ax.invert_yaxis()
    ax.set(xlim=(0, 100), xlabel=xlabel, title=title)
    ax.legend(title=legend_title, frameon=False, ncol=pct.shape[1], loc="upper center", bbox_to_anchor=(0.5, -0.3))
    _finish(fig, ax, path)


def plot_coefficients(coef_table, title, xlabel, path=None, ref_line=1.0, log_scale=True):
    """Forest plot. `coef_table` index = labels, columns = estimate, ci_low, ci_high."""
    table = coef_table.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(table) + 1.4))
    y = np.arange(len(table))
    significant = (table["ci_low"] > ref_line) | (table["ci_high"] < ref_line)
    colors = np.where(significant, COLOR_EXT, COLOR_NEUTRAL)
    ax.hlines(y, table["ci_low"], table["ci_high"], color=colors, lw=2)
    ax.scatter(table["estimate"], y, color=colors, zorder=3)
    ax.axvline(ref_line, color="black", lw=0.8, ls="--")
    if log_scale:
        ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels(table.index)
    ax.set(xlabel=xlabel, title=title)
    _finish(fig, ax, path)


def plot_spearman_heatmap(corr, title, path=None):
    fig, ax = plt.subplots(figsize=(7.5, 6))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, square=True,
                cbar_kws={"shrink": 0.7, "label": "ρ de Spearman"}, ax=ax, annot_kws={"fontsize": 8})
    ax.set_title(title)
    fig.tight_layout()
    if path is not None:
        fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.show()
