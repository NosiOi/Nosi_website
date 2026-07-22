import { RecoveryAPI } from "./api.js";

let HEATMAP_DATA = [];
let CURRENT_YEAR = new Date().getFullYear();

export function initRecoveryHeatmap() {
    const yearSelect = document.getElementById("rc-heatmap-year");
    const openCalendar = document.getElementById("rc-open-calendar");
    const modal = document.getElementById("rc-calendar-modal");
    const grid = document.getElementById("recovery-heatmap");
    const tooltip = document.getElementById("rc-heatmap-tooltip");

    if (!yearSelect || !openCalendar || !grid || !tooltip) return;

    const nowYear = new Date().getFullYear();
    yearSelect.innerHTML = "";
    for (let y = nowYear; y >= 2020; y--) {
        const opt = document.createElement("option");
        opt.value = String(y);
        opt.textContent = String(y);
        yearSelect.appendChild(opt);
    }

    CURRENT_YEAR = Number(yearSelect.value || nowYear);

    const load = () => {
        CURRENT_YEAR = Number(yearSelect.value);

        RecoveryAPI.getHeatmap(window.USER_ID, 365)
            .then(data => {
                HEATMAP_DATA = Array.isArray(data) ? data : [];
                renderRecoveryHeatmap(HEATMAP_DATA, grid, tooltip);
            })
            .catch(() => {
                HEATMAP_DATA = [];
                renderRecoveryHeatmap([], grid, tooltip);
            });
    };

    load();

    yearSelect.addEventListener("change", load);

    openCalendar.addEventListener("click", () => {
        if (modal) modal.classList.add("open");
    });

    const closeCalendar = document.querySelectorAll("[data-close-calendar]");
    closeCalendar.forEach(btn =>
        btn.addEventListener("click", () => {
            if (modal) modal.classList.remove("open");
        })
    );
}

export function renderRecoveryHeatmap(days, grid, tooltip) {
    if (!grid || !tooltip) return;

    grid.innerHTML = "";

    const weeks = [];
    for (let i = 0; i < 53; i++) {
        weeks.push(new Array(7).fill(null));
    }

    days.forEach(d => {
        const date = new Date(d.date);
        const dayOfWeek = date.getDay();
        const weekOfYear = getWeekIndex(date);
        const level = Number(d.recovery_score) || 0;

        if (weekOfYear >= 0 && weekOfYear < weeks.length) {
            weeks[weekOfYear][dayOfWeek] = {
                level,
                date: d.date,
                score: d.recovery_score
            };
        }
    });

    weeks.forEach(week => {
        week.forEach(cellData => {
            const cell = document.createElement("div");
            cell.className = "rc-heatmap-cell";

            if (cellData) {
                cell.dataset.level = cellData.level;

                cell.addEventListener("mouseenter", e => {
                    tooltip.textContent = `${cellData.score || 0} балів`;
                    tooltip.classList.add("visible");
                    positionTooltip(e, tooltip);
                });

                cell.addEventListener("mousemove", e => {
                    positionTooltip(e, tooltip);
                });

                cell.addEventListener("mouseleave", () => {
                    tooltip.classList.remove("visible");
                });

                cell.addEventListener("click", () => openRecoveryDay(cellData.date));
            }

            grid.appendChild(cell);
        });
    });
}

function positionTooltip(event, tooltip) {
    const x = event.clientX + 12;
    const y = event.clientY - 12;
    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
}

function getWeekIndex(date) {
    const start = new Date(date.getFullYear(), 0, 1);
    const dayOfYear =
        Math.floor((date - start) / (1000 * 60 * 60 * 24)) + 1;
    const startDay = start.getDay();
    return Math.floor((dayOfYear + startDay) / 7);
}

function openRecoveryDay(date) {
    RecoveryAPI.getSnapshot(window.USER_ID, date)
        .then(snapshot => {
            const modal = document.getElementById("rc-day-details-modal");
            const title = document.getElementById("rc-day-details-title");
            const body = document.getElementById("rc-day-details-body");

            if (!modal || !title || !body) return;

            const dt = new Date(date).toLocaleDateString("uk-UA", {
                day: "numeric",
                month: "long",
                year: "numeric"
            });

            title.textContent = dt;

            if (!snapshot) {
                body.innerHTML = "<p>Немає даних за цей день</p>";
            } else {
                body.innerHTML = `
                    <div class="rc-day-info">
                        <div class="rc-day-score">Відновлення: ${snapshot.recovery_score}</div>
                        <div class="rc-day-sleep">Сон: ${snapshot.sleep_score}</div>
                        <div class="rc-day-habits">Звички: ${snapshot.habit_score}</div>
                        <div class="rc-day-energy">Енергія: ${snapshot.energy_score}</div>
                    </div>
                `;
            }

            modal.classList.add("open");
        })
        .catch(() => {
            const modal = document.getElementById("rc-day-details-modal");
            const title = document.getElementById("rc-day-details-title");
            const body = document.getElementById("rc-day-details-body");

            if (title) title.textContent = "Помилка";
            if (body) body.innerHTML = "<p>Не вдалося завантажити дані.</p>";
            if (modal) modal.classList.add("open");
        });
}
