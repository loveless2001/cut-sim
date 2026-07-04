// Injects the shared nav bar. Usage: <script src="assets/site-nav.js" data-page="index"></script>
(function () {
  const page = document.currentScript.dataset.page;
  const links = [
    ["index", "index.html", "Overview"],
    ["game", "the-cut-game.html", "The Game"],
    ["framework", "framework-explorer.html", "Framework Explorer"],
    ["time", "time-as-forgetting-lab.html", "Time Lab"],
    ["cone", "lieb-robinson-cone-lab.html", "Cone Lab"],
    ["verdict", "ruler-cancellation-verdict-lab.html", "Verdict Lab"],
  ];
  const nav = document.createElement("nav");
  nav.className = "cutnav";
  nav.innerHTML = '<span class="brand">THE CUT</span>' + links.map(([id, href, label]) =>
    `<a href="${href}"${id === page ? ' class="active"' : ""}>${label}</a>`).join("");
  document.body.prepend(nav);
})();
