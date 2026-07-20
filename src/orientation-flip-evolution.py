"""Exact O+/O- evolution of the doubled-chain Gaussian state; coupling window; readouts.

Variant single-particle Hamiltonian (2N x 2N, real symmetric — evolution is exact eigh):
  H1 = [[s * h_L, g W], [g W^T, h_R(+mods)]],  s = +1 (O+) / -1 (O-),
  W = identity on the 16-site coupling window centred at N/2.
Side-R modifications (R-local devices, never touch L): carved cavities (cut bonds),
local quench potential +V n_q. Orientation flip is Impl A (flipped generator); Impl B
(conjugation sandwich, evolve under -H1 between two Theta_L conjugations) is provided
for the pre-registered A/B equivalence check.

Everything is evaluated in the eigenbasis of H1 (Q, eps):
  G(t)[I,J] = (Q_I E) Gm (Q_J E)+,  Gm = Q+ G0 Q,  E = diag(e^{-i eps t})
  F(t)[I,J] = (Q_I E) Fm (Q_J E)^T, Fm = Q+ F0 Q*
Two-time (Heisenberg) correlators, exact:
  C<[i](t) = <c+_i(t) c_{x0}(0)> = conj(U(t) conj(G0^T) )... = (conj(U) G0^T) rows
  C>[i](t) = <c_i(t) c+_{x0}(0)> = (U (I - G0)) rows
  K [i](t) = <c_i(t) c_{x0}(0)>  = (U F0) rows
"""
import numpy as np

COUPLING_WINDOW = 16


def window_sites(N, w=COUPLING_WINDOW):
    """Site indices (per side, 0..N-1) of the coupling window centred at N/2."""
    c = N // 2
    return np.arange(c - w // 2, c + w // 2)


def cavity_specs(N):
    """(start, length) of the two carved R cavities: C1 (l=8) inside the coupling
    window, C2 (l=13) diametrically opposite. Chosen to avoid PBC wrap."""
    c = N // 2
    c1 = (c - 4, 8)
    start2 = (c + N // 2 - 6) % N
    start2 = min(start2, N - 13)          # keep contiguous (no wrap bookkeeping)
    return c1, (start2, 13)


def build_variant_h1(N, s, g, J=1.0, carve=False, quench=None, w=COUPLING_WINDOW):
    """Assemble the 2N x 2N variant Hamiltonian. quench = (site_on_R, V) or None.
    carve=True cuts the boundary bonds of both cavities in h_R (clock protocol)."""
    import sys
    ts = sys.modules["tfd_state"]
    hL = ts.ring_hamiltonian(N, J)
    hR = ts.ring_hamiltonian(N, J)
    if carve:
        for start, ell in cavity_specs(N):
            for (a, b) in ((start - 1) % N, start), ((start + ell - 1) % N, (start + ell) % N):
                hR[a, b] = hR[b, a] = 0.0
    if quench is not None:
        q, V = quench
        hR[q, q] += V
    H1 = np.zeros((2 * N, 2 * N))
    H1[:N, :N] = s * hL
    H1[N:, N:] = hR
    for i in window_sites(N, w):
        H1[i, N + i] = H1[N + i, i] = g
    return H1


class VariantEvolution:
    """Exact evolution of one variant state under one protocol Hamiltonian."""

    def __init__(self, H1, G0, F0):
        self.eps, self.Q = np.linalg.eigh(H1)
        self.H1, self.G0, self.F0 = H1, G0, F0
        Qc = self.Q.conj()
        self.Gm = Qc.T @ G0 @ self.Q
        self.Fm = Qc.T @ F0 @ Qc

    def _qe(self, t, idx):
        return self.Q[idx, :] * np.exp(-1j * self.eps * t)[None, :]

    def g_block(self, t, idx):
        QE = self._qe(t, idx)
        return QE @ self.Gm @ QE.conj().T

    def f_block(self, t, idx):
        QE = self._qe(t, idx)
        return QE @ self.Fm @ QE.T

    def gf_full(self, t):
        n = self.H1.shape[0]
        return self.g_block(t, np.arange(n)), self.f_block(t, np.arange(n))

    def densities(self, times, sites):
        """<n_x(t)> for x in sites, all t at once: shape (len(sites), len(times))."""
        ph = np.exp(-1j * np.outer(self.eps, times))            # (2N, T)
        out = np.empty((len(sites), len(times)))
        for si, x in enumerate(sites):
            u = self.Q[x, :]
            A = (u[:, None] * ph)                               # rows of Q_x E(t)
            out[si] = np.real(np.einsum("at,ab,bt->t", A, self.Gm, np.conj(A)))
        return out

    def coherence(self, times, idx, v1, v2):
        """z(t) = <a+_1 a_2>(t) = v2^T G(t)[idx,idx] v1 for all t (vectorized)."""
        a = self.Q[idx, :].conj().T @ v1                        # (2N,)
        b = self.Q[idx, :].T @ v2
        ph = np.exp(-1j * np.outer(self.eps, times))            # (2N, T)
        right = self.Gm @ (a[:, None] * np.conj(ph))            # (2N, T)
        return np.einsum("at,at->t", b[:, None] * ph, right)

    def two_time(self, times, rows, x0):
        """(C<, C>, K) each shape (len(rows), len(times)) — see module docstring."""
        ph = np.exp(-1j * np.outer(self.eps, times))
        Qr = self.Q[rows, :]
        n = self.H1.shape[0]
        wl = self.Q.conj().T @ np.conj(self.G0.T[:, x0])        # C< = conj(U conj(G0^T))
        wg = self.Q.conj().T @ ((np.eye(n) - self.G0)[:, x0])   # C> = U (I - G0)
        wk = self.Q.conj().T @ self.F0[:, x0]                   # K  = U F0
        Cl = np.conj(Qr @ (ph * wl[:, None]))
        Cg = Qr @ (ph * wg[:, None])
        Kk = Qr @ (ph * wk[:, None])
        return Cl, Cg, Kk

    def conservation_drift(self, t):
        """(relative number drift, relative energy drift) at time t — gate G9."""
        G_t, _ = self.gf_full(t)
        n0, n1 = np.real(np.trace(self.G0)), np.real(np.trace(G_t))
        e0 = np.real(np.trace(self.H1 @ self.G0))
        e1 = np.real(np.trace(self.H1 @ G_t))
        scale_e = max(abs(e0), 1.0)
        return abs(n1 - n0) / max(abs(n0), 1.0), abs(e1 - e0) / scale_e


class ImplBEvolution:
    """Impl B of the orientation flip: K o evolve under -H1 o K, with K = entrywise
    conjugation (theta_l_conjugation). A genuinely distinct code path (eigh of -H1);
    exposes the same readout interface as VariantEvolution so the whole battery can
    run through it — the pre-registered A/B check compares full battery verdicts.
    Heisenberg operators evolve with U_B(t) = conj(U_inner(t)), U_inner = e^{+i H1 t}."""

    def __init__(self, H1, G0, F0):
        import sys
        ts = sys.modules["tfd_state"]
        Gc, Fc = ts.theta_l_conjugation(G0, F0)
        self.inner = VariantEvolution(-H1, Gc, Fc)
        self.G0, self.F0 = G0, F0

    def g_block(self, t, idx):
        return np.conj(self.inner.g_block(t, idx))

    def f_block(self, t, idx):
        return np.conj(self.inner.f_block(t, idx))

    def coherence(self, times, idx, v1, v2):
        return np.conj(self.inner.coherence(times, idx, v1, v2))

    def two_time(self, times, rows, x0):
        ev = self.inner
        ph = np.exp(-1j * np.outer(ev.eps, times))
        Qr = ev.Q[rows, :]
        n = ev.H1.shape[0]
        # U_B = conj(U_inner):  C< = U_in G0^T ; C> = conj(U_in conj(I-G0)) ; likewise K
        wl = ev.Q.conj().T @ self.G0.T[:, x0]
        wg = ev.Q.conj().T @ np.conj((np.eye(n) - self.G0)[:, x0])
        wk = ev.Q.conj().T @ np.conj(self.F0[:, x0])
        Cl = Qr @ (ph * wl[:, None])
        Cg = np.conj(Qr @ (ph * wg[:, None]))
        Kk = np.conj(Qr @ (ph * wk[:, None]))
        return Cl, Cg, Kk
