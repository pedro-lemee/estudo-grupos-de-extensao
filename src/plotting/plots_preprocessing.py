import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot_histograms(df: pd.DataFrame, titles):
    fig, axes = plt.subplots(1, len(titles), figsize=(18, 4.5), constrained_layout=True)

    for ax, (col, title) in zip(axes, titles.items()):
        sns.countplot(data=df, x=col, color="#0F4C81", ax=ax)
        ax.set(title=title, xlabel="", ylabel="")
        ax.tick_params(axis="x", rotation=25)
        plt.setp(ax.get_xticklabels(), ha="right")
        ax.bar_label(ax.containers[0], padding=3, fontsize=8.5)
        ax.margins(y=0.15)

    axes[0].set_ylabel("Frequência (n)")
    sns.despine()
    fig.suptitle("Distribuição das Variáveis Discretizadas (Histogramas)", fontweight="bold")


def build_gof_summary_df(results, alpha=0.05):
    rows = []
    for name, dist_name, params, observed, expected, chi2_stat, crit_val, dof, p_val in results:
        rows.append(
            {
                "Variable": name,
                "Distribution": dist_name,
                "Param 1 (mu / mu_ln)": round(float(params[0]), 4),
                "Param 2 (sigma / sigma_ln)": round(float(params[1]), 4),
                "Observed": [round(float(x), 2) for x in observed],
                "Expected": [round(float(x), 2) for x in expected],
                "Diff": [round(float(x), 2) for x in (observed - expected)],
                "Chi2": round(float(chi2_stat), 4),
                "Critical": round(float(crit_val), 4),
                "DoF": int(dof),
                "p-value": round(float(p_val), 4),
                "Result": "Reject H0" if p_val < alpha else "Fail to reject H0",
            }
        )
    return pd.DataFrame(rows)


def plot_observed_vs_expected(plots_data):
    fig, axes = plt.subplots(1, len(plots_data), figsize=(18, 4.5), constrained_layout=True)

    for ax, (title, labels, observed, expected) in zip(axes, plots_data):
        x = np.arange(len(labels))
        width = 0.38

        bars_obs = ax.bar(x - width / 2, observed, width, label="Observado", color="#0F4C81")
        bars_exp = ax.bar(x + width / 2, expected, width, label="Esperado", color="#C84B31")

        ax.set(title=title, xticks=x, xticklabels=labels)
        ax.tick_params(axis="x", rotation=25)
        plt.setp(ax.get_xticklabels(), ha="right")
        ax.bar_label(bars_obs, padding=3, fontsize=8)
        ax.bar_label(bars_exp, fmt="%.1f", padding=3, fontsize=8)
        ax.margins(y=0.18)

    axes[0].set_ylabel("Frequência (n)")
    axes[-1].legend(frameon=False)
    sns.despine()
    fig.suptitle("Comparação entre Frequências Observadas e Esperadas", fontweight="bold")
