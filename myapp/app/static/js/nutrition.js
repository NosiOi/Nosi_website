document.addEventListener("DOMContentLoaded", () => {
    const mealsOverlay = document.querySelector("[data-meals-overlay]");
    const mealsPanel = document.querySelector("[data-meals-panel]");
    const openMealsBtn = document.querySelector("[data-open-meals-panel]");
    const closeMealsBtn = document.querySelector("[data-meals-close]");

    const tipsBtn = document.querySelector("[data-open-tips]");
    const tipsPopover = document.querySelector("[data-tips-popover]");

    if (tipsBtn && tipsPopover) {
        tipsBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            tipsPopover.classList.toggle("open");
        });

        document.addEventListener("click", (e) => {
            if (!tipsPopover.contains(e.target) && !tipsBtn.contains(e.target)) {
                tipsPopover.classList.remove("open");
            }
        });
    }

    if (openMealsBtn) {
        openMealsBtn.addEventListener("click", () => {
            mealsOverlay.classList.add("open");
        });
    }

    if (closeMealsBtn) {
        closeMealsBtn.addEventListener("click", () => {
            mealsOverlay.classList.remove("open");
        });
    }

    const tabs = document.querySelectorAll("[data-meals-tab]");
    const sections = document.querySelectorAll("[data-meals-section]");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.mealsTab;

            tabs.forEach(t => t.classList.remove("nutr-meals-tab-active"));
            tab.classList.add("nutr-meals-tab-active");

            sections.forEach(sec => {
                sec.classList.remove("nutr-meals-section-active");
                if (sec.dataset.mealsSection === target) {
                    sec.classList.add("nutr-meals-section-active");
                }
            });
        });
    });
});
