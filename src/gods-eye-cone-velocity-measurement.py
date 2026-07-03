"""God's-eye (control) measurement: Lieb-Robinson cone velocities in BARE lattice units.

A localized quench at the origin spreads ballistically; the correlation front along
each axis is tracked by threshold crossing of |psi(x,t)|^2 with sub-site log-linear
interpolation, then fitted linearly in global simulation time. This uses site counts
and the integrator's t deliberately — it is the external, structure-independent ruler
the endogenous observer is NOT allowed to use.

Outputs vx, vy (sites per unit time) and A_god = vx/vy. For the tight-binding band
the exact band-edge group velocities are 2*Jx and 2*Jy, so A_god should equal Jx/Jy.
"""
import numpy as np
import lattice_model as lm  # injected by the kebab-module bootstrap in the driver

FLOOR = 1e-300


def front_position(prob_line, theta):
    """Outermost sub-site position where prob crosses theta, on a half-axis line
    prob_line[0..L/2] taken outward from the source. Returns np.nan if no crossing."""
    above = np.where(prob_line > theta)[0]
    if len(above) == 0 or above[-1] + 1 >= len(prob_line):
        return np.nan
    i = above[-1]
    lp0 = np.log10(max(prob_line[i], FLOOR))
    lp1 = np.log10(max(prob_line[i + 1], FLOOR))
    return i + (lp0 - np.log10(theta)) / (lp0 - lp1)


THETAS = (1e-6, 1e-8, 1e-10, 1e-12)  # all in the monotone tail (below Airy fringes)


def _fit_front_airy(times, fronts):
    """Fit front(t) = v*t + c*t^(1/3) + b. The t^(1/3) term absorbs the known
    Lieb-Robinson edge broadening (Airy scaling); a plain linear fit is biased
    high by ~1-2%. Requires a WIDE time range so t and t^(1/3) decorrelate.
    Returns (v, sigma_v) from the fit covariance."""
    ok = ~np.isnan(fronts)
    t, f = times[ok], fronts[ok]
    A = np.vstack([t, t ** (1.0 / 3.0), np.ones_like(t)]).T
    coef, res, _, _ = np.linalg.lstsq(A, f, rcond=None)
    dof = max(len(t) - 3, 1)
    s2 = (res[0] / dof) if len(res) else 0.0
    cov = s2 * np.linalg.inv(A.T @ A)
    return coef[0], np.sqrt(max(cov[0, 0], 0.0))


def _axis_velocity(psi0, E, L, J_axis, axis, ntimes, margin):
    """Front velocity along one axis, with the time window sized to THIS axis
    (2*J_axis is used only to choose the window, never in the fit itself).
    Central value = mean over thresholds; sigma = fit error + threshold spread."""
    tmax = (L / 2.0 - margin) / (2.0 * J_axis)
    times = np.linspace(2.0 / J_axis, tmax, ntimes)
    fronts = {th: [] for th in THETAS}
    for t in times:
        P = np.abs(lm.evolve(psi0, E, t)) ** 2
        line = P[: L // 2, 0] if axis == 0 else P[0, : L // 2]
        for th in THETAS:
            fronts[th].append(front_position(line, th))
    fits = [_fit_front_airy(times, np.array(fronts[th])) for th in THETAS]
    vs = np.array([f[0] for f in fits])
    sv = np.hypot(np.mean([f[1] for f in fits]), vs.std())
    return vs.mean(), sv


def measure_cone(L, Jx, Jy, ntimes=30, margin=16, snapshot=True):
    """Full god's-eye cone measurement: vx, vy in bare lattice units, A_god = vx/vy.
    Accuracy ~1% per axis (validated in gate G2); exact band-edge values 2*Jx, 2*Jy
    are reported alongside for reference."""
    E = lm.dispersion(L, Jx, Jy)
    psi0 = lm.delta_source(L)
    vx, svx = _axis_velocity(psi0, E, L, Jx, 0, ntimes, margin)
    vy, svy = _axis_velocity(psi0, E, L, Jy, 1, ntimes, margin)

    A_god = vx / vy
    sA = A_god * np.hypot(svx / vx, svy / vy)
    out = {
        "L": L, "Jx": Jx, "Jy": Jy, "thetas": list(THETAS),
        "vx": vx, "vy": vy, "sigma_vx": svx, "sigma_vy": svy,
        "A_god": A_god, "sigma_A_god": sA,
        "v_exact_x": 2.0 * Jx, "v_exact_y": 2.0 * Jy,
    }
    if snapshot:
        # 0.7x so the fast-axis front sits visibly inside the frame
        t_snap = 0.7 * (L / 2.0 - margin) / (2.0 * max(Jx, Jy))
        P = np.abs(lm.evolve(psi0, E, t_snap)) ** 2
        out["snapshot"] = np.fft.fftshift(P)
        out["snapshot_t"] = t_snap
    return out
