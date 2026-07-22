import { RecoveryAPI } from "./api.js";

let HEATMAP_DATA = [];
let CURRENT_YEAR = new Date().getFullYear();

export function initRecoveryHeatmap() {
    const yearSelect = document.getElementById("rc-heatmap-year");
    const openCalendar = document.getElementById("rc-open-calendar");
    const modal = document.getElementById("rc-calendar-modal");

    if (!yearSelect || !openCalendar) return;

    CURRENT_YEAR = Number(yearSelect.value || new Date().getFullYear());

    const load = () => {
        CURRENT_YEAR = Number(yearSelect.value);

        RecoveryAPI.getHeatmap(window.USER_ID, 365)
            .then(data => {
                HEATMAP_DATA = Array.isArray(data) ? data : [];
                renderRecoveryHeatmap(HEATMAP_DATA);
            })
            .catch(() => {
                HEATMAP_DATA = [];
                renderRecoveryHeatmap([]);
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

export function renderRecoveryHeatmap(days) {
    const grid = document.getElementById("recovery-heatmap");
    if (!grid) return;

    grid.innerHTML = "";

    const weeks = [];
    for (let i = 0; i < 53; i++) {
        weeks.push([]);
    }

    days.forEach(d => {
        const date = new Date(d.date);
        const dayOfWeek = date.getDay();
        const weekOfYear = getWeekOfYear(date);
        const level = Number(d.recovery_score) || 0;

        if (!weeks[weekOfYear]) weeks[weekOfYear] = [];
        weeks[weekOfYear][dayOfWeek] = {
            level,
            date: d.date,
            score: d.recovery_score
        };
    });

    weeks.forEach(week => {
        for (let i = 0; i < 7; i++) {
            const cellData = week[i];
            const cell = document.createElement("div");
            cell.className = "rc-heatmap-cell";

            if (cellData) {
                cell.dataset.level = cellData.level;

                const tooltip = document.createElement("div");
                tooltip.className = "rc-heatmap-tooltip";
                tooltip.textContent = `${cellData.score || 0} балів`;

                cell.appendChild(tooltip);

                cell.addEventListener("click", () => openRecoveryDay(cellData.date));
            }

            grid.appendChild(cell);
        }
    });
}

function getWeekOfYear(date) {
    const start = new Date(date.getFullYear(), 0, 1);
    const diff = date - start;
    return Math.floor(diff / (1000 * 60 * 60 * 24 * 7));
}

function openRecoveryDay(date) {
    RecoveryAPI.getSnapshot(window.USER_ID)
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
