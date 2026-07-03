"""Adversarial battery of DIMENSIONLESS internal experiments (spec measurement 3).

Every test returns a pure ratio R (should be 1 if the substrate axis is invisible),
an uncertainty, and a DETECTED flag under the pre-registered criterion:

    DETECTED  iff  |R - 1| > max(TOL, NSIG * sigma_R),   TOL = 0.02, NSIG = 5.

Tests:
  1. front_ratio      — fastest-signal (LR front) speed, x vs y, in rods per tick.
  2. wavepacket_ratio — endogenously-prepared wavepacket speed, x vs y, rods per tick.
  3. spreading        — birefringence/dispersion: a k=0 packet prepared isotropic in
     ROD units; observer waits (internal criterion: until sigma_x grows by sqrt(2))
     and checks the aspect ratio in rod units. Any preferred axis shows up as R != 1.

CALIBRATION GATE (spec trap #4): the same tests are fed god's-eye units
(rod = 1 site, tick = 1 dt). On an anisotropic substrate they MUST fire there,
otherwise their endogenous null results are void.
"""
import numpy as np
import lattice_model as lm  # injected by the kebab-module bootstrap in the driver

TOL = 0.02
NSIG = 5.0


def _verdict(R, sigma):
    return {"R": float(R), "sigma": float(sigma),
            "detected": bool(abs(R - 1.0) > max(TOL, NSIG * sigma))}


def front_ratio_test(vx, vy, svx, svy, rod_x=1.0, rod_y=1.0, sigma_rod_rel=0.0):
    """R = (vx/rod_x)/(vy/rod_y); the shared tick cancels exactly."""
    R = (vx / rod_x) / (vy / rod_y)
    rel = np.hypot(svx / vx, svy / vy)
    return _verdict(R, abs(R) * np.hypot(rel, 2.0 * sigma_rod_rel))


def wavepacket_ratio_test(vx, vy, svx, svy, rod_x=1.0, rod_y=1.0, sigma_rod_rel=0.0):
    """Same pure ratio, but for the observer's own low-energy signals."""
    return front_ratio_test(vx, vy, svx, svy, rod_x, rod_y, sigma_rod_rel)


def spreading_test(L, Jx, Jy, rod_x, rod_y, s=3.0, sigma_rod_rel=0.0,
                   nsamples=40, grow=np.sqrt(2.0)):
    """Prepare a stationary Gaussian, widths (s*rod_x, s*rod_y) — 'round' by the
    observer's own rods. Evolve until sigma_x has grown by `grow` (an internal,
    dimensionless stop criterion), then R = (sigma_x/rod_x)/(sigma_y/rod_y).
    Free-particle prediction: widths grow as t * (2 J_d) / (2 sigma0_d); in the
    continuum, rod_d^2 ~ J_d makes the rod-unit aspect ratio stay exactly 1."""
    w0x, w0y = s * rod_x, s * rod_y
    psi0 = lm.gaussian_packet(L, 0.0, 0.0, w0x, w0y)
    E = lm.dispersion(L, Jx, Jy)
    # numerical horizon only (not a measurement): time for the fastest band mode to
    # double the narrower width, times a generous margin
    t_hi = 8.0 * max(w0x, w0y) * min(w0x, w0y) / min(Jx, Jy)
    sx = sy = None
    for t in np.linspace(t_hi / nsamples, t_hi, nsamples):
        P = np.abs(lm.evolve(psi0, E, t)) ** 2
        sx, sy, tail = lm.rms_widths(P)
        if sx >= grow * w0x or sy >= grow * w0y:
            break
    R = (sx / rod_x) / (sy / rod_y)
    sigma = abs(R) * np.hypot(2.0 * sigma_rod_rel, tail * 10.0 + 0.002)
    out = _verdict(R, sigma)
    out.update({"sigma_x_final": float(sx), "sigma_y_final": float(sy),
                "stopped_at_t": float(t), "tail_mass": float(tail)})
    return out


def calibrate_battery(L, Jx, Jy, vfx, vfy, svfx, svfy, vwx, vwy, svwx, svwy):
    """God's-eye calibration: rods = 1 site, tick = 1 dt. On Jx != Jy every test must
    DETECT; on Jx == Jy every test must stay null. Returns per-test results + pass."""
    res = {
        "front": front_ratio_test(vfx, vfy, svfx, svfy),
        "wavepacket": wavepacket_ratio_test(vwx, vwy, svwx, svwy),
        "spreading": spreading_test(L, Jx, Jy, rod_x=1.0, rod_y=1.0),
    }
    anisotropic = abs(Jx / Jy - 1.0) > TOL
    ok = all(r["detected"] == anisotropic for r in res.values())
    return {"tests": res, "substrate_anisotropic": anisotropic, "calibration_pass": ok}
