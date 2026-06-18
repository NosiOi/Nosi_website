function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add("open");
}

function closeModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove("open");
}

function setTodayDate() {
    const el = document.getElementById("current-date");
    const d = new Date();
    const opts = { day: "2-digit", month: "2-digit", year: "numeric" };
    el.textContent = d.toLocaleDateString("uk-UA", opts);
}

function fillBalance(data) {
    document.getElementById("kcal-main-value").textContent = data.kcal;
    document.getElementById("kcal-main-goal").textContent = `з ${data.kcal_goal} ккал`;

    document.getElementById("macro-protein-value").textContent = `${data.protein} / ${data.protein_goal} г`;
    document.getElementById("macro-protein-percent").textContent = `${data.protein_percent}%`;

    document.getElementById("macro-fat-value").textContent = `${data.fat} / ${data.fat_goal} г`;
    document.getElementById("macro-fat-percent").textContent = `${data.fat_percent}%`;

    document.getElementById("macro-carb-value").textContent = `${data.carb} / ${data.carb_goal} г`;
    document.getElementById("macro-carb-percent").textContent = `${data.carb_percent}%`;

    document.getElementById("kcal-balance-label").textContent = `${data.kcal_balance} ккал`;
    document.getElementById("kcal-balance-status").textContent = data.balance_status;

    document.getElementById("kcal-diff").textContent = `${data.kcal_diff_label} ккал`;
    document.getElementById("protein-diff").textContent = `${data.protein_diff_label} Б`;
    document.getElementById("fat-diff").textContent = `${data.fat_diff_label} Ж`;
    document.getElementById("carb-diff").textContent = `${data.carb_diff_label} В`;

    if (data.water !== undefined)
        document.getElementById("water-today").textContent = `${data.water} л`;

    if (data.water_goal !== undefined)
        document.getElementById("water-goal").textContent = `${data.water_goal} л`;

    if (data.current_weight !== undefined && data.current_weight !== null)
        document.getElementById("weight-current").textContent = `${data.current_weight} кг`;
}

function loadDay() {
    fetch("/api/nutrition/day")
        .then(r => r.json())
        .then(data => {
            fillBalance(data);
            renderMeals(data.meals || []);
        });
}

function setupModals() {

    // ДОДАТИ ПРИЙОМ
    document.getElementById("open-add-meal").addEventListener("click", () => {
        document.getElementById("add-meal-name").value = "";
        document.getElementById("add-meal-category").value = "Сніданок";
        document.getElementById("add-meal-time").value = "";
        openModal("modal-add-meal");
    });

    document.getElementById("close-add-meal").addEventListener("click", () => {
        closeModal("modal-add-meal");
    });

    document.getElementById("save-add-meal").addEventListener("click", () => {
        const body = {
            name: document.getElementById("add-meal-name").value,
            category: document.getElementById("add-meal-category").value,
            time: document.getElementById("add-meal-time").value || null
        };

        fetch("/api/nutrition/meals", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        }).then(() => {
            closeModal("modal-add-meal");
            loadDay();
        });
    });

    // РЕДАГУВАТИ ПРИЙОМ
    document.getElementById("close-edit-meal").addEventListener("click", () => {
        closeModal("modal-edit-meal");
    });

    document.getElementById("save-edit-meal").addEventListener("click", () => {
        const id = document.getElementById("edit-meal-id").value;
        const body = {
            name: document.getElementById("edit-meal-name").value,
            category: document.getElementById("edit-meal-category").value,
            time: document.getElementById("edit-meal-time").value || null
        };

        fetch(`/api/nutrition/meals/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        }).then(() => {
            closeModal("modal-edit-meal");
            loadDay();
        });
    });

    // ДОДАТИ ПРОДУКТ
    document.getElementById("close-add-item").addEventListener("click", () => {
        closeModal("modal-add-item");
    });

    document.getElementById("save-add-item").addEventListener("click", () => {
        const body = {
            meal_id: Number(document.getElementById("add-item-meal-id").value),
            name: document.getElementById("add-item-name").value,
            calories: Number(document.getElementById("add-item-kcal").value || 0),
            protein: Number(document.getElementById("add-item-protein").value || 0),
            fat: Number(document.getElementById("add-item-fat").value || 0),
            carbs: Number(document.getElementById("add-item-carb").value || 0)
        };

        fetch("/api/nutrition/items", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        }).then(() => {
            closeModal("modal-add-item");
            loadDay();
        });
    });

    // РЕДАГУВАТИ ПРОДУКТ
    document.getElementById("close-edit-item").addEventListener("click", () => {
        closeModal("modal-edit-item");
    });

    document.getElementById("save-edit-item").addEventListener("click", () => {
        const id = document.getElementById("edit-item-id").value;
        const body = {
            name: document.getElementById("edit-item-name").value,
            calories: Number(document.getElementById("edit-item-kcal").value || 0),
            protein: Number(document.getElementById("edit-item-protein").value || 0),
            fat: Number(document.getElementById("edit-item-fat").value || 0),
            carbs: Number(document.getElementById("edit-item-carb").value || 0)
        };

        fetch(`/api/nutrition/items/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        }).then(() => {
            closeModal("modal-edit-item");
            loadDay();
        });
    });

    // ОНОВИТИ ВАГУ
    document.getElementById("open-update-weight").addEventListener("click", () => {
        document.getElementById("update-weight-value").value = "";
        openModal("modal-update-weight");
    });

    document.getElementById("close-update-weight").addEventListener("click", () => {
        closeModal("modal-update-weight");
    });

    document.getElementById("save-update-weight").addEventListener("click", () => {
        const w = document.getElementById("update-weight-value").value;
        if (!w) return;

        fetch("/api/nutrition/weight", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ weight: Number(w) })
        }).then(() => {
            closeModal("modal-update-weight");
            loadDay();
        });
    });

    // ДОДАТИ ВОДУ
    document.getElementById("open-water-modal").addEventListener("click", () => {
        document.getElementById("water-amount").value = "";
        openModal("modal-water");
    });

    document.getElementById("close-water-modal").addEventListener("click", () => {
        closeModal("modal-water");
    });

    document.getElementById("save-water").addEventListener("click", () => {
        const amount = Number(document.getElementById("water-amount").value || 0);
        if (!amount) return;

        fetch("/api/nutrition/water", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount })
        }).then(() => {
            closeModal("modal-water");
            loadDay();
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setTodayDate();
    setupModals();
    loadDay();
});
function renderMeals(meals) {
    const list = document.getElementById("meals-list");
    list.innerHTML = "";

    if (!meals || !meals.length) {
        const empty = document.createElement("div");
        empty.className = "meals-empty";
        empty.textContent = "Ще немає прийомів за сьогодні.";
        list.appendChild(empty);
        return;
    }

    meals.forEach(meal => {
        const card = document.createElement("div");
        card.className = "meal-card-large";

        const header = document.createElement("div");
        header.className = "meal-header-large";

        const titleBlock = document.createElement("div");
        titleBlock.className = "meal-title-block";

        const title = document.createElement("div");
        title.className = "meal-title";
        title.textContent = meal.name;

        const meta = document.createElement("div");
        meta.className = "meal-meta-large";
        meta.textContent = `${meal.category || "—"} · ${meal.time || "—"} · ${meal.total_calories || 0} ккал`;

        titleBlock.appendChild(title);
        titleBlock.appendChild(meta);

        const actions = document.createElement("div");
        actions.className = "meal-actions-large";

        const btnAddItem = document.createElement("button");
        btnAddItem.className = "btn small";
        btnAddItem.textContent = "Додати продукт";
        btnAddItem.addEventListener("click", () => {
            document.getElementById("add-item-meal-id").value = meal.id;
            document.getElementById("add-item-name").value = "";
            document.getElementById("add-item-kcal").value = 0;
            document.getElementById("add-item-protein").value = 0;
            document.getElementById("add-item-fat").value = 0;
            document.getElementById("add-item-carb").value = 0;
            openModal("modal-add-item");
        });

        const btnEditMeal = document.createElement("button");
        btnEditMeal.className = "btn small";
        btnEditMeal.textContent = "Редагувати";
        btnEditMeal.addEventListener("click", () => {
            document.getElementById("edit-meal-id").value = meal.id;
            document.getElementById("edit-meal-name").value = meal.name || "";
            document.getElementById("edit-meal-category").value = meal.category || "Сніданок";
            document.getElementById("edit-meal-time").value = meal.time || "";
            openModal("modal-edit-meal");
        });

        const btnDeleteMeal = document.createElement("button");
        btnDeleteMeal.className = "btn small danger";
        btnDeleteMeal.textContent = "Видалити";
        btnDeleteMeal.addEventListener("click", () => {
            if (!confirm("Видалити цей прийом?")) return;
            fetch(`/api/nutrition/meals/${meal.id}`, { method: "DELETE" })
                .then(() => loadDay());
        });

        actions.appendChild(btnAddItem);
        actions.appendChild(btnEditMeal);
        actions.appendChild(btnDeleteMeal);

        header.appendChild(titleBlock);
        header.appendChild(actions);

        const itemsBlock = document.createElement("div");
        itemsBlock.className = "meal-items-large";

        if (meal.items && meal.items.length) {
            meal.items.forEach(item => {
                const row = document.createElement("div");
                row.className = "meal-item-row-large";

                const name = document.createElement("div");
                name.className = "meal-item-name-large";
                name.textContent = item.name;

                const macros = document.createElement("div");
                macros.className = "meal-item-macros-large";
                macros.textContent =
                    `${item.calories || 0} ккал · ` +
                    `${item.protein || 0} Б · ` +
                    `${item.fat || 0} Ж · ` +
                    `${item.carbs || 0} В`;

                const itemActions = document.createElement("div");
                itemActions.className = "meal-item-actions-large";

                const btnEditItem = document.createElement("button");
                btnEditItem.className = "btn tiny";
                btnEditItem.textContent = "Ред.";
                btnEditItem.addEventListener("click", () => {
                    document.getElementById("edit-item-id").value = item.id;
                    document.getElementById("edit-item-name").value = item.name || "";
                    document.getElementById("edit-item-kcal").value = item.calories || 0;
                    document.getElementById("edit-item-protein").value = item.protein || 0;
                    document.getElementById("edit-item-fat").value = item.fat || 0;
                    document.getElementById("edit-item-carb").value = item.carbs || 0;
                    openModal("modal-edit-item");
                });

                const btnDeleteItem = document.createElement("button");
                btnDeleteItem.className = "btn tiny danger";
                btnDeleteItem.textContent = "×";
                btnDeleteItem.addEventListener("click", () => {
                    fetch(`/api/nutrition/items/${item.id}`, {
                        method: "DELETE"
                    }).then(() => loadDay());
                });

                itemActions.appendChild(btnEditItem);
                itemActions.appendChild(btnDeleteItem);

                row.appendChild(name);
                row.appendChild(macros);
                row.appendChild(itemActions);

                itemsBlock.appendChild(row);
            });
        } else {
            const emptyItems = document.createElement("div");
            emptyItems.className = "meal-items-empty";
            emptyItems.textContent = "Продукти ще не додані.";
            itemsBlock.appendChild(emptyItems);
        }

        card.appendChild(header);
        card.appendChild(itemsBlock);
        list.appendChild(card);
    });
}
