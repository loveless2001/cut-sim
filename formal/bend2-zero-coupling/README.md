# Bend 2: zero-coupling operational slice

**Status:** a checked theorem about a finite classical access model. It formalizes a
specific instance of [OC-R3](../../docs/operational-core.md#oc-r3)
and the access logic behind the zero-coupling orientation experiment. It does **not**
prove the fermionic TFD construction or its Python implementation.

Run the gate from this directory:

```bash
bend --version                 # checked with Bend 2.0.16
bend PROOF.bend                # All terms check.
```

`Model.bend` defines a joint two-bit L/R distribution using exact natural-number
weights. `reduce_r` sums over L. `Procedure` is a finite tree: an R-only binary
instrument runs at each node, and its next instrument can depend on the recorded
R outcome. An instrument contains exact two-by-two transition matrices for both
outcomes. `run_r` keeps subnormalized branch weights and returns a tree of
complete transcript weights. A leaf's probability is its weight divided by its
recorded denominator when the input and instruments are normalized.

Normalization means the initial joint weights sum to a positive `base_denom`, each
instrument denominator is positive, and the two outcome matrices' combined
column sums equal that denominator. `valid_instrument` and `valid_procedure`
encode the instrument condition; the laws check normalization of the concrete
states and validity of the concrete adaptive procedure. The general equivalence
law itself holds for all natural-number weights, including invalid instruments;
the valid procedures are a subset.

`LAWS.bend` states, and `PROOF.bend` checks:

- For **every finite adaptive procedure in this model**, any two joint states
  with the same R marginal have the same complete weighted transcript tree.
  The model's zero-coupling premise is explicit: each instrument receives only
  the R state, and the L data never enters an R transition or readout.
- Any number of the declared L-local bit flips preserves the R marginal and
  every such transcript. The proof uses induction and exact addition laws.
- Two normalized, distinct joint distributions have the same R marginal but a
  different joint readout. A concrete adaptive protocol has two nonzero
  transcripts, each with probability one half, in both distributions.

The first result is conditional on the *access and dynamics encoded here*.
This model has a classical two-state R system, exact counts, binary outcomes,
and finite protocols. It has no quantum amplitudes, density matrices, partial
trace, Hamiltonian, spatial locality, clock, or phase reference. The L-local
bit flip is an example of an invisible complement operation, not a formal model
of the experiment's time-orientation flip. The proof does not establish that
the existing [orientation simulation](../../orientation-test.md) implements
these assumptions, nor does it establish a result for nonzero coupling.

The next formal bridge would define finite-dimensional complex density matrices,
tensor-local evolution, partial trace, and R-local instruments; prove the
reduced-state and transcript laws there; then check the simulation's state,
control, and readout mappings against that specification. Numerical gates remain
separate evidence about the Python implementation.
