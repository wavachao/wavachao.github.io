(function () {
    "use strict";

    var root = document.documentElement;
    var body = document.body;
    var header = document.querySelector("[data-header]");
    var themeToggle = document.querySelector("[data-theme-toggle]");
    var menuToggle = document.querySelector("[data-menu-toggle]");
    var nav = document.querySelector("[data-nav]");
    var year = document.querySelector("[data-current-year]");

    function setTheme(theme) {
        root.dataset.theme = theme;
        try { localStorage.setItem("portfolio-theme", theme); } catch (error) {}
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            setTheme(root.dataset.theme === "light" ? "dark" : "light");
        });
    }

    function setMenu(open) {
        if (!menuToggle || !nav) return;
        menuToggle.setAttribute("aria-expanded", String(open));
        menuToggle.setAttribute("aria-label", open ? "关闭导航" : "打开导航");
        nav.classList.toggle("is-open", open);
        body.classList.toggle("nav-open", open);
    }

    if (menuToggle && nav) {
        menuToggle.addEventListener("click", function () {
            setMenu(menuToggle.getAttribute("aria-expanded") !== "true");
        });
        nav.addEventListener("click", function (event) {
            if (event.target.closest("a")) setMenu(false);
        });
        addEventListener("resize", function () {
            if (innerWidth > 840) setMenu(false);
        });
        addEventListener("keydown", function (event) {
            if (event.key === "Escape") setMenu(false);
        });
    }

    function updateHeader() {
        if (header) header.classList.toggle("is-scrolled", scrollY > 12);
    }
    updateHeader();
    addEventListener("scroll", updateHeader, { passive: true });

    var revealItems = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
    revealItems.forEach(function (item) {
        var delay = item.getAttribute("data-delay");
        if (delay) item.style.setProperty("--reveal-delay", delay + "ms");
    });

    if ("IntersectionObserver" in window) {
        var revealObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: .12, rootMargin: "0px 0px -36px" });
        revealItems.forEach(function (item) { revealObserver.observe(item); });
    } else {
        revealItems.forEach(function (item) { item.classList.add("is-visible"); });
    }

    var links = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
    var sections = links.map(function (link) {
        return document.querySelector(link.getAttribute("href"));
    }).filter(Boolean);

    if ("IntersectionObserver" in window) {
        var sectionObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                links.forEach(function (link) {
                    var active = link.getAttribute("href") === "#" + entry.target.id;
                    if (active) link.setAttribute("aria-current", "true");
                    else link.removeAttribute("aria-current");
                });
            });
        }, { rootMargin: "-30% 0px -60%", threshold: 0 });
        sections.forEach(function (section) { sectionObserver.observe(section); });
    }

    if (year) year.textContent = String(new Date().getFullYear());
}());
