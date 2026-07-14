import { TrainingAPI } from "./api.js";
import { renderStrengthTestResults } from "./dashboard.js";

export function initStrengthTest() {
    const openBtn = document.getElementById("tr-strength-open");
    const modal = document.getElementById("tr-modal-strength");
    const closeBtns = document.querySelectorAll("[data-close-strength]");
    const submitBtn = document.getElementById("strength-test-submit");
    const successBlock = document.getElementById("strength-success");
    const helpIcon = document.getElementById("strength-help");
    const helpTip = document.getElementById("strength-help-tip");

    if (openBtn && modal) {
        openBtn.onclick = () => {
            modal.classList.add("open");
            if (successBlock) successBlock.classList.add("hidden");
        };
    }

    closeBtns.forEach(btn => {
        btn.onclick = () => modal.classList.remove("open");
    });

    if (helpIcon && helpTip) {
        helpIcon.onclick = () => helpTip.classList.toggle("visible");
    }

    if (submitBtn) {
        submitBtn.onclick = () => {
            const pushups = Number(document.getElementById("st_pushups")?.value) || 0;
            const squats = Number(document.getElementById("st_squats")?.value) || 0;
            const situps = Number(document.getElementById("st_situps")?.value) || 0;

            const text = submitBtn.querySelector(".btn-text");
            const loader = submitBtn.querySelector(".btn-loader");

            if (text && loader) {
                text.classList.add("hidden");
                loader.classList.remove("hidden");
            }

            TrainingAPI.strengthTest({ pushups, squats, situps })
                .then(res => {
                    const perf = res?.raw_performance || res || {};
                    renderStrengthTestResults(perf);
                    if (successBlock) successBlock.classList.remove("hidden");
                })
                .finally(() => {
                    if (text && loader) {
                        loader.classList.add("hidden");
                        text.classList.remove("hidden");
                    }
                });
        };
    }
}
