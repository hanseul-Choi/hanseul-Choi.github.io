// Manual light/dark theme toggle. The only JS on this site — everything
// else (nav active state, collapsible sections, lightbox, project modals)
// is plain HTML/CSS. See templates/base.html for the early-init inline
// script that applies a saved choice before first paint.
(function () {
  "use strict";

  var STORAGE_KEY = "theme";
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");
  if (!toggle) {
    return;
  }

  function systemPrefersDark() {
    return (
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  }

  function currentTheme() {
    var explicit = root.getAttribute("data-theme");
    if (explicit === "dark" || explicit === "light") {
      return explicit;
    }
    return systemPrefersDark() ? "dark" : "light";
  }

  toggle.addEventListener("click", function () {
    var next = currentTheme() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (e) {
      // localStorage unavailable (private mode, disabled) — the toggle
      // still works for this page view, it just won't persist.
    }
  });
})();
