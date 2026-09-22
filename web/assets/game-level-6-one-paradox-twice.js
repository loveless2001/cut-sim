// Level 6 — limited scope comparison between relational clocks and island calculations.
// The analogy is limited and derives neither result. Hand-authored, no physics sim.
(() => {
  const $ = id => document.getElementById(id);
  const moved = new Set();

  const DEMAND = {
    time: "One absolute time was requested without specifying a clock or relational observable. A stationary constraint in some formulations makes that request underspecified; S_U = 0 alone does not establish stationarity.",
    bh: "Radiation entropy was treated as a complete statement about the global state. It is a subsystem quantity and does not by itself determine global purity or unitarity.",
  };
  const MOVE = {
    time: "One relational construction chooses a clock subsystem C and asks how R's state correlates with C's readings (Page–Wootters). This is a specific physical realization, not a consequence of reduced entropy or of the operational core alone.",
    bh: "The island prescription extremizes generalized entropy over candidate saddles in controlled gravitational models. This is not merely choosing the 'best cut': its gravitational area term and path-integral derivation are essential inputs absent from this game.",
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
        CutGame.complete(6, "scope declared");
        setTimeout(() => {
          $("l6-bh-out").textContent += " The comparison is limited to scope discipline. The island rule comes from gravitational calculations and is not derived by this framework.";
        }, 600);
      }
    }));
  }

  CutGame.register(6, { init });
})();
