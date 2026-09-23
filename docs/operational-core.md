# The Cut — Operational Core and Limits of Inference

- **Status:** Proposed foundation for this research programme
- **Role:** Operational core, not a definition of time and not a replacement for the ontology of The Cut
- **Version:** 0.5 (2026-09-23; causal-accessibility revision)

This module states the conditions under which a system can distinguish, record,
compare, and test models from within its actual range of access. It does not deny a
reality outside an observer, and it does not infer the structure of that reality merely
from what the observer can represent or fit.

The commitments below are a **proposed basis for this research programme**. No proof
is claimed that they are the unique minimal axioms, that each is logically independent
of the others, or that every possible theory must use this formulation. Here an
*observer* may be any physical system capable of making and retaining records;
consciousness is not assumed.

## 1. Three layers of the framework

| Layer | Work | Limit |
|---|---|---|
| **Operational core** | Specifies distinguishability, records, procedure composition, comparison rules, and the scope of causal inference | Does not by itself supply dynamics or an ontology of the whole |
| **Physical realizations** | Proposes physical structures that realize those capacities | Must declare additional assumptions; the present pure-state, unitary quantum model is one realization |
| **Phenomena and interpretations** | Studies clocks, arrows, records, shareability, and experience within a realization | Must not treat those phenomena as consequences of the operational core alone |

The layers are connected by **adding assumptions and testing consequences**, not by an
automatic chain of deduction. Evidence may reject a realization or an interpretation
without rejecting the whole operational core. Conversely, operational adequacy does
not uniquely select an ontology.

Ontology therefore retains a separate role. It may propose what exists, but agreement
between a representation and accessible data is not evidence that the ontology has
been uniquely determined.

## 2. Foundation

**Definition.** A system can investigate what it can access when it can register
differences, retain traces for comparison, compose operations into procedures, and
identify relations stable enough to test predictions.

**Limitation.** Conclusions established from inside the system must be tied to their
operational scope, recording channels, preparation conditions, and corresponding
errors. They do not automatically determine a unique structure for the whole beyond
that scope.

**Definition.** Two models are operationally equivalent for a test scope when they
predict the same distribution over every accessible record for every procedure in that
scope. This equivalence neither asserts that the models share an ontology nor
guarantees that they remain equivalent when the test scope is enlarged.

## 3. Operational assumptions

<a id="oc-a1"></a>
### OC-A1 — Distinguishability

**Operational assumption.** There is at least one procedure for which two situations
produce outcomes, or distributions of records, that are distinguishable within a
stated error model.

This does not assume that an observer can read the complete state, discriminate
perfectly in one trial, or access an absolute set of object-properties. Without a
distinguishable difference, there is no data available to that observer for that
comparison.

<a id="oc-a2"></a>
### OC-A2 — Recordability and comparability

**Operational assumption.** Some traces persist long enough to enter comparisons, and
there are criteria for identifying procedures as equivalent in the properties relevant
to a test.

Memory need not be infallible, storage need not be permanent, and a record need not
contain a complete history. The relation “this trace is a record of that source” still
requires a model and tests. Agreement among all observers about every record is not
assumed.

<a id="oc-a3"></a>
### OC-A3 — Composability of procedures

**Operational assumption.** Some operations can be composed into structured
procedures: preparation, interaction, readout, and comparison. Not every operation is
required to compose with every other.

**Foundational debt.** Composition and retained traces already carry a primitive local
ordering structure. This core does not derive all of time from a basis with no order
relations at all. The local structure does not by itself imply a universal linear
order, a standard duration, or a thermodynamic arrow.

<a id="oc-a4"></a>
### OC-A4 — Restricted regularity

**Operational assumption.** Within a specified domain, equivalent procedures exhibit
statistical relations stable enough for calibration and for testing predictions on
further trials.

This does not assume deterministic outcomes, independent and identically distributed
trials, or laws invariant at every place and epoch. Temperature, context, and
preparation history must be included when they affect the records. OC-A4 is a bounded
inductive commitment, not a theorem about the universe as a whole.

## 4. Constraints on inference

<a id="oc-r1"></a>
### OC-R1 — Predictive consistency

**Empirical constraint.** A model supplies predictions in the form

\[
P_M(r\mid Q).
\]

`Q` is a specified procedure, including relevant preparation conditions, operations,
readout channels, and—where applicable—a policy that selects later operations from
earlier records. `r` is the **complete accessible transcript** of the procedure, not
only a final-state snapshot. `M` is the model.

When probabilities are used, they must be non-negative, normalized, and consistent
under coarse-graining of outcomes for the same procedure. This requirement does not
presume one joint distribution for incompatible measurements or for unobserved
counterfactual outcomes. A probabilistic representation also does not decide whether
chance is fundamental in the ontology.

<a id="oc-r2"></a>
### OC-R2 — Representation invariance

**Empirical constraint.** Relabelling, changing units, or changing coordinates—while
transforming the model consistently—must not change predictions for the **same physical
procedure**.

This is not the claim that every cut is equivalent. A change of description must be
distinguished from a change of apparatus, access rights, or coupling. Two descriptions
of one measurement must agree; two physically different measurements need not.

<a id="oc-r3"></a>
### OC-R3 — Scope-limited identifiability

**Definition.** Let `Q_O` (written \(\mathcal Q_O\)) be the procedures available to
observer `O`. Then

\[
M_1\sim_{\mathcal Q_O}M_2
\quad\Longleftrightarrow\quad
P_{M_1}(r\mid Q)=P_{M_2}(r\mid Q)
\quad\text{for every }Q\in\mathcal Q_O\text{ and every accessible }r.
\]

Three claims must be kept separate:

1. the available data have not yet distinguished two models;
2. equivalence has been proved for every procedure in a defined class; and
3. the models have the same ontology.

The third does not follow from either of the first two. Equal reduced states at one
instant do not guarantee equivalence under all future interactions. Any approximate
equivalence must state its metric, error tolerance, and experimental budget; a larger
sample or an expanded procedure class may expose a previously sub-threshold difference.

“Inaccessible in this configuration” must not be rewritten as “forever unknowable by
humans.” A finite numerical null is not an exact proof covering every possible test.

For causal structure, let \(C_M=(E,\leadsto_M)\) be a model-level influence structure
and let \(\widehat C_O\) be an observer's reconstruction from transcripts of
\(\mathcal Q_O\). The research question is how much of \(C_M\) is identifiable
under that access. A missing detected edge is not evidence that the model has no
edge; a reported edge can also be mistaken when controls or errors are inadequate.

## 5. Model cut and operational access

**Definition — model cut.** A model cut is the way a model divides a system, its
complement, and the relevant interactions. In the present quantum realization it
includes a chosen tensor factorization, together with any separately declared state,
Hamiltonian split, locality structure, and coupling assumptions.

**Definition — operational access.** Operational access consists of the preparations,
controls, readout channels, records, resolutions, and resources actually available to
an observer. The class \(\mathcal Q_O\) is generated from this access.

The definition of a cut is not replaced by a set of operations. A physical realization
must explain how its cut, state, couplings, and apparatus produce a given access class.
The map need not be one-to-one: one cut may support different apparatus and access
levels, while the same accessible statistics need not identify a unique underlying
cut.

Operational indistinguishability also does not prove that no physical principle could
select a cut. Any no-selection conclusion must retain the object and assumptions of its
own argument.

**Limitation — no privilege outside the model.** In an endogenous test, the clock,
memory, phase reference, preparation source, and signals must be declared. Simulator
steps, the global state matrix, exact lattice coordinates, and debug variables belong
to the model builder. They are not automatically records available to the modeled
observer.

## 6. Causal accessibility and scoped ordering

**Definition — model-level influence.** In a physical realization \(M\), let
\(e\) and \(f\) denote declared events, operational stages, or localized
intervention/readout regions. Write \(e\leadsto_M f\) when an admissible
controlled variation at \(e\) can change the distribution of an accessible
record at \(f\), with the rest of the procedure held fixed. Schematically,

\[
e\leadsto_M f\quad\Longleftrightarrow\quad
\exists x,x',Q,r_f:\
P_M(r_f\mid \operatorname{do}(x),Q)\ne
P_M(r_f\mid \operatorname{do}(x'),Q).
\]

Here \(x,x'\) are alternative interventions or preparations at \(e\), \(Q\)
fixes the remaining declared conditions (including the readout at \(f\)), and
\(r_f\) is a record associated with \(f\). The `do` notation stresses a
controlled change, not mere conditioning on an observed value. Admissibility,
localization, dynamics, and the error model belong to the realization; the
operational core alone does not supply them. Correlation from a common source
does not establish either directed influence.

**Observer-identifiable influence.** Write \(e\leadsto_{\mathcal Q_O}f\) only
when an observer's available interventions, detectors, clocks, references,
records, resolution, and trial budget support that inference under a declared
decision rule. This is a scoped reconstruction of \(\leadsto_M\), not a second
physical coupling created by the observer. In general
\(\leadsto_{\mathcal Q_O}\ne\leadsto_M\). A model edge can be inaccessible or
below the observer's detection threshold; finite data can also support a false
edge. The cut and access class therefore remain different objects.

**Derived reachability.** Define \(e\prec_M f\) when there is a directed path
of one or more \(\leadsto_M\) edges from \(e\) to \(f\). This is a transitive
reachability relation. In an acyclic domain it is a *strict* partial order
(its reflexive closure is a partial order). If the realization permits causal
loops, reachability need not be antisymmetric or irreflexive; retain it as a
directed reachability structure. Acyclicity must be assumed or shown. Unrelated
events can remain incomparable, with no universal linear order.

This construction uses the primitive local sequencing already admitted by
OC-A3. It does not derive directed order from an entirely order-free basis,
nor does ordering alone supply duration, a thermodynamic arrow, or experience.

## 7. Four tasks concerning time

These are related questions. They are neither an automatic sequence of deductions nor
asserted to be fully independent.

| Task | Question and required structure | Limit |
|---|---|---|
| **Ordering and influence** | Which stages can affect which others? Use local sequencing, a declared intervention model, dynamics/coupling, preparations, and controls to obtain \(e\prec_M f\). | Neither entropy monotonicity, a universal coordinate time, an absolute clock, nor a total order follows. |
| **Duration and clocks** | How much calibrated physical change accumulates along a causal chain or worldline? Add a reference system, read/count rule, calibration domain, and clock-comparison model. | Ordering alone supplies no seconds; proper time requires a suitable relativistic model. |
| **Arrow and records** | Why are histories and records statistically asymmetric under reversal? Specify boundary/preparation conditions, environment, coarse-graining, entropy production or loss of accessible information, and record formation, persistence, and recoverability. | Do not define the arrow by entropy increase and count that increase as its explanation. |
| **Temporal judgement / experience** | How does an observer infer before/after, duration, and “now” from signals and retained records? Model memory, integration, prediction, belief update, and report. | Physical ordering does not require this layer; a processing model alone is not a solution to consciousness. |

The symbols and kinds of quantity must remain distinct:

- `t`: a parameter in a dynamical model;
- \(\prec_M\): model-relative causal reachability, with no duration attached;
- `S_A`: reduced entropy for a specified subsystem and state;
- a physical clock reading: the output of a calibrated physical procedure;
- proper time: the relativistic quantity in a domain where the relevant spacetime model applies;
- \(\tau_A^{\mathrm{ent}}\): a candidate *entropic orientation* label, usable only on a
  stated history segment where the relevant entropy is sufficiently monotone.

“Time as forgetting” is a **model-dependent, conditional hypothesis about arrow
and record asymmetry**: asymmetric retention or loss of causal records may help
explain an embedded observer's experienced arrow along an already defined
history. When \(S_A\) is sufficiently monotone on a declared interval,
\(\tau_A^{\mathrm{ent}}\) may label its entropic orientation. It neither defines
the underlying reachability relation nor supplies seconds, a universal clock,
or record formation. A history can have \(e_1\prec e_2\prec e_3\) even when
\(S_A(e_1)=S_A(e_3)\) or entropy temporarily decreases. Recurrence limits an
entropic label; it does not erase the causal history.

## 8. Worked examples

### 8.1 Clock matching without absolute time

**Example.** Between two markers defined by a procedure, clock A records 100 ticks while
clock B usually records 97. The relation can be calibrated, assigned an uncertainty,
and tested on new trials. It does not show that A measures absolute time. If a mere
change of description preserves every record and the 100:97 relation, OC-R2 forbids
presenting that relabelling as a measured difference.

### 8.2 Entropy does not register every change

**Counterexample.** Consider

\[
\lvert\psi(\phi)\rangle =
\frac{\lvert0\rangle+e^{-i\phi}\lvert1\rangle}{\sqrt 2}.
\]

Every member of the family is pure and has von Neumann entropy zero, yet a measurement
in an appropriate relative-phase basis can have outcome probability
\(\cos^2(\phi/2)\). The measurement basis, phase reference, and preparation relation
must be physically declared: this is not observation of an unobservable global phase
and does not provide a clock without additional structure. It is a counterexample to using entropy as an
indicator of every change, not a derivation of the origin of time.

### 8.3 Penrose diagrams: representation and access

A Penrose diagram is a conformal representation of a *specified spacetime
model*, not a literal picture. Its compactification can put infinity at a
finite drawing position while retaining the model's null directions, causal
reachability, horizons, and causal boundaries. Drawing distances, finite
placement of infinity, coordinate shape, and most visual angles are not metric
measurements; only the null-direction convention carries causal meaning.

The full diagram is a **model-level causal completion**. An embedded observer
does not see it directly. The observer has signals, interventions, records,
and local instruments and may reconstruct only a partial causal structure
under \(\mathcal Q_O\). The diagram illustrates OC-R2 and OC-R3: a change of
coordinates need not change causal content, while a model-builder's complete
representation is not automatically an accessible record. See [Sbierski, *General Relativity II*, §3.2](https://www.maths.ed.ac.uk/~jsbiersk/assets/LectureNotesGRII.pdf) for the conformal compactification construction.

## 9. Assumption ledger

| Commitment | Role | Scope | Consequence or test | Not inferred |
|---|---|---|---|---|
| OC-A1 distinguishability | Operational assumption | A stated comparison and error model | At least one procedure separates the alternatives | Complete-state access or perfect single-shot discrimination |
| OC-A2 recordability/comparability | Operational assumption | Specified traces and equivalence criteria | Enables repeatable comparison and audit | Infallible memory, complete history, or universal agreement |
| OC-A3 composability | Operational assumption | Declared preparation–interaction–readout chains | Makes transcript-bearing tests possible | A globally linear order or the origin of time |
| OC-A4 restricted regularity | Operational assumption | A stated calibration and application domain | Supports out-of-sample tests within that domain | Determinism, IID trials, or universal laws |
| Model-level causal accessibility \(\leadsto_M\) | Definition conditional on a physical realization | Declared events, interventions, fixed conditions, dynamics, and records | Test whether a controlled change at one stage alters a later record distribution | Influence from correlation alone, acyclicity, or a universal time coordinate |
| Observer reconstruction \(\widehat C_O\) | Inference under an access and error model | \(\mathcal Q_O\), resolution, references, and finite trial budget | Compare detectable edges and reachable regions with a declared model | Identity with \(C_M\), or absence of an edge from a null result |
| Reachability \(\prec_M\) | Derived relation | Directed paths of model-level influence; acyclicity only where established | Partial ordering in an acyclic domain | Duration, total order, or arrow from reachability alone |
| Chosen cut and access map | Model assumption | A particular realization and apparatus | Generates \(\mathcal Q_O\); must expose observer-visible channels | A unique cut, or a one-to-one cut/access map |
| Probability model \(P_M(r\mid Q)\) | Model assumption constrained by OC-R1 | Declared procedures and transcripts | Normalization and coarse-graining checks; empirical calibration | Fundamental ontic randomness or joint counterfactual values |
| Global purity and unitary dynamics | Model assumption in the current quantum realization | The models and simulations that explicitly adopt them | Purity, reversibility, and numerical conservation checks | Stationarity, time-reversal symmetry, or the actual state of the universe |
| Clock calibration | Model assumption plus empirical constraint | Reference, readout rule, and calibration domain | New-trial clock comparisons such as 100:97 | Absolute time or universal seconds |
| Arrow / record conditions | Model assumption | Boundary/preparation condition, environment, coarse-graining, and record maintenance | Tests of history asymmetry, entropy, persistence, and recoverability | Causal order or a universal arrow from entropy alone |
| Temporal judgement | Model assumption | A specified trace-integration and reporting system | Compare interaction, record, and reported order | Conscious experience in general |

## 10. Limits and relation to the current experiments

- Global purity implies \(S_U=0\); it does not imply stationarity or the absence of all
  internal temporal relations. It only makes that global entropy unusable as a varying
  clock indicator.
- Unitarity supplies reversible evolution. Time-reversal symmetry is a separate
  condition on the dynamics and the transformation of states and observables.
- Given a state and dynamics, the sign of an entropy change can be calculated. What the
  entropy functional alone does not supply is a universal macroscopic arrow.
- A coordinate or manifold description does not grant the ability to reverse a
  physical history. Choosing a monotone index assumes or verifies monotonicity in a
  domain; it does not explain the asymmetry or produce causal reachability.
- Similar formulas for Shannon and von Neumann entropy do not identify uncertainty,
  information transfer, duration, and record order.
- Recording does not universally imply an increase in the entropy of the observer's
  reduced state. Preparation, correlations, environment, erasure, and resources must
  be modeled.

The ruler-cancellation and orientation experiments remain tests of their declared
quantum realizations and operational batteries. Their stored data, preregistered gates,
and verdicts are unchanged. In particular, an orientation null at zero cross-cut
coupling applies to that access class and setup; it is not an ontological identity, a
general gauge redundancy of every theory, or a claim about watching a star run
backwards. The measured crossover belongs to the tested model, state, observables, and
parameter range; it does not say that every nonzero coupling exposes every distinction.

The 2026-09-22 targeted follow-up gives a concrete access comparison in the
same declared realization. The original battery's weak-coupling orientation
response is approximately quadratic, while a new pair-sensitive local
reference gives an approximately linear response; the zero-coupling null
remains. The reference, shared preparation phase, and joint readout are extra
apparatus. This shows that *identifiable* influence depends on the access
class, not that physical causality or ontology changes when apparatus changes.
The measured powers retain their stated parameter ranges and fit limits.

The existing construction tracks two unresolved inputs, historically called “the two
turtles”: arrow conditions and cut selection. This module does not prove that all
possible theories contain exactly two foundational assumptions, and it does not close
cut selection, the arrow, or intersubjectivity.

## 11. Future work, not a deliverable of this revision

Possible later work includes enlarging operational procedure classes, studying how
different realizations induce the same access, and designing explicit tests that
separate causal order, entropic orientation, and calibrated duration. A possible
**causal reconstruction pilot** would use a local brickwork quantum circuit or
cellular automaton with a strict finite causal cone, hide simulator steps and
exact coordinates from the observer, and allow tagged interventions and detector
records. Stages could add restricted detectors, expanded detectors and references,
an endogenous clock, then an asymmetric environment with persistent records.
Compare \(C_M=(E,\prec_M)\) with \(\widehat C_O\) as access expands; possible
future diagnostics include detectable/missed/false edges, reachability agreement,
cone boundaries, and uncertainty over causal models. These metrics and the
experiment are **not implemented** in this revision. No new three-state loop or
origin-of-time laboratory is introduced here.

## 12. References and provenance

These sources motivate parts of the operational vocabulary; none proves this module as
a unique or minimal axiom system.

- Lucien Hardy, *Quantum Theory From Five Reasonable Axioms*,
  [arXiv:quant-ph/0101012](https://arxiv.org/abs/quant-ph/0101012) — an operational
  reconstruction programme; cited as precedent, not as this module's derivation.
- Giulio Chiribella, Giacomo Mauro D'Ariano, and Paolo Perinotti, *Informational
  derivation of Quantum Theory*,
  [arXiv:1011.6451](https://arxiv.org/abs/1011.6451) — operational tests and
  informational principles leading to a specific physical realization.
- Bianca Dittrich, *Partial and Complete Observables for Hamiltonian Constrained
  Systems*, [arXiv:gr-qc/0411013](https://arxiv.org/abs/gr-qc/0411013) — relational
  observables in constrained systems.
- Don N. Page and William K. Wootters, *Evolution without evolution: Dynamics described
  by stationary observables*,
  [Phys. Rev. D 27, 2885 (1983)](https://doi.org/10.1103/PhysRevD.27.2885) — dynamics
  expressed relative to internal clock readings; it does not identify clocks with
  reduced entropy in general.
- Harold Ollivier, David Poulin, and Wojciech H. Zurek, *Environment as a Witness:
  Selective Proliferation of Information and Emergence of Objectivity in a Quantum
  Universe*, [arXiv:quant-ph/0408125](https://arxiv.org/abs/quant-ph/0408125) — records,
  redundancy, and operational objectivity in a particular decoherence framework.

The framework's quantum realization and its older epistemic tags remain specified in
[`cut_spec.tex`](cut_spec.tex). Numerical claims and their historical scope remain in
[`results-writeup.md`](results-writeup.md) and
[`results-writeup-orientation.md`](results-writeup-orientation.md).
