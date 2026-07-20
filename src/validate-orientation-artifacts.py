"""Fast consistency checks for the orientation-gauge result artifacts.

This is intentionally lighter than the numerical gates: it checks verdict semantics,
result-field provenance, and claim/documentation consistency around the stored
orientation run.

Run: .venv/bin/python3 src/validate-orientation-artifacts.py
"""
import importlib.util
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _load(fname, modname):
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, SRC / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def check(ok, msg, failures):
    if not ok:
        failures.append(msg)


def close(a, b, rel=1e-12, abs_=1e-15):
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=abs_)


def main():
    failures = []
    driver = _load("run-orientation-gauge-experiment.py", "orientation_driver")
    bt = _load("internal-battery-side-r.py", "internal_battery")
    res = json.loads((ROOT / "results" / "results-orientation.json").read_text())

    classify = getattr(driver, "classify_verdict", None)
    check(classify is not None, "driver exposes classify_verdict()", failures)
    if classify is not None:
        check(classify(0.0, True) == "HOLDS", "null + live controls => HOLDS", failures)
        check(classify(2e-9, True) == "FALSIFIED", "g=0 hit + live controls => FALSIFIED", failures)
        check(classify(0.0, False) == "INCONCLUSIVE",
              "null + dead controls => INCONCLUSIVE", failures)
        check(classify(2e-9, False) == "INCONCLUSIVE",
              "g=0 hit + dead controls => INCONCLUSIVE", failures)

    for axis in ("orientation-mirror", "purification"):
        cross = res["verdict"]["crossover"][axis]
        check("all_nonzero_slope_D" in cross,
              f"{axis} stores saturated all-nonzero slope separately", failures)
        check(cross.get("smallg_slope_window") == [0.001, 0.01],
              f"{axis} records the small-g slope window", failures)
        d_vs_g = cross["D_vs_g"]
        two_point = math.log(float(d_vs_g["0.01"]) / float(d_vs_g["0.001"])) / math.log(10.0)
        check(close(cross["smallg_slope_D"], two_point),
              f"{axis} smallg_slope_D matches 1e-3 to 1e-2 slope", failures)

    probe_offsets_sites = getattr(bt, "probe_offsets_sites", None)
    check(probe_offsets_sites is not None, "battery exposes probe_offsets_sites()", failures)
    if probe_offsets_sites is not None:
        expected_sites = list(map(int, probe_offsets_sites(res["records"][0]["rod"])))
    else:
        expected_sites = None
    expected_rods = [float(x) for x in getattr(bt, "PROBE_OFFSETS_RODS", [])]
    for rec in res["records"]:
        for variant, meta in rec["meta"].items():
            check(meta.get("probe_offsets_rods") == expected_rods,
                  f"{variant} N={rec['N']} beta={rec['beta']} g={rec['g']} records rod offsets",
                  failures)
            if expected_sites is not None:
                check(meta.get("probe_offsets_sites") == expected_sites,
                      f"{variant} N={rec['N']} beta={rec['beta']} g={rec['g']} records site offsets",
                      failures)

    plan = (ROOT / "plans" / "260720-2257-orientation-gauge-sim" / "plan.md").read_text()
    writeup = (ROOT / "docs" / "results-writeup-orientation.md").read_text()
    web = (ROOT / "web" / "orientation-gauge-lab.html").read_text()
    check("no extra excitation needed" not in plan,
          "plan no longer contradicts the clock-kick amendment", failures)
    check("beta = 0.5 was a null-only stress point" in writeup,
          "write-up marks beta=0.5 as null-only", failures)
    check("beta = 0.5 was null-only" in web,
          "web page marks beta=0.5 as null-only", failures)

    if failures:
        print("ORIENTATION ARTIFACT CHECKS FAILED")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("ORIENTATION ARTIFACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
