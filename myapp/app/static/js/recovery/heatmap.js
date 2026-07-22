import { RecoveryAPI } from "./api.js";

let HEATMAP_DATA = [];
let CURRENT_YEAR = new Date().getFullYear();

export function initRecoveryHeatmap() {
    const root = document.getElementById("recovery-app");
    const yearSelect = document.getElementById("rc-heatmap-year");
    const openCalendar = document.getElementById("rc-open-calendar");
    const modal = document.getElementById("rc-calendar-modal");
    const grid = document.getElementById("recovery-heatmap");
    const tooltip = document.getElementById("rc-heatmap-tooltip");

    if (!root || !yearSelect || !openCalendar || !grid || !tooltip) return;

    const userId = Number(root.dataset.userId || 0);
    if (!userId) return;

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

        RecoveryAPI.getHeatmap(userId, CURRENT_YEAR)
            .then(data => {
                HEATMAP_DATA = Array.isArray(data?.days) ? data.days : [];
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
        const weekIndex = getWeekIndex(date);
        const level = Number(d.level) || 0;

        if (weekIndex >= 0 && weekIndex < weeks.length) {
            weeks[weekIndex][dayOfWeek] = {
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

                cell.addEventListener("click", () => openRecoveryDay(cellData.date, tooltip));
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
    const yearStart = new Date(date.getFullYear(), 0, 1);
    const dayOffset = (yearStart.getDay() + 6) % 7;
    const firstWeekStart = new Date(yearStart);
    firstWeekStart.setDate(yearStart.getDate() - dayOffset);

    const diffDays = Math.floor((date - firstWeekStart) / (1000 * 60 * 60 * 24));
    return Math.floor(diffDays / 7);
}

function openRecoveryDay(date) {
    const root = document.getElementById("recovery-app");
    if (!root) return;
    const userId = Number(root.dataset.userId || 0);
    if (!userId) return;

    RecoveryAPI.getSnapshot(userId, date)
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
