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

  // Default is dark (see static/css/main.css) regardless of OS preference,
  // so anything other than an explicit "light" counts as dark.
  function currentTheme() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
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
