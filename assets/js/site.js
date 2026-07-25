(function () {
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");
  var themeColor = document.querySelector("[data-theme-color]");

  function applyTheme(theme, persist) {
    root.dataset.theme = theme;

    if (toggle) {
      toggle.setAttribute("aria-pressed", String(theme === "dark"));
      toggle.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
      );
    }

    if (themeColor) {
      themeColor.content = theme === "dark" ? "#151614" : "#f1eee6";
    }

    if (persist) {
      localStorage.setItem("site-theme", theme);
    }
  }

  applyTheme(root.dataset.theme || "light", false);

  if (toggle) {
    toggle.addEventListener("click", function () {
      applyTheme(root.dataset.theme === "dark" ? "light" : "dark", true);
    });
  }

  var systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  if (systemTheme.addEventListener) {
    systemTheme.addEventListener("change", function (event) {
      if (!localStorage.getItem("site-theme")) {
        applyTheme(event.matches ? "dark" : "light", false);
      }
    });
  }

  var search = document.querySelector("[data-archive-search]");
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-archive-item]"));
  var count = document.querySelector("[data-archive-count]");
  var empty = document.querySelector("[data-archive-empty]");

  function filterArchive() {
    var query = search.value.trim().toLocaleLowerCase();
    var visible = 0;

    items.forEach(function (item) {
      var matches = !query || item.dataset.search.toLocaleLowerCase().includes(query);
      item.hidden = !matches;
      if (matches) visible += 1;
    });

    if (count) count.textContent = String(visible);
    if (empty) empty.hidden = visible !== 0;
  }

  if (search) {
    var query = new URLSearchParams(window.location.search).get("q");
    if (query) search.value = query;
    search.addEventListener("input", filterArchive);
    filterArchive();
  }

  function replaceBrokenImage(image) {
    if (image.dataset.fallbackApplied === "true") return;
    image.dataset.fallbackApplied = "true";

    var fallback = document.createElement("span");
    fallback.className = "missing-media";
    fallback.setAttribute("role", "img");
    fallback.setAttribute("aria-label", "The original article image is no longer available");
    fallback.innerHTML = "<strong>Image unavailable</strong><small>The original external image is no longer online.</small>";
    image.replaceWith(fallback);
  }

  document.querySelectorAll(".legacy-article-content img").forEach(function (image) {
    image.addEventListener("error", function () {
      replaceBrokenImage(image);
    });
    if (image.complete && image.naturalWidth === 0) {
      replaceBrokenImage(image);
    }
  });
}());
