// Injects the shared nav bar. Usage: <script src="assets/site-nav.js" data-page="index"></script>
(function () {
  const page = document.currentScript.dataset.page;
  const links = [
    ["index", "index.html", "Overview"],
    ["operational", "operational-core.html", "Operational Core"],
    ["game", "the-cut-game.html", "Interactive Guide"],
    ["framework", "framework-explorer.html", "Framework Explorer"],
    ["time", "time-as-forgetting-lab.html", "Entropy Lab"],
    ["cone", "lieb-robinson-cone-lab.html", "Cone Lab"],
    ["verdict", "ruler-cancellation-verdict-lab.html", "Verdict Lab"],
    ["orientation", "orientation-gauge-lab.html", "Orientation Lab"],
    ["followup", "followup-study.html", "Follow-up Results"],
  ];
  const nav = document.createElement("nav");
  nav.className = "cutnav";
  nav.setAttribute("aria-label", "Primary");
  nav.innerHTML = '<span class="brand">THE CUT</span>' + links.map(([id, href, label]) =>
    `<a href="${href}"${id === page ? ' class="active" aria-current="page"' : ""}>${label}</a>`).join("");
  document.body.prepend(nav);
  // Wrapped navigation changes height on narrow screens. Keep sticky controls and anchors clear.
  const updateNavHeight = () => document.documentElement.style.setProperty(
    "--cutnav-height", `${Math.ceil(nav.getBoundingClientRect().height)}px`);
  updateNavHeight();
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(updateNavHeight).observe(nav);
  else window.addEventListener("resize", updateNavHeight);
})();
