"""Check follow-up coverage, numerical consistency, provenance, and preserved inputs."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/followup-20260922")
    output = parser.parse_args().output
    manifest = json.loads((output / "manifest.json").read_text())
    failures = []

    def check(ok, message):
        if not ok:
            failures.append(message)

    check(manifest["status"] == "COMPLETE", "run completed")
    check(manifest.get("inputs_verified_unchanged") is True, "input hashes verified at completion")
    check(len(manifest["gates"]) == 4 and all(g["returncode"] == 0 for g in manifest["gates"]),
          "all four preflight suites passed")
    for name, digest in manifest["input_sha256"].items():
        check((ROOT / name).is_file() and hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
              f"source/input hash: {name}")
    expected_outputs = {"crossover.json", "pair-access.json", "finite-trials.json", "spreading.json",
                        "followup-summary.png", "followup-summary.svg"}
    check(set(manifest["output_sha256"]) == expected_outputs, "expected result and plot inventory")
    for name, digest in manifest["output_sha256"].items():
        check((output / name).is_file() and hashlib.sha256((output / name).read_bytes()).hexdigest() == digest,
              f"output hash: {name}")

    data = {name: json.loads((output / f"{name}.json").read_text()) for name in
            ("crossover", "pair-access", "finite-trials", "spreading")}
    crossover, pairs, trials, spreading = (data[k] for k in data)
    gs = [0., 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
    combos = [(256, 1., 20260720), (128, 4., 20260720)] + [(128, 1., s) for s in
                                                                       (20260720,20260721,20260722)]
    expected = {(n,b,s,g) for n,b,s in combos for g in gs}
    observed = [(r["N"],r["beta"],r["seed"],r["g"]) for r in crossover["records"]]
    check(set(observed) == expected and len(observed) == len(expected), "complete crossover/seed grid")
    check(crossover["max_null_distance"] < 1e-9, "extended zero-coupling controls")
    check(crossover["max_historical_item_discrepancy"] < 1e-8, "original item values reproduced")
    expected = {(n,b,g,t) for n in (64,128,256) for b in (1.,4.) for g in gs for t in (.25,.5,1.)}
    observed = [(r["N"],r["beta"],r["g"],r["duration_ticks"]) for r in pairs["records"]]
    check(set(observed) == expected and len(observed) == len(expected), "complete pair-access grid")
    for row in pairs["signed_g_checks"]:
        check(max(row["pair_odd_defect"],row["normal_even_defect"]) < 1e-10, "signed-g parity checks")
    for fit in [r["fit"] for r in crossover["fits"]+pairs["fits"]]:
        points = fit["resolved_points"]
        if len(points) >= 4:
            xx, yy = np.log(np.array(points).T)
            slope = np.linalg.lstsq(np.column_stack([xx,np.ones(len(xx))]),yy,rcond=None)[0][0]
            check(abs(slope-fit["windows"]["all"]["slope"]) < 1e-10, "stored slopes follow stored points")
    check(len(trials["records"]) == 288, "complete trial-budget/noise grid")
    for r in trials["records"]:
        error = r["exact_error"]
        check(0 <= error <= .5+1e-12, "valid equal-prior error")
        if r["visibility"] == 0 or r["g"] == 0:
            check(abs(error-.5) < 1e-8, "no-reference / zero-coupling error is chance")
        check(abs(r["simulated_error"]-error) <= 6*r["simulation_se"]+1/4096,
              "sampled records agree with exact binomial error")
    for r in spreading["records"]:
        check(r["old_grid_R_reproduction_error"] < 1e-9, "separable solver reproduces archived spreading")
        check(len(r["rod_checks"]) == 3 and len(r["packet_checks"]) == 18, "complete convergence grid")
    if failures:
        for failure in sorted(set(failures)):
            print("FAIL:", failure)
        return 1
    print("FOLLOW-UP ARTIFACT CHECKS PASS: coverage, source/output hashes, nulls, slopes, detector, convergence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
