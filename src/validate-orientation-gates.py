"""Pre-registered sanity gates G0-G9 — ALL must pass before the experiment runs.

G0 (extra) machinery vs dense Fock-space many-body computation at N=3 (JW), < 1e-10.
G1 rho_R of the TFD equals the exact thermal state, < 1e-12.
G2 S_L = S_R < 1e-10; global purity exact (max lam(1-lam) < 1e-12).
G3 Theta_L leaves rho_R(0) invariant < 1e-12; Impl A/B trajectory agreement < 1e-10.
G4 g=0: rho_R(t) stationary-thermal under O+ and O-, and equals single-sided
   evolution of rho_R, < 1e-10 at all sampled t.
G5 scrambled purification reproduces rho_R < 1e-12 at t=0; global purity preserved.
G6 dynamics-extracted clock beat matches the analytic two-mode gap, rel < 1e-8.
G7 every god's-eye discriminator fires (d > 1e-6) at g = 0.
G8 every internal battery item fires at g = 0.1 on BOTH axes (orientation, purif.).
G9 number and energy conserved under evolution, relative drift < 1e-10.

Run: .venv/bin/python3 src/validate-orientation-gates.py   (exit 0 iff all pass)
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


ts = _load("tfd-gaussian-state-construction.py", "tfd_state")
oe = _load("orientation-flip-evolution.py", "orientation_evolution")
bt = _load("internal-battery-side-r.py", "internal_battery")
ge = _load("gods-eye-discriminators.py", "gods_eye")

FAILURES = []
N_GATE, BETA_GATE = 128, 1.0


def gate(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)
    if not ok:
        FAILURES.append(name)


# ---------- G0: dense Fock-space cross-check (Jordan-Wigner, 6 modes, dim 64) ----------

def fock_operators(M):
    a = np.array([[0.0, 1.0], [0.0, 0.0]])
    Z = np.diag([1.0, -1.0])
    I2 = np.eye(2)
    ops = []
    for j in range(M):
        mats = [Z] * j + [a] + [I2] * (M - 1 - j)
        op = mats[0]
        for m in mats[1:]:
            op = np.kron(op, m)
        ops.append(op)
    return ops


def gate_g0():
    from scipy.linalg import expm
    Nl, beta, s, g, t_ev = 3, 0.7, -1, 0.37, 3.1
    st = ts.build_tfd(Nl, beta)
    C = fock_operators(2 * Nl)
    vac = np.zeros(2 ** (2 * Nl))
    vac[0] = 1.0
    psi = vac
    for a_mode in range(Nl):
        cL = sum(st["phi"][x, a_mode] * C[x].conj().T for x in range(Nl))
        cR = sum(st["phi"][x, a_mode] * C[Nl + x].conj().T for x in range(Nl))
        n_a = st["n"][a_mode]
        psi = (np.sqrt(1.0 - n_a) * psi + np.sqrt(n_a) * (cR @ (cL @ psi)))
    err_norm = abs(np.linalg.norm(psi) - 1.0)

    def corr(psi):
        M = 2 * Nl
        G = np.array([[psi.conj() @ (C[j].conj().T @ (C[i] @ psi)) for j in range(M)]
                      for i in range(M)])
        F = np.array([[psi.conj() @ (C[i] @ (C[j] @ psi)) for j in range(M)]
                      for i in range(M)])
        return G, F  # G[i,j] = <c+_j c_i>, F[i,j] = <c_i c_j> by construction

    Gf, Ff = corr(psi)
    e_state = max(np.abs(Gf - st["G"]).max(), np.abs(Ff - st["F"]).max())

    # entropies: qubit partial trace (L modes are the first JW factors)
    psi_mat = psi.reshape(2 ** Nl, 2 ** Nl)
    lamL = np.linalg.eigvalsh(psi_mat @ psi_mat.conj().T)
    lamL = lamL[lamL > 1e-14]
    S_L_fock = float(-np.sum(lamL * np.log(lamL)))
    S_L_mach = ts.entropy(st["G"], st["F"], np.arange(Nl))
    e_ent = abs(S_L_fock - S_L_mach)

    # evolution under a coupled, orientation-flipped variant
    H1 = oe.build_variant_h1(Nl, s, g, w=2)
    H_mb = sum(H1[i, j] * (C[i].conj().T @ C[j]) for i in range(2 * Nl)
               for j in range(2 * Nl))
    psi_t = expm(-1j * H_mb * t_ev) @ psi
    Gt_f, Ft_f = corr(psi_t)
    evo = oe.VariantEvolution(H1, st["G"], st["F"])
    Gt_m, Ft_m = evo.gf_full(t_ev)
    e_evo = max(np.abs(Gt_f - Gt_m).max(), np.abs(Ft_f - Ft_m).max())

    err = max(err_norm, e_state, e_ent, e_evo)
    gate("G0 Fock-space cross-check", err < 1e-10,
         f"norm {err_norm:.1e} state {e_state:.1e} entropy {e_ent:.1e} evo {e_evo:.1e}")


def main():
    gate_g0()

    N, beta = N_GATE, BETA_GATE
    st = ts.build_tfd(N, beta)
    Lix, Rix = np.arange(N), np.arange(N, 2 * N)
    rod = bt.rod_length()

    # G1 thermal R block
    thermal = st["phi"] @ np.diag(st["n"]) @ st["phi"].T
    e1 = np.abs(st["G"][N:, N:] - thermal).max()
    gate("G1 rho_R thermal", e1 < 1e-12, f"max err {e1:.2e}")

    # G2 pure global state, S_L = S_R
    S_L, S_R = ts.entropy(st["G"], st["F"], Lix), ts.entropy(st["G"], st["F"], Rix)
    pd = ts.global_purity_defect(st["G"], st["F"])
    gate("G2 purity + S_L=S_R", abs(S_L - S_R) < 1e-10 and pd < 1e-12,
         f"|S_L-S_R|={abs(S_L - S_R):.2e} purity defect {pd:.2e} (S_L={S_L:.3f})")

    # G3 Theta_L invariance of rho_R + Impl A/B equivalence (g=0 and g=0.1)
    Gc, Fc = ts.theta_l_conjugation(st["G"], st["F"])
    e3 = max(np.abs(Gc[N:, N:] - st["G"][N:, N:]).max(),
             np.abs(Fc[N:, N:] - st["F"][N:, N:]).max())
    e3b = 0.0
    for g in (0.0, 0.1):
        H1 = oe.build_variant_h1(N, -1, g)
        evoA = oe.VariantEvolution(H1, st["G"], st["F"])
        evoB = oe.ImplBEvolution(H1, st["G"], st["F"])
        allix = np.arange(2 * N)
        for t in (10.0, 40.0):
            e3b = max(e3b, np.abs(evoA.g_block(t, allix) - evoB.g_block(t, allix)).max(),
                      np.abs(evoA.f_block(t, allix) - evoB.f_block(t, allix)).max())
    gate("G3 Theta_L + impl A/B", e3 < 1e-12 and e3b < 1e-10,
         f"rho_R(0) invariance {e3:.2e}, A/B trajectory diff {e3b:.2e}")

    # G4 g=0 stationarity of rho_R under O+/O- vs single-sided thermal evolution
    e4 = 0.0
    for s in (+1, -1):
        evo = oe.VariantEvolution(oe.build_variant_h1(N, s, 0.0), st["G"], st["F"])
        for t in (13.7, 40.0):
            e4 = max(e4, np.abs(evo.g_block(t, Rix) - st["G"][N:, N:]).max(),
                     np.abs(evo.f_block(t, Rix) - st["F"][N:, N:]).max())
    gate("G4 g=0 rho_R(t) thermal-stationary", e4 < 1e-10, f"max err {e4:.2e}")

    # G5 scrambled purification
    scr = ts.scramble_l_sector(st)
    e5 = max(np.abs(scr["G"][N:, N:] - st["G"][N:, N:]).max(),
             np.abs(scr["F"][N:, N:]).max())
    pd5 = ts.global_purity_defect(scr["G"], scr["F"])
    gate("G5 scrambled rho_R identical", e5 < 1e-12 and pd5 < 1e-12,
         f"rho_R err {e5:.2e}, purity defect {pd5:.2e}")

    # G6 clock beat vs analytic two-mode gap (g=0, mirror, O+); clock prep kick
    Gk, Fk = bt.apply_clock_kick(st["G"], st["F"], N)
    evo_clk = oe.VariantEvolution(oe.build_variant_h1(N, +1, 0.0, carve=True), Gk, Fk)
    c1, _ = oe.cavity_specs(N)
    m = bt.clock_measurement(evo_clk, N, c1)
    e6 = abs(m["omega"] / m["gap_analytic"] - 1.0)
    gate("G6 clock vs analytic gap", e6 < 1e-8,
         f"rel err {e6:.2e} (|z0|={m['z0_abs']:.2e})")

    # G7 god's-eye discriminators fire at g = 0
    evoP = oe.VariantEvolution(oe.build_variant_h1(N, +1, 0.0), st["G"], st["F"])
    evoM = oe.VariantEvolution(oe.build_variant_h1(N, -1, 0.0), st["G"], st["F"])
    disc = ge.orientation_discriminators(evoP, evoM, N)
    disc["ge-complement"] = ge.complement_discriminator(st, scr)
    ok7 = all(v["fires"] for v in disc.values())
    gate("G7 god's-eye discriminators fire", ok7,
         " ".join(f"{k}={v['d']:.2e}" for k, v in disc.items()))

    # G8 every internal item fires at g = 0.1 on both axes
    def battery(state, s, g):
        mk = lambda **kw: oe.VariantEvolution(oe.build_variant_h1(N, s, g, **kw),
                                              state["G"], state["F"])
        Gk8, Fk8 = bt.apply_clock_kick(state["G"], state["F"], N)
        clk = oe.VariantEvolution(oe.build_variant_h1(N, s, g, carve=True), Gk8, Fk8)
        q = N // 2
        items, meta = bt.compute_internal_items(
            mk(), {V: mk(quench=(q, V)) for V in (1.0, 3.0)}, clk, N, rod)
        return items

    it_pm = battery(st, +1, 0.1)
    it_mm = battery(st, -1, 0.1)
    it_ps = battery(scr, +1, 0.1)
    d_or, _ = bt.battery_distances(it_pm, it_mm)
    d_pu, _ = bt.battery_distances(it_pm, it_ps)
    ok8 = all(d > ge.THETA_FIRE for d in d_or.values()) and \
        all(d > ge.THETA_FIRE for d in d_pu.values())
    gate("G8 battery fires at g=0.1", ok8,
         "orientation: " + " ".join(f"{k}={v:.1e}" for k, v in d_or.items()) +
         " | purification: " + " ".join(f"{k}={v:.1e}" for k, v in d_pu.items()))

    # G9 conservation
    e9 = 0.0
    for s in (+1, -1):
        evo = oe.VariantEvolution(oe.build_variant_h1(N, s, 0.1), st["G"], st["F"])
        for t in (10.0, 40.0):
            dn, de = evo.conservation_drift(t)
            e9 = max(e9, dn, de)
    evq = oe.VariantEvolution(oe.build_variant_h1(N, +1, 0.1, quench=(N // 2, 3.0)),
                              st["G"], st["F"])
    dn, de = evq.conservation_drift(40.0)
    e9 = max(e9, dn, de)
    gate("G9 number/energy conservation", e9 < 1e-10, f"max rel drift {e9:.2e}")

    print(f"\n{'ALL GATES PASS' if not FAILURES else 'GATES FAILED: ' + str(FAILURES)}",
          flush=True)
    return FAILURES


if __name__ == "__main__":
    sys.exit(0 if not main() else 1)
