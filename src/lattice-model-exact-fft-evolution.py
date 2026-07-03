"""Exact single-particle dynamics of a 2D anisotropic tight-binding lattice (PBC).

H = -Jx * sum (c+_{x+1,y} c_{x,y} + h.c.)  -  Jy * sum (c+_{x,y+1} c_{x,y} + h.c.)

Free/Gaussian theory: the single-particle dispersion is
    E(kx, ky) = -2 Jx cos(kx) - 2 Jy cos(ky)
and time evolution of any one-particle amplitude psi(x,y) is EXACT via FFT:
    psi(t) = IFFT2[ exp(-i E(k) t) * FFT2[psi(0)] ].
|psi(x,t)|^2 is exactly the two-point correlation C(x,t) = |<x| e^{-iHt} |0>|^2
for a localized quench at the origin — no Trotter error, no truncation.

Conventions: sources/impurities sit at index (0,0); real-space coordinates are the
wrapped ("centered") coordinates 0..L/2-1, -L/2..-1 so distances are wrap-safe as
long as support stays well inside |x| < L/2.
"""
import numpy as np
from scipy.optimize import brentq


def dispersion(L, Jx, Jy):
    """E(k) on the FFT grid, shape (L, L), axis 0 = x, axis 1 = y."""
    k = 2.0 * np.pi * np.fft.fftfreq(L)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    return -2.0 * Jx * np.cos(kx) - 2.0 * Jy * np.cos(ky)


def centered_coords(L):
    """Wrapped integer coordinates [0, 1, ..., L/2-1, -L/2, ..., -1]."""
    return np.fft.fftfreq(L, d=1.0 / L)


def evolve(psi0, E, t):
    """Exact evolution of amplitude psi0 for time t under dispersion grid E."""
    return np.fft.ifft2(np.exp(-1j * E * t) * np.fft.fft2(psi0))


def delta_source(L):
    """Single-site excitation at the origin (localized quench)."""
    psi = np.zeros((L, L), dtype=complex)
    psi[0, 0] = 1.0
    return psi


def gaussian_packet(L, kx, ky, wx, wy):
    """Normalized Gaussian wavepacket centered at origin with carrier (kx, ky)
    and envelope RMS widths (wx, wy) in lattice sites."""
    X, Y = np.meshgrid(centered_coords(L), centered_coords(L), indexing="ij")
    psi = np.exp(1j * (kx * X + ky * Y)) * np.exp(
        -(X**2) / (4.0 * wx**2) - (Y**2) / (4.0 * wy**2)
    )
    return psi / np.sqrt(np.sum(np.abs(psi) ** 2))


def impurity_bound_state(L, Jx, Jy, eps):
    """Exact bound state of an attractive point impurity of strength eps at the origin,
    H = H0 - eps |0><0|.  The binding condition is
        1 = eps * (1/N) sum_k 1/(E(k) - E0),   E0 < min E(k),
    and the (unnormalized) wavefunction is the lattice Green's function
        psi(x) proportional to (1/N) sum_k e^{ikx} / (E0 - E(k)).
    In 2D an attractive impurity always binds (log divergence at the band bottom),
    so eps sweeps the bound-state size from ~1 site (large eps) to >>1 (small eps).
    Returns (psi, E0, binding_energy)."""
    E = dispersion(L, Jx, Jy)
    Emin = E.min()

    def gap_condition(E0):
        return 1.0 - eps * np.mean(1.0 / (E - E0))

    lo = Emin - eps - 1.0                # gap_condition > 0 here (sum < 1/(eps+1))
    hi = Emin - 1e-12                    # diverges to -inf at the band bottom
    E0 = brentq(gap_condition, lo, hi, xtol=1e-14, rtol=1e-15)
    psi = np.fft.ifft2(1.0 / (E0 - E)).real
    psi /= np.sqrt(np.sum(psi**2))
    return psi, E0, Emin - E0


def rms_widths(prob):
    """RMS widths (sigma_x, sigma_y) of a probability distribution centered near the
    origin, using wrapped coordinates. Also returns the probability mass outside
    |coord| < L/4 in either direction (wrap-safety diagnostic)."""
    L = prob.shape[0]
    p = prob / prob.sum()
    c = centered_coords(L)
    px, py = p.sum(axis=1), p.sum(axis=0)
    mx, my = np.dot(px, c), np.dot(py, c)
    sx = np.sqrt(max(np.dot(px, c**2) - mx**2, 0.0))
    sy = np.sqrt(max(np.dot(py, c**2) - my**2, 0.0))
    far = np.abs(c) >= L / 4
    tail = max(px[far].sum(), py[far].sum())
    return sx, sy, tail


def circular_center_of_mass(prob):
    """Wrap-safe center of mass per axis via circular mean; returns values in
    (-L/2, L/2]. Caller unwraps trajectories over time."""
    L = prob.shape[0]
    p = prob / prob.sum()
    out = []
    for axis in (0, 1):
        marg = p.sum(axis=1 - axis)
        z = np.dot(marg, np.exp(2j * np.pi * np.arange(L) / L))
        out.append(L / (2.0 * np.pi) * np.angle(z))
    return out[0], out[1]


def cavity_clock_tick(Jx, Jy, n=5):
    """Endogenous clock: an excitation confined to an n x n cavity (open block cut
    from the same lattice) beats at the frequency of the lowest spectral gap.
    Tick T = 2*pi / (E1 - E0). One shared scalar — direction-blind by construction;
    both couplings enter but no axis is singled out."""
    N = n * n
    H = np.zeros((N, N))
    for x in range(n):
        for y in range(n):
            i = x * n + y
            if x + 1 < n:
                H[i, i + n] = H[i + n, i] = -Jx
            if y + 1 < n:
                H[i, i + 1] = H[i + 1, i] = -Jy
    ev = np.linalg.eigvalsh(H)
    return 2.0 * np.pi / (ev[1] - ev[0])
