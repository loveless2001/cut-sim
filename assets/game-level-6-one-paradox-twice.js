// Level 6 — "Two views of one paradox" (explicitly analogy-only): the problem of
// time and the black-hole information paradox presented as the same move — a
// cut-relative quantity mistaken for an absolute one. Hand-authored, no physics sim.
(() => {
  const $ = id => document.getElementById(id);
  const moved = new Set();

  const DEMAND = {
    time: "You demanded THE time of the whole. The constraint answers: H|Ψ⟩ = 0 — the global state has nothing to evolve with respect to. Asked as an absolute question, it has no answer. (You met this wall in Level 1; it hasn't moved.)",
    bh: "You demanded THE entropy of the radiation, as an absolute fact about the radiation alone. Computed naively it rises forever, crashing through the bound a unitary theory must respect. Asked this way, the question generates the paradox.",
  };
  const MOVE = {
    time: "Reframed: pick a cut — a clock subsystem C and the rest R — and ask how R's state correlates with C's readings. Conditional evolution appears (the Page–Wootters construction). Time wasn't lost; it was never a property of the whole. It lives at the cut, like your Level-1 clock.",
    bh: "Reframed: ask for the entropy given the best cut — minimize over ways of carving the interior in or out (the island prescription). The answer follows the Page curve and unitarity survives. The 'paradox' was insisting one fixed cut's bookkeeping was an absolute fact.",
  };

  function init() {
    document.querySelectorAll(".l6-demand").forEach(b => b.addEventListener("click", () => {
      $("l6-" + b.dataset.p + "-out").textContent = DEMAND[b.dataset.p];
    }));
    document.querySelectorAll(".l6-move").forEach(b => b.addEventListener("click", () => {
      const p = b.dataset.p;
      $("l6-" + p + "-out").textContent = MOVE[p];
      moved.add(p);
      if (moved.size === 2) {
        CutGame.complete(6, "one move, two locks");
        setTimeout(() => {
          $("l6-bh-out").textContent += " — Same move, both panels. One badge: “one move, two locks.” And to keep the conscience clear: the island rule was discovered by gravitational path integrals, not by this framework; what you just saw is a shared shape, not a derivation.";
        }, 600);
      }
    }));
  }

  CutGame.register(6, { init });
})();
