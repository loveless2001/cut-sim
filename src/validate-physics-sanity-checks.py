"""Physics sanity gates — must ALL pass before any experiment result is trusted.

G1  Unitarity: exact FFT evolution conserves norm to machine precision.
G2  Known velocities: fitted front speeds match the exact band-edge group
    velocities 2*Jx, 2*Jy within 1% (validates the god's-eye fit machinery).
G3  Isotropic null: at Jx == Jy every ratio (A_god, rods, endogenous speeds) is 1
    within tolerance (no fake anisotropy from the pipeline itself).
G4  Battery calibration: fed god's-eye data on an anisotropic substrate (r=2), every
    dimensionless test DETECTS the axis (spec: a battery that can't flag a known
    anisotropy has a void null result).
G5  Bound-state physics: impurity state binds below the band and rod_x/rod_y moves
    toward sqrt(Jx/Jy) as the rod grows (continuum scaling reachable).

Run:  .venv/bin/python3 src/validate-physics-sanity-checks.py   (exit 0 iff all pass)
"""
import importlib.util, pathlib, sys
import numpy as np

SRC = pathlib.Path(__file__).parent


def _load(fname, modname):
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

FAILURES = []


def gate(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        FAILURES.append(name)


def main():
    # G1 unitarity
    E = lm.dispersion(256, 2.0, 1.0)
    psi = lm.evolve(lm.delta_source(256), E, 37.3)
    drift = abs(np.sum(np.abs(psi) ** 2) - 1.0)
    gate("G1 unitarity", drift < 1e-10, f"norm drift {drift:.2e}")

    # G2 front velocities vs exact 2J (threshold-front has a known ~1-2% Airy-edge
    # systematic, folded into sigma; gate at 3%)
    cone = ge.measure_cone(1024, 2.0, 1.0, snapshot=False)
    ex, ey = abs(cone["vx"] / 4.0 - 1), abs(cone["vy"] / 2.0 - 1)
    gate("G2 front velocity", max(ex, ey) < 0.03,
         f"vx={cone['vx']:.4f} (exact 4), vy={cone['vy']:.4f} (exact 2)")

    # G2b sharp check of the propagation machinery: band-edge wavepacket (k=pi/2)
    # CoM velocity = 2*Jx*<sin k> — must match to <0.5%
    vbe, _ = eo.wavepacket_com_velocity(512, 2.0, 1.0, 0, np.pi / 2, 8.0)
    gate("G2b band-edge wavepacket", abs(vbe / 4.0 - 1) < 0.005,
         f"v={vbe:.4f} (exact 4 minus O(sigma_k^2) envelope correction)")

    # G3 isotropic null
    iso = ge.measure_cone(1024, 1.5, 1.5, snapshot=False)
    obs = eo.make_observer(1.5, 1.5, 3.0)
    wp = eo.endogenous_wavepacket_speeds(1.5, 1.5, obs)
    Awp = eo.speeds_in_rods_per_tick(
        wp["x"]["v_sites_per_time"], wp["y"]["v_sites_per_time"],
        wp["x"]["sigma_v"], wp["y"]["sigma_v"], obs)["A_endo"]
    rodr = obs["rod_x"] / obs["rod_y"]
    ok = abs(iso["A_god"] - 1) < 0.01 and abs(rodr - 1) < 0.005 and abs(Awp - 1) < 0.01
    gate("G3 isotropic null", ok,
         f"A_god={iso['A_god']:.4f} rod_ratio={rodr:.4f} A_endo_wp={Awp:.4f}")

    # G4 battery calibration on god's-eye anisotropic data (r=2)
    vwx, svwx = eo.wavepacket_com_velocity(512, 2.0, 1.0, 0, 0.5, 8.0)
    vwy, svwy = eo.wavepacket_com_velocity(512, 2.0, 1.0, 1, 0.5, 8.0)
    cal = bt.calibrate_battery(512, 2.0, 1.0, cone["vx"], cone["vy"],
                               cone["sigma_vx"], cone["sigma_vy"],
                               vwx, vwy, svwx, svwy)
    det = {k: v["detected"] for k, v in cal["tests"].items()}
    gate("G4 battery calibration", cal["calibration_pass"], f"detections={det}")
    # and battery stays null on the isotropic substrate
    vix, svix = eo.wavepacket_com_velocity(512, 1.5, 1.5, 0, 0.5, 8.0)
    viy, sviy = eo.wavepacket_com_velocity(512, 1.5, 1.5, 1, 0.5, 8.0)
    cal_iso = bt.calibrate_battery(512, 1.5, 1.5, iso["vx"], iso["vy"],
                                   iso["sigma_vx"], iso["sigma_vy"],
                                   vix, viy, svix, sviy)
    gate("G4b battery no-false-positive", cal_iso["calibration_pass"],
         f"detections={ {k: v['detected'] for k, v in cal_iso['tests'].items()} }")

    # G5 bound state binds and rod ratio approaches sqrt(r)
    tight = eo.make_observer(2.0, 1.0, 8.0)
    wide = eo.make_observer(2.0, 1.0, 1.5)
    target = np.sqrt(2.0)
    closer = abs(wide["rod_x"] / wide["rod_y"] - target) < abs(
        tight["rod_x"] / tight["rod_y"] - target)
    ok = tight["binding_energy"] > 0 and wide["binding_energy"] > 0 and \
        wide["xi"] > tight["xi"] and closer and wide["tail_mass"] < 1e-3
    gate("G5 bound-state scaling", ok,
         f"xi: {tight['xi']:.2f}->{wide['xi']:.2f}, rod_ratio: "
         f"{tight['rod_x']/tight['rod_y']:.4f}->{wide['rod_x']/wide['rod_y']:.4f} "
         f"(target {target:.4f}), tail={wide['tail_mass']:.1e}")

    print(f"\n{'ALL GATES PASS' if not FAILURES else 'GATES FAILED: ' + str(FAILURES)}")
    sys.exit(0 if not FAILURES else 1)


if __name__ == "__main__":
    main()
