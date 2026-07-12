import { state, normalize } from "../state.js";
import { savePlanAPI } from "./api.js";
import { showToast } from "../ui/toast.js";

export async function savePlan(name, modal) {
    const btn = document.getElementById("tr-plan-save");
    const text = btn.querySelector(".btn-text");
    const loader = btn.querySelector(".btn-loader");

    const payload = {
        name: name || "Мій план",
        is_active: true,
        days: state.days
    };

    btn.disabled = true;
    text.classList.add("hidden");
    loader.classList.remove("hidden");

    try {
        const saved = await savePlanAPI(payload);
        window.trainingStore.plan = saved;
        state.days = normalize(saved.days || {});
        showToast("План збережено");
        setTimeout(() => modal.classList.remove("open"), 600);
    } catch {
        showToast("Помилка збереження");
    } finally {
        btn.disabled = false;
        loader.classList.add("hidden");
        text.classList.remove("hidden");
    }
}
