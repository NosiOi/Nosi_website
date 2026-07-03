const HeatmapAPI = {
  getYear: year => fetch(`/api/training/heatmap?year=${year}`).then(r => r.json()),
  getDay: date => fetch(`/api/training/day/${date}`).then(r => r.json())
};

let CALENDAR_DATA = [];
let CURRENT_YEAR = 2026;
let CURRENT_MONTH = new Date().getMonth();


function renderHeatmap(days) {
  const grid = document.getElementById("training-heatmap");
  grid.innerHTML = "";

  days.forEach(d => {
    const cell = document.createElement("div");
    cell.className = "heatmap-cell";
    cell.dataset.level = d.level;

    if (d.is_today) cell.classList.add("today");

    const tooltip = document.createElement("div");
    tooltip.className = "heatmap-tooltip";
    tooltip.textContent = `${d.load} навантаження`;

    cell.appendChild(tooltip);
    grid.appendChild(cell);

    cell.addEventListener("click", () => openDayDetails(d.date));
  });
}


function renderCalendarMonth() {
  if (!CALENDAR_DATA.length) return;

  const grid = document.getElementById("tr-calendar-grid");
  const title = document.getElementById("cal-month-title");
  grid.innerHTML = "";

  const monthNames = [
    "Січень","Лютий","Березень","Квітень","Травень","Червень",
    "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"
  ];

  title.textContent = `${monthNames[CURRENT_MONTH]}`;

  const days = CALENDAR_DATA.filter(d => {
    const dt = new Date(d.date);
    return dt.getFullYear() === CURRENT_YEAR && dt.getMonth() === CURRENT_MONTH;
  });

  days.forEach(d => {
    const item = document.createElement("div");
    item.className = "tr-calendar-item tr-level-" + d.level;

    const date = document.createElement("div");
    date.className = "tr-calendar-date";
    date.textContent = new Date(d.date).getDate();

    const load = document.createElement("div");
    load.className = "tr-calendar-load";
    load.textContent = d.load;

    item.appendChild(date);
    item.appendChild(load);

    item.addEventListener("click", () => openDayDetails(d.date));

    grid.appendChild(item);
  });
}


function openDayDetails(date) {
  HeatmapAPI.getDay(date).then(data => {
    const modal = document.getElementById("tr-day-details-modal");
    const title = document.getElementById("tr-day-details-title");
    const body = document.getElementById("tr-day-details-body");

    const dt = new Date(date).toLocaleDateString("uk-UA", {
      day: "numeric",
      month: "long",
      year: "numeric"
    });

    title.textContent = dt;

    if (!data.sessions.length) {
      body.innerHTML = "<p>Немає тренувань у цей день</p>";
    } else {
      body.innerHTML = data.sessions
        .map(s => `
          <div class="tr-day-session">
            <div class="tr-day-session-title">Сесія</div>
            ${s.exercises
              .map(ex => `
                <div class="tr-day-exercise">
                  <div class="tr-ex-name">${ex.name}</div>
                  <div class="tr-ex-meta">${ex.sets}×${ex.reps}, ${ex.load} кг</div>
                </div>
              `)
              .join("")}
          </div>
        `)
        .join("");
    }

    modal.classList.add("open");
  });
}


document.addEventListener("DOMContentLoaded", () => {
  const yearSelect = document.getElementById("tr-heatmap-year");
  const yearSelectCal = document.getElementById("cal-year-select");
  const openCalendar = document.getElementById("tr-open-calendar");
  const closeCalendar = document.querySelectorAll("[data-close-calendar]");
  const closeDayDetails = document.querySelectorAll("[data-close-day-details]");
  const modal = document.getElementById("tr-calendar-modal");

  const load = () => {
    CURRENT_YEAR = Number(yearSelect.value);

    HeatmapAPI.getYear(CURRENT_YEAR).then(data => {
      CALENDAR_DATA = data.days;

      renderHeatmap(data.days);
      renderCalendarMonth(); // тепер працює
    });
  };

  load();

  yearSelect.addEventListener("change", load);
  yearSelectCal.addEventListener("change", () => {
    CURRENT_YEAR = Number(yearSelectCal.value);
    yearSelect.value = CURRENT_YEAR;
    load();
  });

  openCalendar.addEventListener("click", () => modal.classList.add("open"));
  closeCalendar.forEach(btn => btn.addEventListener("click", () => modal.classList.remove("open")));
  closeDayDetails.forEach(btn => btn.addEventListener("click", () => {
    document.getElementById("tr-day-details-modal").classList.remove("open");
  }));

  document.getElementById("cal-prev").addEventListener("click", () => {
    CURRENT_MONTH--;
    if (CURRENT_MONTH < 0) {
      CURRENT_MONTH = 11;
      CURRENT_YEAR--;
      yearSelect.value = CURRENT_YEAR;
      yearSelectCal.value = CURRENT_YEAR;
      load();
    } else {
      renderCalendarMonth();
    }
  });

  document.getElementById("cal-next").addEventListener("click", () => {
    CURRENT_MONTH++;
    if (CURRENT_MONTH > 11) {
      CURRENT_MONTH = 0;
      CURRENT_YEAR++;
      yearSelect.value = CURRENT_YEAR;
      yearSelectCal.value = CURRENT_YEAR;
      load();
    } else {
      renderCalendarMonth();
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        if (typeof syncRightBlockHeight === "function") {
            syncRightBlockHeight();
        }
    }, 150);
});
