document.getElementById("save-start-session").addEventListener("click", async () => {
    const title = document.getElementById("start-session-title").value || "Нова сесія";

    const res = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
    });

    closeModal("modal-start-session");
    loadTodaySession();
});

document.getElementById("confirm-finish-session").addEventListener("click", async () => {
    const sessionType = document.getElementById("tr-session-type").textContent;
    if (!sessionType.startsWith("plan-") && sessionType !== "fallback") return;

    const id = sessionType.replace("plan-", "");

    await fetch(`/api/session/${id}/finish`, { method: "POST" });

    closeModal("modal-finish-session");
    loadTodaySession();
});
