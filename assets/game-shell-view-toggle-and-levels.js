// Core of "The Cut — the game": level registry, the god's-eye <-> cut view toggle
// (the game's central mechanic), level navigation, badge shelf, and the shared
// animation loop. Levels register via CutGame.register(n, def) where def may have
// { enter(), leave(), tick(dtSeconds), onView(view), onComplete() }.
const CutGame = (() => {
  const levels = new Map();          // n -> def
  const completed = new Set();
  const badges = [];                 // {n, name}
  let current = 1, view = "gods", switching = false, lastT = 0;

  const $ = id => document.getElementById(id);
  const css = k => getComputedStyle(document.documentElement).getPropertyValue(k).trim();

  function register(n, def) { levels.set(n, def); }

  // ---- view toggle with iris-style transition: the perspective SHIFT ----
  function setView(v, instant) {
    if (v === view || switching) return;
    const apply = () => {
      view = v;
      document.body.classList.toggle("view-gods", v === "gods");
      document.body.classList.toggle("view-cut", v === "cut");
      $("viewGods").classList.toggle("on", v === "gods");
      $("viewCut").classList.toggle("on", v === "cut");
      const def = levels.get(current);
      if (def && def.onView) def.onView(v);
    };
    if (instant) { apply(); return; }
    switching = true;
    const iris = $("iris");
    iris.classList.add("in");                       // fade to substrate-dark...
    setTimeout(() => { apply(); iris.classList.remove("in"); }, 190);
    setTimeout(() => { switching = false; }, 400);  // ...and re-emerge in the other view
  }

  // ---- level navigation ----
  function goto(n) {
    if (!levels.has(n) && n !== 7) return;
    const prev = levels.get(current);
    if (prev && prev.leave) prev.leave();
    current = n;
    document.querySelectorAll(".level").forEach(s => s.classList.remove("active"));
    const sec = $("lv" + n);
    if (sec) sec.classList.add("active");
    document.querySelectorAll("#levelNav button").forEach(b =>
      b.classList.toggle("here", +b.dataset.n === n));
    const def = levels.get(n);
    if (def && def.enter) def.enter();
    if (def && def.onView) def.onView(view);
    if (n === 7) renderFinale();
    window.scrollTo({ top: 0 });
  }

  function complete(n, badgeName) {
    if (completed.has(n)) return;
    completed.add(n);
    const btn = document.querySelector(`#levelNav button[data-n="${n}"]`);
    if (btn) btn.classList.add("done");
    if (badgeName) {
      badges.push({ n, name: badgeName });
      const s = document.createElement("span");
      s.textContent = badgeName;
      $("badgeShelf").appendChild(s);
    }
  }

  // ---- finale summary: lessons paired with their limits, never a victory ----
  const LESSONS = [
    [1, "Time, information, energy appear only across a cut; the whole stays frozen (S_U = 0).", "…computed with an external parameter the framework itself cannot banish."],
    [2, "Each cut splits the world into flowing and persisting piles, exactly and honestly.", "…and the split reshuffles when you recut; the ledger is cut-relative."],
    [3, "Every cut is as valid as any other.", "Turtle 2: no partition selector exists inside the theory — the quest was unwinnable by design."],
    [4, "From an entropy minimum, both directions look like the future.", "Turtle 1: the arrow is imported via a past condition you don't control from inside."],
    [5, "An endogenous observer sees the substrate square-rooted; slow instruments see none of it; its own light-front always leaks it back.", "Naive claim falsified; the IR-only claim survives; the interacting case is open."],
    [6, "The problem of time and the information paradox share one shape: a cut-relative quantity mistaken for an absolute.", "Shape only — nothing was derived here."],
  ];
  function renderFinale() {
    const box = $("finale-list");
    box.innerHTML = LESSONS.map(([n, claim, limit]) =>
      `<div class="card"><p><strong>Level ${n}${completed.has(n) ? " ✓" : " (not finished)"}:</strong> ${claim}<br>
       <span class="small" style="color:var(--gapc)"><strong>Its limit:</strong> ${limit}</span></p></div>`).join("");
  }

  // ---- shared animation loop: only the active level ticks ----
  function loop(t) {
    const dt = Math.min(0.1, (t - lastT) / 1000); lastT = t;
    const def = levels.get(current);
    if (def && def.tick) def.tick(dt);
    requestAnimationFrame(loop);
  }

  function start() {
    const nav = $("levelNav");
    for (let n = 1; n <= 7; n++) {
      const b = document.createElement("button");
      b.dataset.n = n;
      b.textContent = n === 7 ? "End" : "L" + n;
      b.addEventListener("click", () => goto(n));
      nav.appendChild(b);
    }
    $("viewGods").addEventListener("click", () => setView("gods"));
    $("viewCut").addEventListener("click", () => setView("cut"));
    document.querySelectorAll(".nextlv").forEach(b =>
      b.addEventListener("click", () => goto(+b.dataset.next)));
    for (const [n, def] of levels) if (def.init) def.init();
    goto(1);
    requestAnimationFrame(loop);
  }

  return { register, start, setView, goto, complete, css,
           get view() { return view; }, get current() { return current; } };
})();
