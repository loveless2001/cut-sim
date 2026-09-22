"""Run the bounded follow-up in docs/followup-study-plan.md, preserving old results.

Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 for predictable laptop runtime.
An existing output directory is never overwritten. No original driver main() is run.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def load(file, name):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SRC / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


driver = load("run-orientation-gauge-experiment.py", "orientation_driver")
measure = load("followup-measurements.py", "followup_measurements")
support = driver.support
ts, oe, bt = driver.ts, driver.oe, driver.bt
G_VALUES = [0., 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
SEEDS = [20260720, 20260721, 20260722]
PAIR_RODS = np.array([0., -13.])
DURATIONS = [0.25, 0.5, 1.]


def write_json(path, data):
    def convert(value):
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
        raise TypeError(type(value).__name__)
    path.write_text(json.dumps(data, indent=2, default=convert, allow_nan=False) + "\n")


def variant(N, state, s, g, rod):
    mk = lambda **kw: oe.VariantEvolution(oe.build_variant_h1(N, s, g, **kw),
                                        state["G"], state["F"])
    main = mk()
    quenches = {v: mk(quench=(N//2, v)) for v in driver.QUENCH_VS}
    Gk, Fk = bt.apply_clock_kick(state["G"], state["F"], N)
    clock = oe.VariantEvolution(oe.build_variant_h1(N, s, g, carve=True), Gk, Fk)
    items, meta = bt.compute_internal_items(main, quenches, clock, N, rod)
    return {"main": main, "quenches": quenches, "clock": clock,
            "items": items, "meta": meta}


def distances(a, b):
    per_item, maximum = bt.battery_distances(a, b)
    return {"items": per_item, "D": maximum}


def crossover_study():
    rod = bt.rod_length()
    records, windows = [], []
    for N, beta in ((256, 1.), (128, 1.), (128, 4.)):
        state = ts.build_tfd(N, beta)
        seeds = SEEDS if (N, beta) == (128, 1.) else SEEDS[:1]
        scrambled = {seed: ts.scramble_l_sector(state, seed=seed) for seed in seeds}
        for g in G_VALUES:
            start = time.monotonic()
            plus = variant(N, state, +1, g, rod)
            minus = variant(N, state, -1, g, rod)
            orientation = distances(plus["items"], minus["items"])
            for seed, scr in scrambled.items():
                complement = variant(N, scr, +1, g, rod)
                records.append({"N": N, "beta": beta, "g": g, "seed": seed,
                    "orientation": orientation,
                    "purification": distances(plus["items"], complement["items"]),
                    "meta": {"O+mirror": plus["meta"], "O-mirror": minus["meta"],
                             "O+scrambled": complement["meta"]}})
                if (N, beta, seed) == (128, 1., SEEDS[0]) and g in (0., 1e-3, 1e-2):
                    for horizon in (100., 200., 300.):
                        times = bt.CLOCK_TIMES[bt.CLOCK_TIMES <= horizon]
                        measured = []
                        for v in (plus, minus, complement):
                            items, meta = bt.compute_internal_items(v["main"], v["quenches"],
                                v["clock"], N, rod, clock_times=times)
                            measured.append((items, meta))
                        windows.append({"N": N, "beta": beta, "g": g, "seed": seed,
                            "requested_horizon": horizon, "actual_horizon": float(times[-1]),
                            "orientation": distances(measured[0][0], measured[1][0]),
                            "purification": distances(measured[0][0], measured[2][0]),
                            "ticks": [m[1]["tick"] for m in measured]})
            print(f"crossover N={N} beta={beta:g} g={g:g}: D_or={orientation['D']:.3g} "
                  f"({time.monotonic()-start:.1f}s)", flush=True)

    fits = []
    for N, beta, seed in sorted({(r["N"],r["beta"],r["seed"]) for r in records}):
        rows = [r for r in records if (r["N"],r["beta"],r["seed"]) == (N,beta,seed)]
        for axis in ("orientation", "purification"):
            for item in ["D", *rows[0][axis]["items"]]:
                values = [r[axis]["D"] if item == "D" else r[axis]["items"][item] for r in rows]
                fits.append({"N":N, "beta":beta, "seed":seed, "axis":axis, "item":item,
                             "fit":measure.power_fit([r["g"] for r in rows],values)})
    historic = json.loads((ROOT/"results/results-orientation.json").read_text())
    discrepancies = []
    for old in historic["records"]:
        matches = [r for r in records if (r["N"],r["beta"],r["g"],r["seed"]) ==
                   (old["N"],old["beta"],old["g"],SEEDS[0])]
        for new in matches:
            for a, b in (("orientation", "orientation-mirror"), ("purification", "purification")):
                discrepancies += [abs(value-old["internal"][b]["items"][key])
                                  for key,value in new[a]["items"].items()]
    null = max(r[a]["D"] for r in records if r["g"] == 0 for a in ("orientation","purification"))
    return {"records":records, "fits":fits, "clock_windows":windows,
            "max_null_distance":null, "null_within_original_tolerance":null < driver.TOL_NULL,
            "max_historical_item_discrepancy":max(discrepancies)}


def pair_study():
    rod = bt.rod_length()
    offsets = np.rint(PAIR_RODS*rod).astype(int)
    records, parity_checks, calibrations = [], [], []
    for N in (64,128,256):
        for beta in (1.,4.):
            state = ts.build_tfd(N,beta)
            Gk,Fk = bt.apply_clock_kick(state["G"],state["F"],N)
            clk = oe.VariantEvolution(oe.build_variant_h1(N,1,0.,carve=True),Gk,Fk)
            tick = bt.clock_items(clk,N)["tick"]
            calibrations.append({"N":N,"beta":beta,"rod":rod,"tick":tick,
                                 "pair_offsets_rods":PAIR_RODS,"pair_offsets_sites":offsets})
            idx = N+((N//2+offsets) % N)
            signed = {}
            for g in [*G_VALUES,-1e-4]:
                evolutions = [oe.VariantEvolution(oe.build_variant_h1(N,s,g),state["G"],state["F"])
                              for s in (1,-1)]
                for duration in DURATIONS:
                    t = duration*tick
                    pairs = [ev.f_block(t,idx)[0,1] for ev in evolutions]
                    normal = [ev.g_block(t,idx) for ev in evolutions]
                    pair_delta = pairs[0]-pairs[1]
                    normal_delta = normal[0]-normal[1]
                    signed[g,duration] = (pair_delta,normal_delta)
                    if g < 0:
                        continue
                    records.append({"N":N,"beta":beta,"g":g,"duration_ticks":duration,
                        "t_model":t,"quadratures_plus":[pairs[0].real,pairs[0].imag],
                        "quadratures_minus":[pairs[1].real,pairs[1].imag],
                        "pair_difference_norm":float(abs(pair_delta)),
                        "normal_difference_norm":float(np.linalg.norm(normal_delta))})
            for duration in DURATIONS:
                p,n = signed[1e-4,duration],signed[-1e-4,duration]
                parity_checks.append({"N":N,"beta":beta,"duration_ticks":duration,
                    "pair_odd_defect":float(abs(p[0]+n[0])),
                    "normal_even_defect":float(np.linalg.norm(p[1]-n[1]))})
            print(f"pair/reference N={N} beta={beta:g} complete",flush=True)
    fits=[]
    for N,beta,duration in sorted({(r["N"],r["beta"],r["duration_ticks"]) for r in records}):
        rows=[r for r in records if (r["N"],r["beta"],r["duration_ticks"]) == (N,beta,duration)]
        for channel in ("pair_difference_norm","normal_difference_norm"):
            fits.append({"N":N,"beta":beta,"duration_ticks":duration,"channel":channel,
                "fit":measure.power_fit([r["g"] for r in rows],[r[channel] for r in rows])})
    return {"calibrations":calibrations,"records":records,"fits":fits,"signed_g_checks":parity_checks}


def finite_trials(pair_data):
    records=[]
    rng=np.random.default_rng(20260922)
    for r in pair_data["records"]:
        if (r["N"],r["beta"]) != (128,1.) or r["g"] not in (0.,1e-4,1e-3,1e-2):
            continue
        correlations=[complex(*r[name]) for name in ("quadratures_plus","quadratures_minus")]
        for visibility in (0.,0.5,1.):
            for noise in (0.,0.05):
                probabilities=[measure.reference_probability(f,visibility=visibility,readout_flip=noise)
                               for f in correlations]
                for trials in (1000,100000,10000000,100000000):
                    result=measure.binomial_discrimination(*probabilities,trials,rng=rng)
                    records.append({"N":128,"beta":1.,"g":r["g"],"duration_ticks":r["duration_ticks"],
                        "visibility":visibility,"readout_flip":noise,"trials":trials,
                        "p_plus_orientation_plus":probabilities[0],"p_plus_orientation_minus":probabilities[1],
                        **result})
    return {"phase":float(np.pi/2),"seed":20260922,"replicates_per_hypothesis":4096,
            "reference":"fresh local two-level pair reference with shared preparation phase",
            "assumptions":"equal priors; independent fresh preparations; known detector probabilities",
            "records":records}


def spreading_study():
    load("lattice-model-exact-fft-evolution.py","lattice_model")
    observer=load("endogenous-observer-rods-clock.py","endogenous_observer")
    old=json.loads((ROOT/"results/results.json").read_text())
    records=[]
    for rec in old["ratios"]:
        if rec["r"] not in (2.,3.):
            continue
        point=[p for p in rec["sweep"] if not p.get("skipped")][-1]
        r,eps=rec["r"],point["eps"]
        rods=point["observer"]
        base=observer.pick_lattice_size(4.5*3*max(rods["rod_x"],rods["rod_y"]))
        rod_checks=[]
        for L in (1024,2048,4096):
            rod_checks.append(measure.bound_state_rods(L,r,1.,eps))
            print(f"rod convergence r={r:g} L={L} done",flush=True)
        rows=[]
        for label,rx,ry in (("original_rods",rods["rod_x"],rods["rod_y"]),
                            ("refined_rods",rod_checks[-1]["rod_x"],rod_checks[-1]["rod_y"])):
            for L in (base,2*base,4*base):
                for samples,refine in ((40,False),(160,False),(40,True)):
                    rows.append({"rod_definition":label,**measure.spreading_measurement(L,r,1.,rx,ry,
                                 samples=samples,refine=refine)})
        last=[p for p in rows if p["rod_definition"] == "refined_rods" and p["refined"]]
        a,b=last[-2:]
        delta_R=abs(a["R"]-b["R"])
        delta_t=abs(a["stopped_at_t"]/b["stopped_at_t"]-1)
        original_replica=next(p for p in rows if p["rod_definition"] == "original_rods"
                             and p["L"] == base and p["samples"] == 40 and not p["refined"])
        records.append({"r":r,"eps":eps,"original_xi":rods["xi"],"original":point["battery"]["spreading"],
            "rod_checks":rod_checks,"packet_checks":rows,
            "old_grid_R_reproduction_error":abs(original_replica["R"]-point["battery"]["spreading"]["R"]),
            "convergence":{"delta_R":delta_R,"relative_delta_stop_time":delta_t,
                "largest_tail_mass":b["tail_mass"],
                "status":"CONVERGED" if delta_R < 1e-4 and delta_t < 1e-4 and b["tail_mass"] < 1e-4
                          else "UNRESOLVED"}})
    fits=[]
    for rec in old["ratios"]:
        if rec["r"] == 1:
            continue
        points=[p for p in rec["sweep"] if not p.get("skipped") and p["observer"]["xi"] >= 2
                and not any(w["uv_capped"] for w in p["wavepacket_raw"].values())]
        fits.append({"r":rec["r"],"fit":measure.power_fit([p["observer"]["xi"] for p in points],
                      [abs(p["A_endo_wavepacket"]["A_endo"]-1) for p in points],floor=1e-12)})
    return {"records":records,"existing_wavepacket_scaling":fits}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"results/followup-20260922")
    args=parser.parse_args()
    output=args.output.resolve()
    if output.exists():
        parser.error(f"Output already exists; choose a new directory: {output}")
    manifest=support.provenance(inputs=("docs/followup-study-plan.md","results/results.json",
        "results/results-orientation.json","orientation-test.md",
        "plans/260720-2257-orientation-gauge-sim/plan.md"))
    manifest["gates"]=[support.run_gate(script) for script in (
        "validate-physics-sanity-checks.py","validate-orientation-gates.py",
        "validate-orientation-artifacts.py","validate-followup-gates.py")]
    manifest["status"]="RUNNING"
    output.mkdir(parents=True,exist_ok=False)
    write_json(output/"manifest.json",manifest)
    start=time.monotonic()
    try:
        crossover=crossover_study()
        write_json(output/"crossover.json",crossover)
        pairs=pair_study()
        write_json(output/"pair-access.json",pairs)
        trials=finite_trials(pairs)
        write_json(output/"finite-trials.json",trials)
        spreading=spreading_study()
        write_json(output/"spreading.json",spreading)
        plots=load("generate-followup-plots.py","followup_plots")
        plots.make_plots(crossover,pairs,trials,spreading,output)
        support.verify_inputs(manifest)
        manifest["status"]="COMPLETE"
        manifest["inputs_verified_unchanged"]=True
        manifest["output_sha256"]={p.name:support.sha256(p) for p in sorted(output.iterdir())
                                   if p.name != "manifest.json"}
    except Exception as error:
        manifest["status"]="FAILED"
        manifest["error"]=f"{type(error).__name__}: {error}"
        raise
    finally:
        manifest["finished_utc"]=support.utc_now()
        manifest["elapsed_seconds"]=time.monotonic()-start
        write_json(output/"manifest.json",manifest)
    print(f"Follow-up complete in {manifest['elapsed_seconds']:.1f}s: {output}",flush=True)


if __name__ == "__main__":
    main()
