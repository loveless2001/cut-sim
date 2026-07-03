"""The endogenous observer: rods, clock, and signal speeds in rods-per-tick ONLY.

Honesty rules enforced here (spec's make-or-break):
- ROD(d): the RMS width along axis d of an attractive point-impurity bound state.
  A *static binding* length set by the local couplings — deliberately NOT defined by
  signal propagation (that would make speed = 1 tautologically) and NOT site counting.
- CLOCK: beat period of the two lowest modes of a small cavity carved from the same
  lattice. A single shared scalar tick; it cancels in x/y speed RATIOS, but makes
  every reported speed a genuine rods-per-tick number.
- SIGNALS the observer can time:
    (a) the quench front — its fastest signal (Lieb-Robinson edge);
    (b) a wavepacket whose wavelength is set endogenously: lambda_d = 4 * rod_d.
- The only lattice-scale intrusion: wavelengths below ~2 sites do not exist (Brillouin
  zone edge). Carrier k is capped at K_UV_CAP < pi; when the cap engages the observer's
  rods are sub-lattice and the continuum description has broken down (reported).
"""
import numpy as np
import lattice_model as lm  # injected by the kebab-module bootstrap in the driver

K_UV_CAP = 2.5          # hard kinematic cutoff, just inside the BZ edge (pi)
LAMBDA_PER_ROD = 4.0    # endogenous choice: signal wavelength = 4 rods (same both axes)


def make_observer(Jx, Jy, eps, L_rod=1024, L_rod_max=2048, clock_n=5):
    """Build the observer's instruments for impurity strength eps.
    Returns rods (sites, god's-eye bookkeeping only), tick, and diagnostics.
    The bound-state lattice grows until wrapped tails are negligible (weakly bound
    states can span tens of sites)."""
    while True:
        psi_b, E0, Eb = lm.impurity_bound_state(L_rod, Jx, Jy, eps)
        rod_x, rod_y, tail = lm.rms_widths(psi_b**2)
        if tail < 1e-4 or L_rod >= L_rod_max:
            break
        L_rod *= 2
    tick = lm.cavity_clock_tick(Jx, Jy, n=clock_n)
    # rod uncertainty: dominated by wrapped tails on the finite lattice
    sigma_rod_rel = tail * 10.0 + 1e-6
    return {
        "eps": eps, "rod_x": rod_x, "rod_y": rod_y,
        "xi": float(np.sqrt(rod_x * rod_y)),        # tuning coordinate (geometric mean)
        "sigma_rod_rel": sigma_rod_rel, "tail_mass": tail,
        "tick": tick, "E0": E0, "binding_energy": Eb,
    }


def wavepacket_com_velocity(L, Jx, Jy, axis, k, w, disp_target=30.0, ntimes=12):
    """Center-of-mass velocity (sites per unit global time) of a Gaussian packet with
    carrier k along `axis` and isotropic envelope width w. Wrap-safe via circular CoM
    + unwrapping over the trajectory. Exact evolution; error from the linear fit."""
    vg_est = max(2.0 * (Jx if axis == 0 else Jy) * abs(np.sin(k)), 1e-9)
    tmax = min(disp_target / vg_est, (L / 3.0) / vg_est)
    times = np.linspace(0.0, tmax, ntimes)
    kx, ky = (k, 0.0) if axis == 0 else (0.0, k)
    psi0 = lm.gaussian_packet(L, kx, ky, w, w)
    E = lm.dispersion(L, Jx, Jy)

    coms = []
    for t in times:
        P = np.abs(lm.evolve(psi0, E, t)) ** 2
        coms.append(lm.circular_center_of_mass(P)[axis])
    ang = np.unwrap(np.array(coms) * 2.0 * np.pi / L) * L / (2.0 * np.pi)

    A = np.vstack([times, np.ones_like(times)]).T
    coef, res, _, _ = np.linalg.lstsq(A, ang, rcond=None)
    dof = max(len(times) - 2, 1)
    s2 = (res[0] / dof) if len(res) else 0.0
    sv = np.sqrt(max((s2 * np.linalg.inv(A.T @ A))[0, 0], 0.0))
    return coef[0], sv


def pick_lattice_size(extent, L_min=512, L_max=2048, margin=32):
    """Smallest power-of-two lattice whose half-width holds `extent` + margin.
    Returns None if even L_max is too small (caller should skip the point)."""
    L = L_min
    while L / 2.0 < extent + margin:
        L *= 2
        if L > L_max:
            return None
    return L


def endogenous_wavepacket_speeds(Jx, Jy, obs, disp_target=30.0):
    """The observer's wavepacket experiment, built entirely from its own rods:
    carrier k_d = 2*pi / (LAMBDA_PER_ROD * rod_d), envelope w_d = one wavelength.
    Returns speeds in sites/time (converted to rods-per-tick by the caller) plus
    whether the UV cap engaged (continuum breakdown flag). Lattice size adapts to
    the packet (rods can reach tens of sites); returns None if it cannot fit."""
    out = {}
    for axis, rod in ((0, obs["rod_x"]), (1, obs["rod_y"])):
        k_raw = 2.0 * np.pi / (LAMBDA_PER_ROD * rod)
        k = min(k_raw, K_UV_CAP)
        w = max(LAMBDA_PER_ROD * rod, 3.0)
        L = pick_lattice_size(3.0 * w + disp_target)
        if L is None:
            return None
        v, sv = wavepacket_com_velocity(L, Jx, Jy, axis, k, w, disp_target)
        out["xy"[axis]] = {"k": k, "uv_capped": bool(k_raw > K_UV_CAP), "w": w,
                           "L": L, "v_sites_per_time": v, "sigma_v": sv}
    return out


def speeds_in_rods_per_tick(v_sites_x, v_sites_y, sv_x, sv_y, obs):
    """Convert raw (sites/time) velocities into the observer's ONLY legal units and
    form A_endo. The tick cancels in the ratio; rod uncertainty enters both axes."""
    ux = v_sites_x * obs["tick"] / obs["rod_x"]
    uy = v_sites_y * obs["tick"] / obs["rod_y"]
    A = ux / uy
    rel = np.hypot(sv_x / abs(v_sites_x), sv_y / abs(v_sites_y))
    rel = np.hypot(rel, 2.0 * obs["sigma_rod_rel"])
    return {"speed_x_rods_per_tick": ux, "speed_y_rods_per_tick": uy,
            "A_endo": A, "sigma_A_endo": abs(A) * rel}
