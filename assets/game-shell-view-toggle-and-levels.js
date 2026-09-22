// Core of the interactive guide: level registry, model/observer view toggle,
// level navigation, result shelf, and the shared
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

  // ---- view toggle ----
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
    iris.classList.add("in");
    setTimeout(() => { apply(); iris.classList.remove("in"); }, 190);
    setTimeout(() => { switching = false; }, 400);
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

  // ---- final summary: claims paired with their limits ----
  const LESSONS = [
    [1, "A chosen cut defines reduced entropy, boundary current, and accessible-record questions in this realization.", "S_U = 0 follows from purity; it neither makes the state stationary nor supplies a physical clock."],
    [2, "A model cut makes boundary currents, reduced entropy, and conserved quantities computable.", "The flow/persistence classification is interpretive and changes when the cut changes."],
    [3, "None of four candidate rules selected a stable unique cut from the supplied inputs.", "A richer physical selection principle was not tested; the universal no-selection claim does not follow."],
    [4, "For this symmetric preparation, S_A rises away from the minimum in both parameter directions.", "This entropy transcript does not derive a macroscopic arrow or cover every procedure."],
    [5, "The front ratio follows square-root scaling while the tested long-wavelength wavepacket approaches isotropy.", "The general null claim is falsified; support is limited to the tested infrared observable, and the interacting case is open."],
    [6, "Relational-time and island constructions both demand explicit observables, subsystems, and scope.", "Analogy only: their distinct clock and gravitational assumptions do the physical work."],
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
