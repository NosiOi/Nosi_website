document.addEventListener("click", (e) => {
  const openBtn = e.target.closest("[data-modal]");
  if (openBtn) {
    const id = openBtn.getAttribute("data-modal");
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("is-open");
  }

  if (e.target.matches("[data-close-modal]") || e.target.classList.contains("modal-backdrop")) {
    const backdrop = e.target.closest(".modal-backdrop");
    if (backdrop) backdrop.classList.remove("is-open");
  }
});
