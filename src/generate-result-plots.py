"""Plots for the ruler-cancellation experiment (loaded by the driver as result_plots).

1. cone-plot-gods-eye.png      — elliptical LR cone heatmap (visual anisotropy proof)
2. anisotropy-vs-coupling-ratio.png — A_god, A_endo(front), A_endo(wavepacket) vs r
3. tuning-sweep-r2.png         — A_endo vs rod size xi at r=2 (the RG curve)
4. rod-ratio-vs-xi.png         — rod_x/rod_y vs xi against the sqrt(Jx/Jy) prediction
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_cone(snap, outdir):
    P, t, r = snap["P"], float(snap["t"]), float(snap["r"])
    L = P.shape[0]
    ext = [-L // 2, L // 2, -L // 2, L // 2]
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    im = ax.imshow(np.log10(P.T + 1e-30), origin="lower", extent=ext,
                   cmap="magma", vmin=-14, vmax=-2)
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(float(snap["vx"]) * t * np.cos(th), float(snap["vy"]) * t * np.sin(th),
            "c--", lw=1.2, label=r"fitted front ellipse $v_d t$")
    ax.set(xlabel="x (sites)", ylabel="y (sites)",
           title=f"God's-eye Lieb-Robinson cone, $J_x/J_y$={r:g}, t={t:.1f}")
    ax.legend(loc="upper right", fontsize=8)
    fig.colorbar(im, ax=ax, label=r"$\log_{10} |\psi|^2$")
    fig.tight_layout()
    fig.savefig(outdir / "cone-plot-gods-eye.png", dpi=150)
    plt.close(fig)


def _valid_sweep(rec):
    return [s for s in rec["sweep"] if not s.get("skipped")]


def _largest_xi_point(rec):
    return max(_valid_sweep(rec), key=lambda s: s["observer"]["xi"])


def plot_vs_ratio(recs, outdir):
    r = np.array([rec["r"] for rec in recs])
    Ag = np.array([rec["gods_eye"]["A_god"] for rec in recs])
    Af = np.array([_largest_xi_point(rec)["A_endo_front"]["A_endo"] for rec in recs])
    Aw = np.array([_largest_xi_point(rec)["A_endo_wavepacket"]["A_endo"] for rec in recs])
    sAf = np.array([_largest_xi_point(rec)["A_endo_front"]["sigma_A_endo"] for rec in recs])
    sAw = np.array([_largest_xi_point(rec)["A_endo_wavepacket"]["sigma_A_endo"] for rec in recs])
    xs = np.linspace(1, r.max(), 100)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot(xs, xs, "k:", lw=1, label=r"$A=r$ (god's eye)")
    ax.plot(xs, np.sqrt(xs), "b:", lw=1, label=r"$A=\sqrt{r}$")
    ax.axhline(1.0, color="g", ls=":", lw=1, label=r"$A=1$ (cancellation)")
    ax.errorbar(r, Ag, fmt="ks", label=r"$A_{god}$ (measured)")
    ax.errorbar(r, Af, yerr=sAf, fmt="bo", label=r"$A_{endo}$ front signal")
    ax.errorbar(r, Aw, yerr=sAw, fmt="g^", label=r"$A_{endo}$ wavepacket signal")
    ax.set(xlabel=r"coupling ratio $r=J_x/J_y$", ylabel="anisotropy ratio",
           title="External vs endogenous rulers (at largest rod)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "anisotropy-vs-coupling-ratio.png", dpi=150)
    plt.close(fig)


def plot_tuning_sweep(recs, outdir, r_target=2.0):
    rec = next(rec for rec in recs if rec["r"] == r_target)
    sweep = _valid_sweep(rec)
    xi = np.array([s["observer"]["xi"] for s in sweep])
    Af = np.array([s["A_endo_front"]["A_endo"] for s in sweep])
    Aw = np.array([s["A_endo_wavepacket"]["A_endo"] for s in sweep])
    sAf = np.array([s["A_endo_front"]["sigma_A_endo"] for s in sweep])
    sAw = np.array([s["A_endo_wavepacket"]["sigma_A_endo"] for s in sweep])
    Ag = rec["gods_eye"]["A_god"]
    o = np.argsort(xi)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.axhline(Ag, color="k", ls=":", lw=1, label=r"$A_{god}$")
    ax.axhline(np.sqrt(Ag), color="b", ls=":", lw=1, label=r"$\sqrt{A_{god}}$")
    ax.axhline(1.0, color="g", ls=":", lw=1, label="perfect cancellation")
    ax.errorbar(xi[o], Af[o], yerr=sAf[o], fmt="bo-", lw=1, label=r"$A_{endo}$ front")
    ax.errorbar(xi[o], Aw[o], yerr=sAw[o], fmt="g^-", lw=1, label=r"$A_{endo}$ wavepacket")
    ax.set_xscale("log")
    ax.set(xlabel=r"rod size $\xi$ (sites)  —  $\xi\to\infty$ = toward continuum fixed point",
           ylabel="endogenous anisotropy ratio",
           title=rf"Tuning sweep at $J_x/J_y={r_target:g}$ (lattice scale $\to$ fixed point)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "tuning-sweep-r2.png", dpi=150)
    plt.close(fig)


def plot_rod_ratio(recs, outdir):
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    for rec in recs:
        sweep = _valid_sweep(rec)
        xi = np.array([s["observer"]["xi"] for s in sweep])
        rr = np.array([s["observer"]["rod_x"] / s["observer"]["rod_y"]
                       for s in sweep])
        o = np.argsort(xi)
        (line,) = ax.plot(xi[o], rr[o], "o-", lw=1, ms=4, label=f"r={rec['r']:g}")
        ax.axhline(np.sqrt(rec["r"]), color=line.get_color(), ls=":", lw=0.8)
    ax.set_xscale("log")
    ax.set(xlabel=r"rod size $\xi$ (sites)", ylabel=r"rod$_x$ / rod$_y$",
           title=r"Rod anisotropy vs continuum prediction $\sqrt{J_x/J_y}$ (dotted)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "rod-ratio-vs-xi.png", dpi=150)
    plt.close(fig)


def make_all_plots(recs, snap, outdir):
    if snap is not None:
        plot_cone(snap, outdir)
    plot_vs_ratio(recs, outdir)
    plot_tuning_sweep(recs, outdir)
    plot_rod_ratio(recs, outdir)
