(function () {
    var root = document.documentElement;
    var button = document.querySelector("[data-theme-toggle]");
    var themeColor = document.querySelector("[data-theme-color]");

    function applyTheme(theme, persist) {
        root.dataset.theme = theme;

        if (button) {
            button.setAttribute("aria-pressed", String(theme === "dark"));
            button.setAttribute("aria-label", theme === "dark" ? "切换到浅色模式" : "切换到深色模式");
        }

        if (themeColor) {
            themeColor.content = theme === "dark" ? "#181815" : "#f3efe5";
        }

        if (persist) {
            localStorage.setItem("homepage-theme", theme);
        }
    }

    applyTheme(root.dataset.theme || "light", false);

    if (button) {
        button.addEventListener("click", function () {
            applyTheme(root.dataset.theme === "dark" ? "light" : "dark", true);
        });
    }

    var systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
    if (systemTheme.addEventListener) {
        systemTheme.addEventListener("change", function (event) {
            if (!localStorage.getItem("homepage-theme")) {
                applyTheme(event.matches ? "dark" : "light", false);
            }
        });
    }
}());
