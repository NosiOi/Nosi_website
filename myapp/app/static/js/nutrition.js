document.addEventListener("DOMContentLoaded", () => {
  const tipsBtn = document.querySelector("[data-open-tips]");
  const tipsPopover = document.querySelector("[data-tips-popover]");
  const mealsOverlay = document.querySelector("[data-meals-overlay]");
  const mealsPanel = document.querySelector("[data-meals-panel]");
  const openMealsBtn = document.querySelector("[data-open-meals-panel]");
  const closeMealsBtn = document.querySelector("[data-meals-close]");
  const tabs = document.querySelectorAll("[data-meals-tab]");
  const sections = document.querySelectorAll("[data-meals-section]");
  const tooltip = document.getElementById("nutr-tooltip");

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
      mealsPanel.classList.add("nutr-animate-modal");
    });
  }

  if (closeMealsBtn) {
    closeMealsBtn.addEventListener("click", () => {
      mealsOverlay.classList.remove("open");
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.mealsTab;

      tabs.forEach((t) => t.classList.remove("nutr-meals-tab-active"));
      tab.classList.add("nutr-meals-tab-active");

      sections.forEach((sec) => {
        sec.classList.remove("nutr-meals-section-active");
        if (sec.dataset.mealsSection === target) {
          sec.classList.add("nutr-meals-section-active");
        }
      });
    });
  });

  const helpButtons = document.querySelectorAll(".nutr-help");
  const helpTexts = {
    kcal: "Калорії — основний показник енергетичного балансу.",
    protein: "Білки — ключові для відновлення та росту м’язів.",
    fat: "Жири — важливі для гормонів та енергії.",
    carb: "Вуглеводи — головне джерело енергії.",
    balance: "Баланс дня показує співвідношення спожитих макросів.",
    compare: "Порівняння з вчора допомагає відстежувати динаміку.",
    water: "Водний баланс впливає на продуктивність та самопочуття.",
    day_chart: "Графік показує розподіл КБЖВ протягом дня.",
    week_chart: "Тижневий графік показує тренди за 7 днів.",
    month: "Місячна статистика показує стабільність харчування.",
    quality: "Якість раціону оцінюється за цільністю продуктів."
  };

  helpButtons.forEach((btn) => {
    btn.addEventListener("mouseenter", (e) => {
      const key = btn.dataset.helpKey;
      const text = helpTexts[key] || "Немає опису.";
      tooltip.textContent = text;
      tooltip.classList.add("visible");
      const rect = btn.getBoundingClientRect();
      tooltip.style.left = rect.left + rect.width / 2 + "px";
      tooltip.style.top = rect.top - 40 + "px";
    });

    btn.addEventListener("mouseleave", () => {
      tooltip.classList.remove("visible");
    });
  });

  const waterButtons = document.querySelectorAll("[data-water-add]");
  const waterReset = document.querySelector("[data-water-reset]");
  const waterValue = document.querySelector(".nutr-water-value");
  const waterFill = document.querySelector(".nutr-water-progress-fill");

  let currentWater = parseFloat(waterValue?.textContent || 0);
  const waterGoal = parseFloat(waterFill?.dataset?.goal || 0);

  function updateWaterUI() {
    waterValue.textContent = currentWater.toFixed(2);
    const percent = Math.min(100, (currentWater / waterGoal) * 100);
    waterFill.style.width = percent + "%";
  }

  waterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const add = parseFloat(btn.dataset.waterAdd);
      currentWater += add;
      updateWaterUI();
    });
  });

  if (waterReset) {
    waterReset.addEventListener("click", () => {
      currentWater = 0;
      updateWaterUI();
    });
  }

  const dayCtx = document.getElementById("nutr-day-chart");
  const weekCtx = document.getElementById("nutr-week-chart");

  if (dayCtx) {
    new Chart(dayCtx, {
      type: "line",
      data: {
        labels: dayChartData.labels,
        datasets: [
          {
            label: "Ккал",
            data: dayChartData.kcal,
            borderColor: "#ffd646",
            backgroundColor: "rgba(255,214,70,0.1)",
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: "#ffd646"
          },
          {
            label: "Білки",
            data: dayChartData.protein,
            borderColor: "#00e0c6",
            backgroundColor: "rgba(0,224,198,0.1)",
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: "#00e0c6"
          },
          {
            label: "Жири",
            data: dayChartData.fat,
            borderColor: "#b89bff",
            backgroundColor: "rgba(184,155,255,0.1)",
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: "#b89bff"
          },
          {
            label: "Вуглеводи",
            data: dayChartData.carb,
            borderColor: "#00e0c6",
            backgroundColor: "rgba(0,224,198,0.1)",
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: "#00e0c6"
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#020308",
            titleColor: "#f3f4fb",
            bodyColor: "#00e0c6",
            borderColor: "rgba(255,255,255,0.12)",
            borderWidth: 1,
            padding: 10
          }
        },
        scales: {
          x: {
            ticks: { color: "#7b8091" },
            grid: { color: "rgba(255,255,255,0.06)" }
          },
          y: {
            ticks: { color: "#7b8091" },
            grid: { color: "rgba(255,255,255,0.06)" }
          }
        }
      }
    });
  }

  if (weekCtx) {
    new Chart(weekCtx, {
      type: "bar",
      data: {
        labels: weekChartData.labels,
        datasets: [
          {
            label: "Ккал",
            data: weekChartData.kcal,
            backgroundColor: "#00e0c6",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#020308",
            titleColor: "#f3f4fb",
            bodyColor: "#00e0c6",
            borderColor: "rgba(255,255,255,0.12)",
            borderWidth: 1,
            padding: 10
          }
        },
        scales: {
          x: {
            ticks: { color: "#7b8091" },
            grid: { display: false }
          },
          y: {
            ticks: { color: "#7b8091" },
            grid: { color: "rgba(255,255,255,0.06)" }
          }
        }
      }
    });
  }
});
