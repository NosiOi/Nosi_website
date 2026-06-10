(function () {
  function qs(s, r = document) { return (r || document).querySelector(s); }
  function qsa(s, r = document) { return Array.from((r || document).querySelectorAll(s)); }

  function openPlanModal() {
    if (window.NosiTraining && typeof window.NosiTraining.openPlanModal === 'function') {
      window.NosiTraining.openPlanModal();
      return;
    }
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
    if (!overlay || !modal) return;
    overlay.setAttribute('aria-hidden', 'false');
    modal.innerHTML = `
      <h3 style="margin:0 0 8px 0">Редагувати план (швидко)</h3>
      <label class="cmp-label">Назва</label>
      <input id="tr-modal-plan-name" class="cmp-input" value="Мій план">
      <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
        <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel">Скасувати</button>
        <button class="tr-btn tr-btn--primary" id="tr-modal-save">Зберегти</button>
      </div>
    `;
    qs('#tr-modal-cancel').addEventListener('click', closeModal);
    qs('#tr-modal-save').addEventListener('click', async () => {
      const name = qs('#tr-modal-plan-name').value.trim() || 'Мій план';
      try {
        await fetch('/api/plans', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) });
      } catch (e) {
        console.warn('Save plan error', e);
      }
      closeModal();
      location.reload();
    });
  }

  function closeModal() {
    const overlay = qs('#tr-modal-overlay');
    if (!overlay) return;
    overlay.setAttribute('aria-hidden', 'true');
    qs('#tr-modal').innerHTML = '';
  }

  document.addEventListener('DOMContentLoaded', () => {
    const open = qs('#tr-open-plan');
    if (open) open.addEventListener('click', openPlanModal);
    const cancel = qs('#tr-modal-cancel');
    if (cancel) cancel.addEventListener('click', closeModal);
  });

  window.NosiPlan = { openPlanModal, closeModal };
})();
