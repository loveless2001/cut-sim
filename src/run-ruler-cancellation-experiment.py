"""Driver: full ruler-cancellation experiment per spec.md.

Sweeps coupling anisotropy r = Jx/Jy and the tuning parameter eps (impurity binding
strength -> rod size xi; xi -> infinity is the approach to the continuum/Gaussian RG
fixed point, i.e. 'criticality' for this free theory). For each point it records:
  A_god, A_endo(front signal), A_endo(wavepacket signal), dimensionless battery,
plus the god's-eye calibration gate for the battery.

Run:  .venv/bin/python3 src/run-ruler-cancellation-experiment.py
Outputs: results/results.json, results/*.png
"""
import importlib.util, json, pathlib, sys, time
import numpy as np

SRC = pathlib.Path(__file__).parent
ROOT = SRC.parent
RESULTS = ROOT / "results"


def _load(fname, modname):
    """Bootstrap loader for kebab-case module files (not natively importable)."""
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, SRC / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


lm = _load("lattice-model-exact-fft-evolution.py", "lattice_model")
ge = _load("gods-eye-cone-velocity-measurement.py", "gods_eye")
eo = _load("endogenous-observer-rods-clock.py", "endogenous_observer")
bt = _load("dimensionless-anisotropy-detection-battery.py", "battery")

RATIOS = [1.0, 1.25, 1.5, 2.0, 3.0]
EPS_SWEEP = [12.0, 8.0, 6.0, 4.0, 3.0, 2.5, 2.0, 1.75, 1.5]
L_CONE, L_PROP, L_ROD = 1024, 512, 1024  # cone / calibration / bound-state lattices
#                                          (endogenous wavepacket L adapts per point)


def classify(A, sigma_A, A_god):
    """Pre-registered verdict rules (fixed in plan.md before any run)."""
    if abs(A - 1.0) < 0.02 and abs(A - 1.0) < abs(A_god - 1.0) / 5.0:
        return "CANCELLED"
    if abs(A - 1.0) > max(0.02, 5.0 * sigma_A):
        return "DETECTED"
    return "APPROXIMATE"


def run_ratio(r, keep_snapshot):
    Jx, Jy = r, 1.0
    rec = {"r": r, "Jx": Jx, "Jy": Jy}
    cone = ge.measure_cone(L_CONE, Jx, Jy, snapshot=keep_snapshot)
    snapshot = cone.pop("snapshot", None)
    rec["gods_eye"] = cone

    # god's-eye reference wavepacket (fixed k, fixed width — external units) used
    # only for the battery calibration gate
    vwx, svwx = eo.wavepacket_com_velocity(L_PROP, Jx, Jy, 0, 0.5, 8.0)
    vwy, svwy = eo.wavepacket_com_velocity(L_PROP, Jx, Jy, 1, 0.5, 8.0)
    rec["calibration"] = bt.calibrate_battery(
        512, Jx, Jy, cone["vx"], cone["vy"], cone["sigma_vx"], cone["sigma_vy"],
        vwx, vwy, svwx, svwy)

    rec["sweep"] = []
    for eps in EPS_SWEEP:
        obs = eo.make_observer(Jx, Jy, eps, L_rod=L_ROD)
        wp = eo.endogenous_wavepacket_speeds(Jx, Jy, obs)
        # spreading test needs to hold the grown packet: widths 3*rod, growing ~sqrt(2)
        w0max = 3.0 * max(obs["rod_x"], obs["rod_y"])
        L_spread = eo.pick_lattice_size(4.5 * w0max)
        if wp is None or L_spread is None:
            print(f"  r={r} eps={eps:5.2f} xi={obs['xi']:6.2f} SKIPPED "
                  f"(rod too large for L_max lattice)", flush=True)
            rec["sweep"].append({"eps": eps, "observer": obs, "skipped": True})
            continue
        front = eo.speeds_in_rods_per_tick(
            cone["vx"], cone["vy"], cone["sigma_vx"], cone["sigma_vy"], obs)
        wpk = eo.speeds_in_rods_per_tick(
            wp["x"]["v_sites_per_time"], wp["y"]["v_sites_per_time"],
            wp["x"]["sigma_v"], wp["y"]["sigma_v"], obs)
        battery = {
            "front": bt.front_ratio_test(
                cone["vx"], cone["vy"], cone["sigma_vx"], cone["sigma_vy"],
                obs["rod_x"], obs["rod_y"], obs["sigma_rod_rel"]),
            "wavepacket": bt.wavepacket_ratio_test(
                wp["x"]["v_sites_per_time"], wp["y"]["v_sites_per_time"],
                wp["x"]["sigma_v"], wp["y"]["sigma_v"],
                obs["rod_x"], obs["rod_y"], obs["sigma_rod_rel"]),
            "spreading": bt.spreading_test(
                L_spread, Jx, Jy, obs["rod_x"], obs["rod_y"],
                sigma_rod_rel=obs["sigma_rod_rel"]),
        }
        rec["sweep"].append({
            "eps": eps, "observer": obs, "wavepacket_raw": wp,
            "A_endo_front": front, "A_endo_wavepacket": wpk,
            "battery": battery,
            "class_front": classify(front["A_endo"], front["sigma_A_endo"], cone["A_god"]),
            "class_wavepacket": classify(wpk["A_endo"], wpk["sigma_A_endo"], cone["A_god"]),
            "battery_any_detected": any(t["detected"] for t in battery.values()),
        })
        s = rec["sweep"][-1]
        print(f"  r={r} eps={eps:5.2f} xi={obs['xi']:6.2f} "
              f"rods=({obs['rod_x']:.3f},{obs['rod_y']:.3f}) "
              f"A_god={cone['A_god']:.4f} "
              f"A_front={front['A_endo']:.4f}[{s['class_front']}] "
              f"A_wp={wpk['A_endo']:.4f}[{s['class_wavepacket']}] "
              f"battery_detected={s['battery_any_detected']}", flush=True)
    return rec, snapshot


def to_jsonable(o):
    if isinstance(o, dict):
        return {k: to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o


def main():
    RESULTS.mkdir(exist_ok=True)
    t0 = time.time()
    all_recs, snap = [], None
    for r in RATIOS:
        print(f"=== coupling ratio r = Jx/Jy = {r} ===", flush=True)
        rec, s = run_ratio(r, keep_snapshot=(r == 2.0))
        if s is not None:
            snap = {"P": s, "t": rec["gods_eye"]["snapshot_t"], "r": r,
                    "vx": rec["gods_eye"]["vx"], "vy": rec["gods_eye"]["vy"]}
        cal = rec["calibration"]["calibration_pass"]
        print(f"  battery calibration gate (god's-eye units): "
              f"{'PASS' if cal else 'FAIL'}", flush=True)
        all_recs.append(rec)

    if snap is not None:
        np.savez_compressed(RESULTS / "cone-snapshot-r2.npz", **snap)
    with open(RESULTS / "results.json", "w") as f:
        json.dump(to_jsonable({"ratios": all_recs,
                               "params": {"L_prop": L_PROP, "L_rod": L_ROD,
                                          "eps_sweep": EPS_SWEEP}}), f, indent=1)

    rp = _load("generate-result-plots.py", "result_plots")
    rp.make_all_plots(all_recs, snap, RESULTS)
    print(f"done in {time.time()-t0:.1f}s -> {RESULTS}", flush=True)


if __name__ == "__main__":
    main()
