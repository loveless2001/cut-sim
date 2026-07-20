"""Result plots for the orientation-gauge experiment (called by the driver).

  orientation-null-and-crossover.png   g=0 nulls + log-log D(g) crossover, both axes
  gods-eye-fires-internal-null.png     MI(t) splits O+/O- while internal S_A(t) overlaps
  quench-arrow-traversable-split.png   S_A(t) all variants, g=0 (collapse) vs 0.1 (split)
  null-robustness-sweep.png            D_internal at g=0 and g=0.1 across N and beta
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TOL_NULL, THETA_FIRE = 1e-9, 1e-6
CC = (256, 1.0)


def _sweep(recs):
    return sorted([r for r in recs if (r["N"], r["beta"]) == CC], key=lambda r: r["g"])


def plot_null_and_crossover(recs, out):
    sweep = _sweep(recs)
    fig, axg = plt.subplots(2, 2, figsize=(12, 8))
    for row, axis in enumerate(("orientation-mirror", "purification")):
        items = sweep[0]["internal"][axis]["items"]
        names = list(items.keys())
        ax = axg[row, 0]
        vals = [max(sweep[0]["internal"][axis]["items"][k], 1e-18) for k in names]
        ax.bar(range(len(names)), vals, color="#4878a8")
        ax.set_yscale("log")
        ax.axhline(TOL_NULL, color="crimson", ls="--", lw=1, label="null tolerance 1e-9")
        ax.axhline(THETA_FIRE, color="darkorange", ls=":", lw=1, label="fire threshold")
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
        ax.set_ylabel(f"{axis}\nitem distance at g=0")
        ax.legend(fontsize=7)
        ax = axg[row, 1]
        gs = [r["g"] for r in sweep if r["g"] > 0]
        for k in names:
            ax.plot(gs, [max(r["internal"][axis]["items"][k], 1e-18)
                         for r in sweep if r["g"] > 0], "o-", lw=1, ms=3, label=k)
        ax.plot(gs, [r["internal"][axis]["D"] for r in sweep if r["g"] > 0],
                "ks-", lw=2.5, ms=5, label="D_internal")
        ax.axhline(THETA_FIRE, color="darkorange", ls=":", lw=1)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("coupling g / J"); ax.set_ylabel("distance")
        ax.legend(fontsize=6, ncol=2)
    axg[0, 0].set_title(f"internal battery nulls at g=0 (N={CC[0]}, beta={CC[1]})")
    axg[0, 1].set_title("crossover: orientation becomes physical as the cut opens")
    fig.tight_layout()
    fig.savefig(out / "orientation-null-and-crossover.png", dpi=150)
    plt.close(fig)


def plot_godseye_vs_internal(recs, out):
    r0 = next(r for r in _sweep(recs) if r["g"] == 0.0)
    cv = r0["curves"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    t = cv["mi_times"]
    a1.plot(t, cv["mi_Oplus"], lw=1.6, label="O+ (both times forward)")
    a1.plot(t, cv["mi_Ominus"], lw=1.6, ls="--", label="O- (L time reversed)")
    a1.set_xlabel("t (bare units, J=1)"); a1.set_ylabel("I(L_w : R_w)  [nats]")
    a1.set_title("God's-eye: two-sided MI fires at g=0")
    a1.legend(fontsize=8)
    tt = np.arange(25) / 8.0
    for k, ls in (("O+mirror", "-"), ("O-mirror", "--")):
        a2.plot(tt, cv["quench_SA_V3"][k], ls, lw=1.6, label=k)
    a2.set_xlabel("t (ticks of the R clock)"); a2.set_ylabel("S_A(t)  [nats]")
    a2.set_title("Internal: quench entropy identical at g=0 (curves overlap)")
    a2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "gods-eye-fires-internal-null.png", dpi=150)
    plt.close(fig)


def plot_quench_split(recs, out):
    rs = {r["g"]: r for r in _sweep(recs) if "curves" in r}
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    tt = np.arange(25) / 8.0
    for ax, g in zip(axs, (0.0, 0.1)):
        cv = rs[g]["curves"]
        for k, ls in (("O+mirror", "-"), ("O-mirror", "--"),
                      ("O+scrambled", "-."), ("O-scrambled", ":")):
            ax.plot(tt, cv["quench_SA_V3"][k], ls, lw=1.5, label=k)
        ax.set_title(f"g = {g:g} J" + ("  (all four collapse)" if g == 0 else
                                       "  (traversable cut: variants split)"))
        ax.set_xlabel("t (ticks)")
        ax.legend(fontsize=7)
    axs[0].set_ylabel("S_A(t)  [nats]")
    fig.tight_layout()
    fig.savefig(out / "quench-arrow-traversable-split.png", dpi=150)
    plt.close(fig)


def plot_robustness(recs, out):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for axis, marker, color in (("orientation-mirror", "o", "#4878a8"),
                                ("purification", "s", "#a85478")):
        for g, alpha in ((0.0, 1.0), (0.1, 0.35)):
            pts = [(f"N={r['N']}\nb={r['beta']:g}", r["internal"][axis]["D"])
                   for r in recs if r["g"] == g]
            if pts:
                xs, ys = zip(*pts)
                ax.scatter(xs, [max(y, 1e-18) for y in ys], marker=marker, s=45,
                           alpha=alpha, color=color,
                           label=f"{axis}, g={g:g}")
    ax.set_yscale("log")
    ax.axhline(TOL_NULL, color="crimson", ls="--", lw=1)
    ax.axhline(THETA_FIRE, color="darkorange", ls=":", lw=1)
    ax.set_ylabel("D_internal")
    ax.set_title("null (g=0) vs traversable control (g=0.1) across the sweep")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "null-robustness-sweep.png", dpi=150)
    plt.close(fig)


def make_all_plots(recs, verdict, out):
    plot_null_and_crossover(recs, out)
    plot_godseye_vs_internal(recs, out)
    plot_quench_split(recs, out)
    plot_robustness(recs, out)
