"""TFD + scrambled Gaussian purification builders, correlation-matrix formalism, Theta_L.

Conventions (fixed in plans/260720-2257-orientation-gauge-sim/plan.md):
  modes 0..N-1 = side L, N..2N-1 = side R (N sites per side, PBC ring each).
  G[i,j] = <c+_j c_i>   (Hermitian)      -> evolves as U G U+
  F[i,j] = <c_i c_j>    (antisymmetric)  -> evolves as U F U^T
TFD(beta) built in the real eigenbasis {phi_a, eps_a} of one side's h:
  n_a = Fermi-Dirac,  G_LL = G_RR = phi n phi^T,  F_LR = phi sqrt(n(1-n)) phi^T
(sign of F_LR is a gauge phase of the |11> convention — documented, irrelevant).
All t=0 matrices are REAL; Theta_L therefore acts trivially on the initial state and
the orientation flip lives purely in the dynamics (see orientation-flip-evolution).

Majorana ordering for the scrambler: m1_j = c_j + c+_j at index j, m2_j = -i(c_j - c+_j)
at index 2N + j; covariance Gamma real antisymmetric with <g_a g_b> = delta_ab + i Gamma_ab.
"""
import numpy as np

SCRAMBLE_SEED = 20260720  # pre-registered single Haar draw shared by every run


def ring_hamiltonian(N, J=1.0):
    """Single-side 1D tight-binding ring: h[i,i+1] = h[i+1,i] = -J (PBC).
    Built by accumulation so the N=2 double-bond ring matches the Fock-space test."""
    h = np.zeros((N, N))
    for i in range(N):
        j = (i + 1) % N
        h[i, j] -= J
        h[j, i] -= J
    return h


def side_eigenbasis(h):
    """Real orthonormal eigenbasis of one side. Returns (eps, phi[site, mode])."""
    eps, phi = np.linalg.eigh(h)
    return eps, phi


def fermi_dirac(eps, beta):
    return 1.0 / (1.0 + np.exp(beta * eps))


def build_tfd(N, beta, J=1.0):
    """Fermionic TFD over the doubled lattice as (G, F). Basis-independent within
    degenerate eigenspaces (G, F blocks are matrix functions of h)."""
    h = ring_hamiltonian(N, J)
    eps, phi = side_eigenbasis(h)
    n = fermi_dirac(eps, beta)
    thermal = phi @ np.diag(n) @ phi.T
    cross = phi @ np.diag(np.sqrt(n * (1.0 - n))) @ phi.T
    G = np.zeros((2 * N, 2 * N))
    G[:N, :N] = thermal
    G[N:, N:] = thermal
    F = np.zeros((2 * N, 2 * N))
    F[:N, N:] = cross          # <c_L c_R>
    F[N:, :N] = -cross.T       # antisymmetry
    return {"N": N, "beta": beta, "J": J, "h": h, "eps": eps, "phi": phi,
            "n": n, "G": G.astype(complex), "F": F.astype(complex)}


def theta_l_conjugation(G, F):
    """Impl-B anti-unitary map K: entrywise complex conjugation of (G, F).
    Legal because h is real in the position basis; see plan for why a strictly
    L-local anti-unitary does not exist basis-independently."""
    return np.conj(G), np.conj(F)


# ---------- Majorana <-> complex conversion (for the L-sector scrambler) ----------

def majorana_from_complex(G, F):
    """Gamma (4M x 4M real antisymmetric) from (G, F) over M complex modes."""
    M = G.shape[0]
    ImG, ImF = np.imag(G), np.imag(F)
    ReG, ReF = np.real(G), np.real(F)
    g11 = 2.0 * (ImF - ImG)
    g22 = -2.0 * (ImF + ImG)
    g12 = -(2.0 * ReF + 2.0 * ReG - np.eye(M))
    Gamma = np.zeros((2 * M, 2 * M))
    Gamma[:M, :M] = g11
    Gamma[M:, M:] = g22
    Gamma[:M, M:] = g12
    Gamma[M:, :M] = -g12.T
    return Gamma


def complex_from_majorana(Gamma):
    """Inverse of majorana_from_complex."""
    M = Gamma.shape[0] // 2
    g11, g22, g12 = Gamma[:M, :M], Gamma[M:, M:], Gamma[:M, M:]
    Mm = 0.5 * (np.eye(M) - g12)
    ReG, ReF = 0.5 * (Mm + Mm.T), 0.5 * (Mm - Mm.T)
    ImG, ImF = -0.25 * (g11 + g22), 0.25 * (g11 - g22)
    return (ReG + 1j * ImG), (ReF + 1j * ImF)


def haar_orthogonal(dim, rng):
    """Haar-distributed O(dim) via QR with sign fix."""
    A = rng.standard_normal((dim, dim))
    Q, R = np.linalg.qr(A)
    return Q * np.sign(np.diag(R))[None, :]


def scramble_l_sector(state, seed=SCRAMBLE_SEED):
    """Haar-random Gaussian unitary on side L only: O(2N) rotation of the L Majoranas.
    Preserves rho_R and global purity exactly (gates G5/G2 verify)."""
    N = state["N"]
    Gamma = majorana_from_complex(state["G"], state["F"])
    idx = np.concatenate([np.arange(N), 2 * N + np.arange(N)])  # m1_L then m2_L
    O = haar_orthogonal(2 * N, np.random.default_rng(seed))
    Ofull = np.eye(4 * N)
    Ofull[np.ix_(idx, idx)] = O
    G, F = complex_from_majorana(Ofull @ Gamma @ Ofull.T)
    out = dict(state)
    out["G"], out["F"] = G, F
    return out


# ---------- entropy / purity / spectra from (G, F) blocks ----------

def nambu_block(G, F, idx):
    """Hermitian [[I-G_A, F_A], [F_A+, G_A^T]] for site set A = idx.
    Eigenvalues lie in [0,1] and pair as (lam, 1-lam)."""
    ix = np.ix_(idx, idx)
    GA, FA = G[ix], F[ix]
    top = np.hstack([np.eye(len(idx)) - GA, FA])
    bot = np.hstack([FA.conj().T, GA.T])
    Nmb = np.vstack([top, bot])
    return 0.5 * (Nmb + Nmb.conj().T)


def nambu_spectrum(G, F, idx):
    lam = np.linalg.eigvalsh(nambu_block(G, F, idx))
    return np.clip(lam, 0.0, 1.0)


def entropy(G, F, idx):
    """Von Neumann entropy of the site set idx (counts each (lam, 1-lam) pair once
    because the sum runs over BOTH partners)."""
    lam = nambu_spectrum(G, F, idx)
    lam = lam[lam > 1e-300]
    return float(-np.sum(lam * np.log(lam)))


def purity(G, F, idx):
    lam = nambu_spectrum(G, F, idx)
    return float(np.exp(0.5 * np.sum(np.log(lam**2 + (1.0 - lam) ** 2))))


def ent_spectrum_top(G, F, idx, k=8):
    """Top-k Nambu eigenvalues (descending) — the entanglement-spectrum probe."""
    lam = np.sort(nambu_spectrum(G, F, idx))[::-1]
    return lam[:k]


def global_purity_defect(G, F):
    """max lam(1-lam) over the full system — 0 iff the global state is pure."""
    lam = nambu_spectrum(G, F, np.arange(G.shape[0]))
    return float(np.max(lam * (1.0 - lam)))
