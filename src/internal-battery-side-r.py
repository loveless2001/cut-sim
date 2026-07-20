"""Dimensionless internal battery — side R only, all rods-per-tick or pure ratios.

Units (endogenous, per plan):
  ROD  = RMS width of the bound state of h_R - eps0|q><q| (static binding length,
         1D lattice Green's function — same construction as cut-sim). Built from
         side-R statics only; it is the unit, not the signal.
  TICK = 2*pi / omega_hat_1, omega_hat_1 = phase-slope-fitted beat frequency of the
         two lowest modes of cavity C1, measured from the variant's own clock run.
Items (pre-registered in plan.md):
  1 clock-ratio + clock-traces   2 two-time correlator C<(x,t)   3 KMS beta_hat/tick
  4 quench arrow S_A(t)          5 coherence floor (purity + entanglement spectrum)
  6 D_internal = max over item distances, d(X,Y) = ||X-Y|| / max(||X||,||Y||,1e-300)
"""
import numpy as np
import sys

ts = sys.modules["tfd_state"]
oe = sys.modules["orientation_evolution"]

ROD_EPS0 = 1.5
ROD_LATTICE = 4096
PROBE_OFFSETS_RODS = np.array([0, 2, 4, 8, 12, 18, 24, 32], dtype=float)
SUBREGION_HALF = 12          # A = 24 sites centred at the quench site
SPECTRUM_TOP_K = 8
CLOCK_TIMES = np.linspace(0.0, 300.0, 1200)
KMS_TIMES = np.linspace(0.0, 40.0, 161)
FLOOR = 1e-3                 # KMS spectral-weight floor (relative)


def rod_length(J=1.0, eps0=ROD_EPS0, L=ROD_LATTICE):
    """1D attractive-impurity bound-state RMS width via the lattice Green's function."""
    from scipy.optimize import brentq
    k = 2.0 * np.pi * np.fft.fftfreq(L)
    E = -2.0 * J * np.cos(k)
    Emin = E.min()

    def gap_condition(E0):
        return 1.0 - eps0 * np.mean(1.0 / (E - E0))

    E0 = brentq(gap_condition, Emin - eps0 - 1.0, Emin - 1e-12, xtol=1e-14)
    psi = np.fft.ifft(1.0 / (E0 - E)).real
    p = psi**2 / np.sum(psi**2)
    x = np.fft.fftfreq(L, d=1.0 / L)
    return float(np.sqrt(np.sum(p * x**2)))


def probe_offsets_sites(rod):
    """Nearest lattice representatives for the pre-registered probe offsets in rods."""
    sites = np.rint(PROBE_OFFSETS_RODS * float(rod)).astype(int)
    return np.maximum(sites, 0)


CLOCK_KICK_THETA = 0.5


def apply_clock_kick(G, F, N):
    """R-local clock preparation: phase imprint e^{i theta n_x} on the LEFT HALF of
    each cavity. Needed because the thermal ring correlator is reflection-symmetric
    about the cavity centre while the two lowest cavity modes have opposite parity,
    so the bare two-mode coherence z(0) vanishes exactly (parity selection rule —
    found at gate G6, amendment documented in plan.md). The kick is a Gaussian
    unitary built entirely from side-R operators."""
    twoN = G.shape[0]
    K = np.ones(twoN, dtype=complex)
    for start, ell in oe.cavity_specs(N):
        half = N + ((start + np.arange(ell // 2)) % N)
        K[half] = np.exp(1j * CLOCK_KICK_THETA)
    Kg = np.conj(K)
    return (K[:, None] * G * Kg[None, :]), (K[:, None] * F * K[None, :])


def cavity_modes(ell, J=1.0):
    """Two lowest eigenmodes + analytic two-mode gap of an ell-site open chain."""
    h = np.zeros((ell, ell))
    for i in range(ell - 1):
        h[i, i + 1] = h[i + 1, i] = -J
    ev, vec = np.linalg.eigh(h)
    gap_analytic = 2.0 * J * (np.cos(np.pi / (ell + 1)) - np.cos(2.0 * np.pi / (ell + 1)))
    return vec[:, 0], vec[:, 1], float(ev[1] - ev[0]), gap_analytic


def clock_measurement(evo, N, spec, times=CLOCK_TIMES):
    """omega_hat via unwrapped phase-slope fit of z(t) = <a+_1 a_2>(t) on one cavity."""
    start, ell = spec
    idx = N + ((start + np.arange(ell)) % N)
    v1, v2, gap_num, gap_ana = cavity_modes(ell)
    z = evo.coherence(times, idx, v1, v2)
    phase = np.unwrap(np.angle(z))
    slope = np.polyfit(times, phase, 1)[0]
    return {"omega": abs(float(slope)), "z0_abs": float(abs(z[0])),
            "gap_numeric": gap_num, "gap_analytic": gap_ana,
            "idx": idx, "v1": v1, "v2": v2}


def clock_items(evo_clock, N):
    """Item 1: beat-frequency ratio + dimensionless coherence traces; also the tick."""
    c1, c2 = oe.cavity_specs(N)
    m1 = clock_measurement(evo_clock, N, c1)
    m2 = clock_measurement(evo_clock, N, c2)
    tick = 2.0 * np.pi / m1["omega"]
    tt = np.arange(65) * tick / 8.0                       # 8 ticks, 1/8-tick sampling
    traces = []
    for m in (m1, m2):
        z = evo_clock.coherence(tt, m["idx"], m["v1"], m["v2"])
        traces.append(z / z[0])
    return {"tick": tick, "m1": m1, "m2": m2,
            "clock-ratio": np.array([m1["omega"] / m2["omega"]]),
            "clock-traces": np.concatenate(traces)}


def two_time_item(evo_main, N, tick, rod):
    """Item 2: C<(x, t) on R probes, t sampled in ticks (0..2 ticks, 1/16-tick step)."""
    c = N // 2
    rows = N + ((c + probe_offsets_sites(rod)) % N)
    tt = np.arange(33) * tick / 16.0
    Cl, _, _ = evo_main.two_time(tt, rows, N + c)
    return Cl.flatten()


def kms_item(evo_main, N, tick, times=KMS_TIMES):
    """Item 3: extracted beta_hat (from the KMS ratio) in tick units."""
    x0 = N + N // 2
    Cl, Cg, _ = evo_main.two_time(times, np.array([x0]), x0)
    Cl, Cg = Cl[0], Cg[0]
    dt = times[1] - times[0]
    # two-sided series s(-t) = conj(s(t)), Hann window, exact FFT grid
    def spectrum(s):
        full = np.concatenate([np.conj(s[:0:-1]), s])
        tfull = np.concatenate([-times[:0:-1], times])
        w = 0.5 * (1.0 + np.cos(np.pi * tfull / times[-1]))
        Sf = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(full * w))) * dt
        om = np.fft.fftshift(np.fft.fftfreq(len(full), d=dt)) * 2.0 * np.pi
        return om, np.real(Sf)
    om, Sg = spectrum(Cg)                  # peaks at +eps_a, weight (1-n)
    _, Sl = spectrum(Cl)                   # peaks at -eps_a, weight n
    Sl_flip = Sl[::-1] if len(om) % 2 == 1 else np.roll(Sl[::-1], 1)
    good = (Sg > FLOOR * Sg.max()) & (Sl_flip > FLOOR * Sg.max()) & (np.abs(om) > 1e-9)
    beta_hat = float(np.polyfit(om[good], np.log(Sg[good] / Sl_flip[good]), 1)[0])
    return np.array([beta_hat / tick]), beta_hat


def subregion_indices(N):
    c = N // 2
    return N + ((c + np.arange(-SUBREGION_HALF, SUBREGION_HALF)) % N)


def quench_arrow_item(evo_quench, N, tick):
    """Item 4: S_A(t) curve, t in ticks (0..3 ticks, 1/8-tick step)."""
    A = subregion_indices(N)
    tt = np.arange(25) * tick / 8.0
    S = []
    for t in tt:
        GA, FA = evo_quench.g_block(t, A), evo_quench.f_block(t, A)
        S.append(ts.entropy(GA, FA, np.arange(len(A))))
    return np.array(S)


def coherence_floor_item(evo_main, N, tick):
    """Item 5: purity + top-k entanglement spectrum of A over the main run."""
    A = subregion_indices(N)
    tt = np.arange(25) * tick / 8.0
    out = []
    for t in tt:
        GA, FA = evo_main.g_block(t, A), evo_main.f_block(t, A)
        out.append(np.concatenate([[ts.purity(GA, FA, np.arange(len(A)))],
                                   ts.ent_spectrum_top(GA, FA, np.arange(len(A)),
                                                       k=SPECTRUM_TOP_K)]))
    return np.concatenate(out)


def compute_internal_items(evo_main, evo_quenches, evo_clock, N, rod=1.0):
    """Full battery for one variant. evo_quenches = {V: VariantEvolution}."""
    clk = clock_items(evo_clock, N)
    tick = clk["tick"]
    kms, beta_hat = kms_item(evo_main, N, tick)
    items = {
        "clock-ratio": clk["clock-ratio"],
        "clock-traces": clk["clock-traces"],
        "two-time": two_time_item(evo_main, N, tick, rod),
        "kms-beta": kms,
        "coherence-floor": coherence_floor_item(evo_main, N, tick),
    }
    for V, evq in evo_quenches.items():
        items[f"quench-arrow-V{V}"] = quench_arrow_item(evq, N, tick)
    return items, {"tick": tick, "beta_hat": beta_hat,
                   "clock_z0": (clk["m1"]["z0_abs"], clk["m2"]["z0_abs"]),
                   "probe_offsets_rods": PROBE_OFFSETS_RODS.tolist(),
                   "probe_offsets_sites": probe_offsets_sites(rod).tolist()}


def distance(X, Y):
    """Pre-registered metric d(X,Y) = ||X-Y|| / max(||X||, ||Y||, 1e-300)."""
    X, Y = np.asarray(X).ravel(), np.asarray(Y).ravel()
    return float(np.linalg.norm(X - Y) / max(np.linalg.norm(X), np.linalg.norm(Y), 1e-300))


def battery_distances(items_a, items_b):
    """Per-item distances + D_internal = max."""
    d = {k: distance(items_a[k], items_b[k]) for k in items_a}
    return d, max(d.values())
