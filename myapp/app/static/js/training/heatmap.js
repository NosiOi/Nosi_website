import { TrainingAPI } from "./api.js";

let CALENDAR_DATA = [];
let CURRENT_YEAR = new Date().getFullYear();
let CURRENT_MONTH = new Date().getMonth();

export function initHeatmap() {
    const yearSelect = document.getElementById("tr-heatmap-year");
    const yearSelectCal = document.getElementById("cal-year-select");
    const openCalendar = document.getElementById("tr-open-calendar");
    const closeCalendar = document.querySelectorAll("[data-close-calendar]");
    const closeDayDetails = document.querySelectorAll("[data-close-day-details]");
    const modal = document.getElementById("tr-calendar-modal");

    if (!yearSelect || !yearSelectCal || !openCalendar || !modal) return;

    CURRENT_YEAR = Number(yearSelect.value || new Date().getFullYear());
    yearSelectCal.value = CURRENT_YEAR;

    const load = () => {
        CURRENT_YEAR = Number(yearSelect.value);
        yearSelectCal.value = CURRENT_YEAR;

        TrainingAPI.getHeatmap(CURRENT_YEAR)
            .then(data => {
                CALENDAR_DATA = Array.isArray(data?.days) ? data.days : [];
                renderHeatmap(CALENDAR_DATA);
                renderCalendarMonth();
            })
            .catch(() => {
                CALENDAR_DATA = [];
                renderHeatmap([]);
                renderCalendarMonth();
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
    closeCalendar.forEach(btn =>
        btn.addEventListener("click", () => modal.classList.remove("open"))
    );
    closeDayDetails.forEach(btn =>
        btn.addEventListener("click", () => {
            const m = document.getElementById("tr-day-details-modal");
            if (m) m.classList.remove("open");
        })
    );

    const prevBtn = document.getElementById("cal-prev");
    const nextBtn = document.getElementById("cal-next");

    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
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
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
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
    }
}

function renderHeatmap(days) {
    const grid = document.getElementById("training-heatmap");
    if (!grid) return;
    grid.innerHTML = "";

    days.forEach(d => {
        const cell = document.createElement("div");
        cell.className = "heatmap-cell";
        cell.dataset.level = Number(d.level) || 0;

        if (d.is_today) cell.classList.add("today");

        const tooltip = document.createElement("div");
        tooltip.className = "heatmap-tooltip";
        tooltip.textContent = `${d.percent}% навантаження (${Number(d.load) || 0} од.)`;

        cell.appendChild(tooltip);
        grid.appendChild(cell);

        cell.addEventListener("click", () => openDayDetails(d.date));
    });
}

function renderCalendarMonth() {
    const grid = document.getElementById("tr-calendar-grid");
    const title = document.getElementById("cal-month-title");
    if (!grid || !title) return;

    grid.innerHTML = "";

    const monthNames = [
        "Січень","Лютий","Березень","Квітень","Травень","Червень",
        "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"
    ];

    title.textContent = `${monthNames[CURRENT_MONTH]} ${CURRENT_YEAR}`;

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
        load.textContent = `${d.percent}%`;

        item.appendChild(date);
        item.appendChild(load);

        item.addEventListener("click", () => openDayDetails(d.date));

        grid.appendChild(item);
    });
}

function openDayDetails(date) {
    TrainingAPI.getDayDetails(date)
        .then(data => {
            const modal = document.getElementById("tr-day-details-modal");
            const title = document.getElementById("tr-day-details-title");
            const body = document.getElementById("tr-day-details-body");
            if (!modal || !title || !body) return;

            const dt = new Date(date).toLocaleDateString("uk-UA", {
                day: "numeric",
                month: "long",
                year: "numeric"
            });

            title.textContent = dt;

            const sessions = Array.isArray(data?.sessions) ? data.sessions : [];

            if (!sessions.length) {
                body.innerHTML = "<p>Немає тренувань у цей день</p>";
            } else {
                body.innerHTML = sessions
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
        })
        .catch(() => {
            const body = document.getElementById("tr-day-details-body");
            const modal = document.getElementById("tr-day-details-modal");
            const title = document.getElementById("tr-day-details-title");

            if (title) title.textContent = "Помилка";
            if (body) body.innerHTML = "<p>Не вдалося завантажити дані.</p>";
            if (modal) modal.classList.add("open");
        });
}
