"""Standalone figures for the measured follow-up, without changing the old web data."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def make_plots(crossover, pairs, trials, spreading, output):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    ax = axes[0, 0]
    rows = [r for r in crossover["records"] if (r["N"], r["beta"], r["seed"]) == (256, 1., 20260720)
            and r["g"] > 0]
    for key, label in (("orientation", "Original battery: orientation"),
                       ("purification", "Original battery: purification")):
        ax.loglog([r["g"] for r in rows], [r[key]["D"] for r in rows], "o-", label=label)
    ax.set(xlabel="Coupling g / J", ylabel="Maximum normalized battery distance",
           title="Denser crossover (N=256, beta=1)")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    for key, label in (("pair_difference_norm", "Pair quadratures (added reference)"),
                       ("normal_difference_norm", "Number-conserving correlation block")):
        rows = [r for r in pairs["records"] if (r["N"], r["beta"], r["duration_ticks"]) == (128, 1., .5)
                and r["g"] > 0]
        ax.loglog([r["g"] for r in rows], [r[key] for r in rows], "o-", label=label)
    ax.set(xlabel="Coupling g / J", ylabel="Absolute correlation difference",
           title="Measurement access changes the leading power")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    for g in (1e-4, 1e-3, 1e-2):
        rows = [r for r in trials["records"] if (r["g"], r["duration_ticks"], r["visibility"],
                r["readout_flip"]) == (g, .5, 1., 0.)]
        ax.semilogx([r["trials"] for r in rows], [r["exact_error"] for r in rows],
                    "o-", label=f"g={g:g}")
    ax.axhline(.5, color="gray", linestyle="--", label="No reference / g=0")
    ax.set(xlabel="Fresh trials (reference renewed each trial)", ylabel="Equal-prior classification error",
           title="Finite reference, half-tick observation", ylim=(-.02, .53))
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    for rec in spreading["records"]:
        for refined, style in ((False, "--"), (True, "-")):
            rows = [r for r in rec["packet_checks"] if r["rod_definition"] == "refined_rods"
                    and r["samples"] == 40 and r["refined"] == refined]
            ax.semilogx([r["L"] for r in rows], [r["R"]-1 for r in rows], "o"+style,
                        label=f"r={rec['r']:g}, {'refined stop' if refined else '40-point stop'}")
    ax.axhline(0, color="gray", linewidth=.7)
    ax.set(xlabel="Packet lattice size L", ylabel="Spreading ratio minus one",
           title="Fixed apparatus, converged rods")
    ax.legend(fontsize=8)
    for ax in axes.flat:
        ax.grid(True, alpha=.2)
    fig.savefig(output / "followup-summary.png", dpi=180)
    fig.savefig(output / "followup-summary.svg")
    plt.close(fig)
