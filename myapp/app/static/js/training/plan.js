(function () {
  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function openPlanModal() {
    if (window.NosiTraining && typeof window.NosiTraining.openPlanModal === 'function') {
      window.NosiTraining.openPlanModal();
      return;
    }
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
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
      await fetch('/api/plans', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) });
      closeModal();
      location.reload();
    });
  }

  function closeModal() {
    const overlay = qs('#tr-modal-overlay');
    overlay.setAttribute('aria-hidden', 'true');
    qs('#tr-modal').innerHTML = '';
  }

  window.NosiPlan = { openPlanModal, closeModal };
})();
