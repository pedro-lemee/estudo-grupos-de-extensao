"""Shared inferential helpers: effect sizes, post-hoc tests and bootstrap intervals.

All functions return plain dicts / DataFrames so notebooks can format them in PT-BR.
"""

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

DEFAULT_ALPHA = 0.05
DEFAULT_N_BOOT = 5000
DEFAULT_SEED = 42


# ---------------------------------------------------------------------------
# Paired comparisons
# ---------------------------------------------------------------------------
def paired_comparison(x, y, n_boot=DEFAULT_N_BOOT, seed=DEFAULT_SEED, alternative="two-sided") -> dict:
    """Compare paired samples x and y with Wilcoxon, sign test and paired t-test (two-sided by default).

    Returns the descriptive summary of d = x - y plus the three tests and their effect sizes:
    matched-pairs rank-biserial correlation (Wilcoxon), proportion of positive non-zero
    differences (sign test) and Cohen's d_z (paired t-test).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    d = x - y
    n = d.size
    nonzero = d[d != 0]
    n_pos, n_neg, n_zero = int((d > 0).sum()), int((d < 0).sum()), int((d == 0).sum())

    # Wilcoxon signed-rank ("wilcox": zero differences are discarded; "pratt" is reported as robustness)
    w_wilcox = stats.wilcoxon(x, y, zero_method="wilcox", alternative=alternative, method="approx")
    w_pratt = stats.wilcoxon(x, y, zero_method="pratt", alternative=alternative, method="approx")
    ranks = stats.rankdata(np.abs(nonzero))
    w_plus, w_minus = ranks[nonzero > 0].sum(), ranks[nonzero < 0].sum()
    rank_biserial = (w_plus - w_minus) / (w_plus + w_minus)

    # Exact sign test on non-zero differences
    sign = stats.binomtest(n_pos, n_pos + n_neg, p=0.5, alternative=alternative)

    # Paired t-test (robustness: Likert differences treated as interval)
    t_res = stats.ttest_rel(x, y, alternative=alternative)
    dz = d.mean() / d.std(ddof=1)
    t_crit = stats.t.ppf(0.975, n - 1)  # the reported CI is always two-sided 95%, whatever `alternative` is
    se = d.std(ddof=1) / np.sqrt(n)

    boot_mean = stats.bootstrap(
        (d,), np.mean, n_resamples=n_boot, confidence_level=0.95, method="BCa", random_state=seed
    ).confidence_interval

    return {
        "n": n,
        "n_positive": n_pos,
        "n_zero": n_zero,
        "n_negative": n_neg,
        "mean_diff": d.mean(),
        "median_diff": np.median(d),
        "mean_diff_ci95_t": (d.mean() - t_crit * se, d.mean() + t_crit * se),
        "mean_diff_ci95_boot": (boot_mean.low, boot_mean.high),
        "wilcoxon_W": w_wilcox.statistic,
        "wilcoxon_p": w_wilcox.pvalue,
        "wilcoxon_pratt_p": w_pratt.pvalue,
        "rank_biserial": rank_biserial,
        "sign_test_p": sign.pvalue,
        "prop_positive_nonzero": n_pos / (n_pos + n_neg),
        "t_stat": t_res.statistic,
        "t_df": n - 1,
        "t_p": t_res.pvalue,
        "cohen_dz": dz,
    }


# ---------------------------------------------------------------------------
# k independent groups
# ---------------------------------------------------------------------------
def kruskal_with_effect(df: pd.DataFrame, value: str, group: str) -> dict:
    """Kruskal-Wallis H test (tie-corrected) with epsilon-squared effect size."""
    data = df[[value, group]].dropna()
    groups = [g[value].to_numpy() for _, g in data.groupby(group, observed=True)]
    h, p = stats.kruskal(*groups)
    n, k = len(data), len(groups)
    epsilon_sq = h * (n + 1) / (n**2 - 1)
    return {"H": h, "df": k - 1, "p": p, "n": n, "k": k, "epsilon_sq": epsilon_sq}


def welch_anova(df: pd.DataFrame, value: str, group: str) -> dict:
    """Welch's one-way ANOVA (does not assume equal variances) with omega-squared from the classic ANOVA."""
    data = df[[value, group]].dropna()
    grouped = [g[value].to_numpy(dtype=float) for _, g in data.groupby(group, observed=True)]
    k = len(grouped)
    n_i = np.array([len(g) for g in grouped])
    m_i = np.array([g.mean() for g in grouped])
    v_i = np.array([g.var(ddof=1) for g in grouped])
    if np.any(v_i == 0):
        raise ValueError("Welch ANOVA is undefined when a group has zero variance")
    w_i = n_i / v_i
    grand = np.sum(w_i * m_i) / np.sum(w_i)
    a = np.sum(w_i * (m_i - grand) ** 2) / (k - 1)
    tmp = np.sum((1 - w_i / w_i.sum()) ** 2 / (n_i - 1))
    b = 1 + 2 * (k - 2) / (k**2 - 1) * tmp
    f_stat = a / b
    df2 = (k**2 - 1) / (3 * tmp)
    p = stats.f.sf(f_stat, k - 1, df2)

    # omega-squared from the standard one-way decomposition
    n = n_i.sum()
    overall = data[value].astype(float).mean()
    ss_between = np.sum(n_i * (m_i - overall) ** 2)
    ss_within = np.sum((n_i - 1) * v_i)
    ms_within = ss_within / (n - k)
    omega_sq = (ss_between - (k - 1) * ms_within) / (ss_between + ss_within + ms_within)
    levene = stats.levene(*grouped, center="median")
    return {
        "F": f_stat,
        "df1": k - 1,
        "df2": df2,
        "p": p,
        "omega_sq": omega_sq,
        "levene_W": levene.statistic,
        "levene_p": levene.pvalue,
    }


def dunn_test(df: pd.DataFrame, value: str, group: str, p_adjust: str = "holm") -> pd.DataFrame:
    """Dunn's pairwise post-hoc test after Kruskal-Wallis, with tie correction and p-value adjustment."""
    data = df[[value, group]].dropna().copy()
    data["rank"] = stats.rankdata(data[value])
    n = len(data)
    _, tie_counts = np.unique(data[value], return_counts=True)
    tie_term = np.sum(tie_counts**3 - tie_counts) / (12 * (n - 1))
    summary = data.groupby(group, observed=True)["rank"].agg(["mean", "size"])

    rows = []
    for g1, g2 in combinations(summary.index, 2):
        r1, n1 = summary.loc[g1]
        r2, n2 = summary.loc[g2]
        se = np.sqrt((n * (n + 1) / 12 - tie_term) * (1 / n1 + 1 / n2))
        z = (r1 - r2) / se
        rows.append({"group_1": g1, "group_2": g2, "z": z, "p_raw": 2 * stats.norm.sf(abs(z))})
    out = pd.DataFrame(rows)
    out["p_adj"] = adjust_pvalues(out["p_raw"].to_numpy(), method=p_adjust)
    return out


def adjust_pvalues(pvalues, method: str = "holm") -> np.ndarray:
    """Holm (FWER) or Benjamini-Hochberg (FDR) adjustment."""
    p = np.asarray(pvalues, dtype=float)
    m = p.size
    order = np.argsort(p)
    adjusted = np.empty(m)
    if method == "holm":
        running = 0.0
        for rank, idx in enumerate(order):
            running = max(running, (m - rank) * p[idx])
            adjusted[idx] = min(1.0, running)
    elif method in ("bh", "fdr_bh"):
        running = 1.0
        for rank in range(m - 1, -1, -1):
            idx = order[rank]
            running = min(running, p[idx] * m / (rank + 1))
            adjusted[idx] = running
    else:
        raise ValueError(f"Unknown p-value adjustment method: {method}")
    return adjusted


# ---------------------------------------------------------------------------
# Association between ordinal variables
# ---------------------------------------------------------------------------
def ordinal_association(x, y, n_boot=DEFAULT_N_BOOT, seed=DEFAULT_SEED) -> dict:
    """Kendall tau-b and Spearman rho (both tie-aware) with bootstrap percentile CIs."""
    data = pd.DataFrame({"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float)}).dropna()
    xv, yv = data["x"].to_numpy(), data["y"].to_numpy()
    tau = stats.kendalltau(xv, yv, variant="b")
    rho = stats.spearmanr(xv, yv)

    rng = np.random.default_rng(seed)
    n = len(xv)
    boot_tau, boot_rho = np.empty(n_boot), np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boot_tau[b] = stats.kendalltau(xv[idx], yv[idx], variant="b").statistic
        boot_rho[b] = stats.spearmanr(xv[idx], yv[idx]).statistic
    return {
        "n": n,
        "kendall_tau_b": tau.statistic,
        "kendall_p": tau.pvalue,
        "kendall_ci95": tuple(np.nanpercentile(boot_tau, [2.5, 97.5])),
        "spearman_rho": rho.statistic,
        "spearman_p": rho.pvalue,
        "spearman_ci95": tuple(np.nanpercentile(boot_rho, [2.5, 97.5])),
    }


# ---------------------------------------------------------------------------
# Bootstrap summaries per group
# ---------------------------------------------------------------------------
def bootstrap_group_means(
    df: pd.DataFrame, value: str, group: str, n_boot=DEFAULT_N_BOOT, seed=DEFAULT_SEED
) -> pd.DataFrame:
    """Mean of `value` per group with a 95% percentile bootstrap CI (resampling within each group)."""
    rng = np.random.default_rng(seed)
    rows = []
    for name, g in df[[value, group]].dropna().groupby(group, observed=True):
        v = g[value].to_numpy(dtype=float)
        boots = rng.choice(v, size=(n_boot, v.size), replace=True).mean(axis=1)
        low, high = np.percentile(boots, [2.5, 97.5])
        rows.append({group: name, "n": v.size, "mean": v.mean(), "median": np.median(v), "ci_low": low, "ci_high": high})
    return pd.DataFrame(rows)


def wilson_interval(successes: int, n: int, confidence: float = 0.95) -> tuple:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (center - half, center + half)


# ---------------------------------------------------------------------------
# Contingency tables
# ---------------------------------------------------------------------------
def chi2_independence(table: pd.DataFrame, n_mc: int = 20000, seed=DEFAULT_SEED) -> dict:
    """Pearson chi-square test of independence, Cramer's V and a Monte Carlo p-value.

    The Monte Carlo p-value (permutation of one margin with fixed margins) is the reliable one when
    more than 20% of the expected counts are below 5.
    """
    observed = table.to_numpy()
    chi2_stat, p, dof, expected = stats.chi2_contingency(observed, correction=False)
    n = observed.sum()
    r, c = observed.shape
    cramer_v = np.sqrt(chi2_stat / (n * (min(r, c) - 1)))

    # Monte Carlo with fixed margins: rebuild individual-level labels and permute one of them
    rows = np.repeat(np.arange(r), observed.sum(axis=1))
    cols = np.concatenate([np.repeat(np.arange(c), observed[i]) for i in range(r)])
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(n_mc):
        perm = rng.permutation(cols)
        sim = np.zeros_like(observed)
        np.add.at(sim, (rows, perm), 1)
        with np.errstate(divide="ignore", invalid="ignore"):
            stat = np.nansum((sim - expected) ** 2 / expected)
        exceed += stat >= chi2_stat - 1e-12
    return {
        "chi2": chi2_stat,
        "df": dof,
        "p_asymptotic": p,
        "p_monte_carlo": (exceed + 1) / (n_mc + 1),
        "cramer_v": cramer_v,
        "share_expected_below_5": float((expected < 5).mean()),
        "min_expected": float(expected.min()),
    }


# ---------------------------------------------------------------------------
# Regression helpers
# ---------------------------------------------------------------------------
def fit_ordinal_logit(y: pd.Series, X: pd.DataFrame):
    """Proportional-odds (cumulative logit) model. Raises if the optimizer did not converge."""
    from statsmodels.miscmodels.ordinal_model import OrderedModel

    model = OrderedModel(y, X.astype(float), distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=20000)
    if not result.mle_retvals.get("converged", False):
        # Polish the BFGS solution with Newton-Raphson before giving up
        result = model.fit(method="newton", start_params=result.params, disp=False, maxiter=200)
    if not result.mle_retvals.get("converged", False):
        raise RuntimeError("Ordinal logit did not converge")
    return result


def ordinal_null_loglik(y: pd.Series) -> float:
    """Log-likelihood of the thresholds-only ordinal model (equals the multinomial of the marginals)."""
    counts = y.value_counts().to_numpy(dtype=float)
    return float(np.sum(counts * np.log(counts / counts.sum())))


def likelihood_ratio_test(llf_full: float, llf_reduced: float, df_diff: int) -> dict:
    stat = 2 * (llf_full - llf_reduced)
    return {"LR": stat, "df": df_diff, "p": stats.chi2.sf(stat, df_diff)}


# ---------------------------------------------------------------------------
# Cross-validation helpers (kept dependency-free on purpose: scikit-learn is not in pyproject.toml)
# ---------------------------------------------------------------------------
def repeated_kfold_indices(y, n_splits=5, n_repeats=20, stratified=True, seed=DEFAULT_SEED):
    """Yield (train_idx, test_idx) for repeated (stratified) K-fold cross-validation."""
    y = np.asarray(y)
    n = y.size
    rng = np.random.default_rng(seed)
    for _ in range(n_repeats):
        fold_of = np.empty(n, dtype=int)
        if stratified:
            for level in np.unique(y):
                idx = rng.permutation(np.flatnonzero(y == level))
                fold_of[idx] = np.arange(idx.size) % n_splits
        else:
            fold_of[rng.permutation(n)] = np.arange(n) % n_splits
        for k in range(n_splits):
            yield np.flatnonzero(fold_of != k), np.flatnonzero(fold_of == k)


def roc_auc(y_true, scores) -> float:
    """Area under the ROC curve via the Mann-Whitney identity (ties count 1/2)."""
    y_true = np.asarray(y_true).astype(bool)
    ranks = stats.rankdata(np.asarray(scores, dtype=float))
    n_pos, n_neg = y_true.sum(), (~y_true).sum()
    if n_pos == 0 or n_neg == 0:
        return np.nan  # AUC is undefined when only one class is present
    return (ranks[y_true].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
