"""Driver: full orientation-gauge experiment per orientation-test.md.

Runs gates G0-G9 first (hard exit on failure), then sweeps
  (N=256, beta in {1,4}) x g in {0, 1e-3, 1e-2, 1e-1}      [g-crossover]
  (N in {64,128,512}, beta=1) x g in {0, 0.1}              [null + control vs size]
  (N=256, beta=0.5, g=0)                                   [extra null point]
computing the internal battery for the four variants {O+,O-} x {mirror, scrambled},
the god's-eye discriminators, and the pre-registered distances. The O- battery is
additionally recomputed through Theta_L Impl B at N=256, beta=1 (verdicts must agree).

Run:  .venv/bin/python3 src/run-orientation-gauge-experiment.py
Outputs: results/results-orientation.json, results/*.png
"""
import importlib.util, json, pathlib, sys, time
import numpy as np

SRC = pathlib.Path(__file__).parent
RESULTS = SRC.parent / "results"


def _load(fname, modname):
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, SRC / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


ts = _load("tfd-gaussian-state-construction.py", "tfd_state")
oe = _load("orientation-flip-evolution.py", "orientation_evolution")
bt = _load("internal-battery-side-r.py", "internal_battery")
ge = _load("gods-eye-discriminators.py", "gods_eye")

G_SWEEP = [0.0, 1e-3, 1e-2, 1e-1]
COMBOS = ([(256, 1.0, G_SWEEP), (256, 4.0, G_SWEEP)]
          + [(n, 1.0, [0.0, 0.1]) for n in (64, 128, 512)]
          + [(256, 0.5, [0.0])])
QUENCH_VS = (1.0, 3.0)
TOL_NULL = 1e-9
CURVE_COMBO = (256, 1.0)          # combo whose curves are stored for plots/web


def classify_verdict(null_distance, controls_ok, tol=TOL_NULL):
    """Apply the pre-registered verdict order.

    A dead calibration/positive control voids the test, even if a g=0 distance is large.
    """
    if not controls_ok:
        return "INCONCLUSIVE"
    return "HOLDS" if null_distance < tol else "FALSIFIED"


def run_variant(N, state, s, g, rod, cls=oe.VariantEvolution):
    """Build the three protocols for one variant and compute its battery."""
    mk = lambda **kw: oe.build_variant_h1(N, s, g, **kw)
    evo_main = cls(mk(), state["G"], state["F"])
    evo_qs = {V: cls(mk(quench=(N // 2, V)), state["G"], state["F"])
              for V in QUENCH_VS}
    Gk, Fk = bt.apply_clock_kick(state["G"], state["F"], N)
    evo_clk = cls(mk(carve=True), Gk, Fk)
    items, meta = bt.compute_internal_items(evo_main, evo_qs, evo_clk, N, rod)
    quench_curves = {V: items[f"quench-arrow-V{V}"] for V in QUENCH_VS}
    return evo_main, items, meta, quench_curves


def run_combo(N, beta, gs, rod):
    st = ts.build_tfd(N, beta)
    scr = ts.scramble_l_sector(st)
    ge_comp = ge.complement_discriminator(st, scr)
    recs = []
    for g in gs:
        t0 = time.time()
        data = {}
        for s, comp, state in ((+1, "mirror", st), (-1, "mirror", st),
                               (+1, "scrambled", scr), (-1, "scrambled", scr)):
            evo, items, meta, qc = run_variant(N, state, s, g, rod)
            key = f"O{'+' if s > 0 else '-'}{comp}"
            data[key] = {"items": items, "meta": meta, "qcurves": qc,
                         "evo": evo if comp == "mirror" else None}

        axes = {}
        for name, (a, b) in {
            "orientation-mirror": ("O+mirror", "O-mirror"),
            "orientation-scrambled": ("O+scrambled", "O-scrambled"),
            "purification": ("O+mirror", "O+scrambled"),
            "purification-Ominus": ("O-mirror", "O-scrambled"),
        }.items():
            d, D = bt.battery_distances(data[a]["items"], data[b]["items"])
            axes[name] = {"items": d, "D": D}

        disc = ge.orientation_discriminators(data["O+mirror"]["evo"],
                                             data["O-mirror"]["evo"], N)
        disc["ge-complement"] = ge_comp

        rec = {"N": N, "beta": beta, "g": g, "rod": rod, "internal": axes,
               "gods_eye": {k: v["d"] for k, v in disc.items()},
               "ge_fires": {k: bool(v["fires"]) for k, v in disc.items()},
               "meta": {k: v["meta"] for k, v in data.items()}}

        if (N, beta) == CURVE_COMBO and g in (0.0, 0.1):
            rec["curves"] = {
                "mi_times": ge.GE_TIMES.tolist(),
                "mi_Oplus": ge.mutual_information_curve(data["O+mirror"]["evo"], N).tolist(),
                "mi_Ominus": ge.mutual_information_curve(data["O-mirror"]["evo"], N).tolist(),
                "quench_SA_V3": {k: v["qcurves"][3.0].tolist() for k, v in data.items()},
                "ticks": {k: v["meta"]["tick"] for k, v in data.items()},
            }
            # Theta_L Impl-B battery for O- : verdicts must match Impl A
            _, items_b, _, _ = run_variant(N, st, -1, g, rod, cls=oe.ImplBEvolution)
            d_b, D_b = bt.battery_distances(data["O+mirror"]["items"], items_b)
            d_a = axes["orientation-mirror"]["items"]
            rec["impl_b_check"] = {
                "items": d_b, "D": D_b,
                "max_item_discrepancy": max(abs(d_a[k] - d_b[k]) for k in d_a),
                "null_verdict_agrees": bool((D_b < TOL_NULL) ==
                                            (axes["orientation-mirror"]["D"] < TOL_NULL)),
            }
        print(f"  N={N} beta={beta} g={g:g}: "
              f"D_or={axes['orientation-mirror']['D']:.2e} "
              f"D_pu={axes['purification']['D']:.2e} "
              f"ge={[f'{v:.1e}' for v in rec['gods_eye'].values()]} "
              f"({time.time() - t0:.1f}s)", flush=True)
        recs.append(rec)
    return recs


def crossover_summary(recs):
    """Smallest firing g per item + small-g slope, from the (256, 1.0) g-sweep."""
    sweep = sorted([r for r in recs if (r["N"], r["beta"]) == CURVE_COMBO],
                   key=lambda r: r["g"])
    out = {}
    for axis in ("orientation-mirror", "purification"):
        item_names = sweep[0]["internal"][axis]["items"].keys()
        first_fire = {}
        for k in item_names:
            fired = [r["g"] for r in sweep if r["g"] > 0
                     and r["internal"][axis]["items"][k] > ge.THETA_FIRE]
            first_fire[k] = min(fired) if fired else None
        positive = [(r["g"], r["internal"][axis]["D"]) for r in sweep if r["g"] > 0]
        gpos = [g for g, _ in positive]
        Dpos = [D for _, D in positive]
        all_slope = float(np.polyfit(np.log(gpos), np.log(Dpos), 1)[0])
        smallg_slope = float(np.log(Dpos[1] / Dpos[0]) / np.log(gpos[1] / gpos[0]))
        out[axis] = {"first_firing_g": first_fire, "smallg_slope_D": smallg_slope,
                     "all_nonzero_slope_D": all_slope,
                     "smallg_slope_window": [gpos[0], gpos[1]],
                     "D_vs_g": dict(zip(map(str, gpos), Dpos))}
    return out


def main():
    print("=== pre-registered gates (must all pass) ===", flush=True)
    va = _load("validate-orientation-gates.py", "validate_gates")
    if va.main():
        print("GATES FAILED — experiment aborted (INCONCLUSIVE by rule).", flush=True)
        sys.exit(1)

    RESULTS.mkdir(exist_ok=True)
    t0 = time.time()
    rod = bt.rod_length()
    print(f"\n=== sweep (rod = {rod:.3f} sites) ===", flush=True)
    recs = []
    for N, beta, gs in COMBOS:
        recs.extend(run_combo(N, beta, gs, rod))

    nulls = [r for r in recs if r["g"] == 0.0]
    D72a = max(r["internal"]["orientation-mirror"]["D"] for r in nulls)
    D72a_scr = max(r["internal"]["orientation-scrambled"]["D"] for r in nulls)
    D72b = max(r["internal"]["purification"]["D"] for r in nulls)
    ge_orientation_ok = all(r["ge_fires"]["ge-mi"] and r["ge_fires"]["ge-cross-phase"]
                            for r in nulls)
    ge_complement_ok = all(r["ge_fires"]["ge-complement"] for r in nulls)
    ge_ok = ge_orientation_ok and ge_complement_ok
    implb = [r["impl_b_check"] for r in recs if "impl_b_check" in r]
    implb_ok = bool(implb) and all(c["null_verdict_agrees"] for c in implb)
    control_rows = [r for r in recs if r["g"] == 0.1]
    positive_controls_ok = bool(control_rows) and all(
        all(v > ge.THETA_FIRE for v in r["internal"]["orientation-mirror"]["items"].values())
        and all(v > ge.THETA_FIRE for v in r["internal"]["purification"]["items"].values())
        for r in control_rows)
    controls72a = ge_orientation_ok and positive_controls_ok and implb_ok
    controls72b = ge_complement_ok and positive_controls_ok

    verdict = {
        "P7.2a": classify_verdict(D72a, controls72a),
        "P7.2b": classify_verdict(D72b, controls72b),
        "D_internal_max_orientation_g0": D72a,
        "D_internal_max_orientation_scrambled_g0": D72a_scr,
        "D_internal_max_purification_g0": D72b,
        "gods_eye_all_fire": ge_ok, "gates_all_pass": True,
        "gods_eye_orientation_fire": ge_orientation_ok,
        "gods_eye_complement_fire": ge_complement_ok,
        "positive_controls_fire": positive_controls_ok,
        "theta_impl_AB_verdicts_agree": implb_ok,
        "tolerance_null": TOL_NULL, "theta_fire": ge.THETA_FIRE,
        "crossover": crossover_summary(recs),
        "note": "P7.2b at g=0 is a theorem (all R-observables are functionals of "
                "rho_R); this run demonstrates the machinery realizes it.",
    }
    print(f"\nVERDICT: P7.2a {verdict['P7.2a']} (D={D72a:.2e}), "
          f"P7.2b {verdict['P7.2b']} (D={D72b:.2e}), ge_fire={ge_ok}", flush=True)

    def to_jsonable(o):
        if isinstance(o, dict):
            return {str(k): to_jsonable(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [to_jsonable(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    slim = [{k: v for k, v in r.items() if k != "meta"} | {"meta": r["meta"]}
            for r in recs]
    for r in slim:                       # strip non-serializable evo refs if any leaked
        r.pop("evo", None)
    payload = to_jsonable({
        "spec": "orientation-test.md", "plan": "plans/260720-2257-orientation-gauge-sim",
        "params": {"g_sweep": G_SWEEP, "quench_Vs": list(QUENCH_VS),
                   "combos": [(n, b, list(g)) for n, b, g in COMBOS],
                   "rod_eps0": bt.ROD_EPS0, "clock_kick_theta": bt.CLOCK_KICK_THETA,
                   "scramble_seed": ts.SCRAMBLE_SEED},
        "records": slim, "verdict": verdict})
    with open(RESULTS / "results-orientation.json", "w") as f:
        json.dump(payload, f, indent=1)

    rp = _load("generate-orientation-plots.py", "orientation_plots")
    rp.make_all_plots(recs, verdict, RESULTS)
    print(f"done in {time.time() - t0:.1f}s -> {RESULTS}", flush=True)


if __name__ == "__main__":
    main()
