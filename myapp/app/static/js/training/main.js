(function () {
  const API = {
    today: '/api/training/today',
    plans: '/api/plans',
    exercises: '/api/exercises',
    session: (id) => `/api/session/${id}`,
    saveNotes: (sid) => `/api/session/${sid}/notes`
  };

  const state = {
    today: null,
    plan: null,
    exercisesBank: [],
    modalOpen: false
  };

  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  async function fetchJson(url, opts) {
    try {
      const res = await fetch(url, opts);
      if (!res.ok) throw new Error('no-data');
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  async function loadFixturesIfNeeded() {
    const data = await fetchJson(API.today);
    if (data) return data;
    return {
      sessionId: 'fixture-1',
      title: 'Upper Body Strength · День 3',
      type: 'Сила',
      duration: 48,
      exercises: [
        { id: 'ex1', name: 'Жим лежачи', sets: 4, reps: 8, location: 'зал' },
        { id: 'ex2', name: 'Підтягування', sets: 3, reps: 6, location: 'зал' },
        { id: 'ex3', name: 'Жим плечима', sets: 3, reps: 10, location: 'зал' }
      ],
      muscles: { Груди: 0.8, Спина: 0.5, Ноги: 0.2, Плечі: 0.6, Руки: 0.4, Кор: 0.3 },
      plan: [{ id: 'p1', name: 'Мій спліт' }],
      recommendations: ['Додати більше спини наступного тижня', 'Зменшити об’єм ніг']
    };
  }

  function renderSession(data) {
    state.today = data;
    const titleEl = qs('#tr-session-title');
    const typeEl = qs('#tr-session-type');
    const durEl = qs('#tr-session-duration');
    titleEl.textContent = data.title || 'Сьогодні';
    typeEl.textContent = data.type || '—';
    durEl.textContent = (data.duration || '—') + ' хв';
    renderExercises(data.exercises || []);
    renderSummary(data.exercises || []);
    renderRecs(data.recommendations || []);
  }

  function renderExercises(list) {
    const ul = qs('#tr-exercises');
    ul.innerHTML = '';
    list.forEach((ex, idx) => {
      const li = document.createElement('li');
      li.className = 'tr-exercise-item tr-animate-pop';
      li.dataset.idx = idx;
      li.innerHTML = `
        <div class="tr-ex-left">
          <div class="tr-ex-avatar">${(ex.name||'').slice(0,2).toUpperCase()}</div>
          <div>
            <div class="tr-ex-name">${ex.name}</div>
            <div class="tr-ex-meta">${ex.sets}×${ex.reps} · ${ex.location || 'будь-де'}</div>
          </div>
        </div>
        <div class="tr-ex-actions">
          <button class="tr-btn tr-btn--ghost tr-btn-edit" data-idx="${idx}">Редагувати</button>
          <button class="tr-btn tr-btn--primary tr-btn-start-ex" data-idx="${idx}">Почати</button>
        </div>
      `;
      ul.appendChild(li);
    });
    qsa('.tr-btn-start-ex').forEach(b => b.addEventListener('click', onStartExercise));
    qsa('.tr-btn-edit').forEach(b => b.addEventListener('click', onEditExercise));
  }

  function renderSummary(list) {
    qs('#tr-summary-ex-count').textContent = list.length;
    const volume = list.reduce((s, ex) => s + (ex.sets * (ex.reps || 0)), 0);
    qs('#tr-summary-volume').textContent = volume;
    const muscles = Object.keys(state.today.muscles || {}).filter(k => (state.today.muscles[k]||0) > 0.3);
    qs('#tr-summary-main-muscles').textContent = muscles.slice(0,3).join(', ') || '—';
  }

  function renderRecs(recs) {
    const el = qs('#tr-recs');
    el.innerHTML = '';
    (recs || []).forEach(r => {
      const d = document.createElement('div');
      d.className = 'tr-rec-item';
      d.innerHTML = `<div class="tr-rec-icon">!</div><div class="tr-rec-body"><div class="tr-rec-title">${r}</div></div>`;
      el.appendChild(d);
    });
    if (!(recs||[]).length) el.innerHTML = '<div class="tr-empty">Рекомендацій поки що немає</div>';
  }

  function renderPlanList(plans) {
    const el = qs('#tr-plan-list');
    if (!el) return;
    el.innerHTML = '';
    (plans || []).forEach(p => {
      const div = document.createElement('div');
      div.className = 'tr-plan-item';
      div.innerHTML = `<div>${p.name}</div><div><button class="tr-btn tr-btn--ghost tr-open-plan" data-id="${p.id}">Відкрити</button></div>`;
      el.appendChild(div);
    });
    qsa('.tr-open-plan').forEach(b => b.addEventListener('click', e => openPlanModal()));
  }

  function wireHeaderButtons() {
    const start = qs('#tr-start');
    const edit = qs('#tr-edit-plan');
    const openPlan = qs('#tr-open-plan');
    if (start) start.addEventListener('click', onStartSession);
    if (edit) edit.addEventListener('click', openPlanModal);
    if (openPlan) openPlan.addEventListener('click', openPlanModal);
    const newPlan = qs('#tr-new-plan');
    if (newPlan) newPlan.addEventListener('click', openPlanModal);
  }

  function onStartSession() {
    if (state.today && state.today.sessionId) {
      window.location.href = `/training/session?session=${encodeURIComponent(state.today.sessionId)}`;
    } else {
      openToast('Немає активної сесії для запуску', 'warn');
    }
  }

  function onStartExercise(e) {
    const idx = Number(e.currentTarget.dataset.idx);
    const ex = (state.today.exercises || [])[idx];
    if (!ex) return;
    openModalExercise(ex, idx);
  }

  function onEditExercise(e) {
    const idx = Number(e.currentTarget.dataset.idx);
    const ex = (state.today.exercises || [])[idx];
    if (!ex) return;
    openModalEditExercise(ex, idx);
  }

  function openModalExercise(ex, idx) {
    const modal = qs('#tr-modal');
    const overlay = qs('#tr-modal-overlay');
    overlay.setAttribute('aria-hidden', 'false');
    modal.innerHTML = `
      <h3 style="margin:0 0 8px 0">${ex.name}</h3>
      <p class="cmp-card-sub">${ex.sets}×${ex.reps} · ${ex.location || 'будь-де'}</p>
      <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
        <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel">Закрити</button>
        <button class="tr-btn tr-btn--primary" id="tr-modal-start-ex" data-idx="${idx}">Почати</button>
      </div>
    `;
    qs('#tr-modal-cancel').addEventListener('click', closeModal);
    qs('#tr-modal-start-ex').addEventListener('click', () => {
      closeModal();
      if (state.today && state.today.sessionId) {
        window.location.href = `/training/session?session=${encodeURIComponent(state.today.sessionId)}&focus=${idx}`;
      } else {
        openToast('Немає сесії', 'warn');
      }
    });
  }

  function openModalEditExercise(ex, idx) {
    const modal = qs('#tr-modal');
    const overlay = qs('#tr-modal-overlay');
    overlay.setAttribute('aria-hidden', 'false');
    modal.innerHTML = `
      <h3 style="margin:0 0 8px 0">Редагувати: ${ex.name}</h3>
      <div style="display:flex; gap:8px; margin-top:8px;">
        <div style="flex:1">
          <label class="cmp-label">Підходи</label>
          <input id="tr-edit-sets" class="cmp-input" type="number" min="1" value="${ex.sets}">
        </div>
        <div style="width:120px">
          <label class="cmp-label">Повторення</label>
          <input id="tr-edit-reps" class="cmp-input" type="number" min="1" value="${ex.reps}">
        </div>
      </div>
      <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
        <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel">Скасувати</button>
        <button class="tr-btn tr-btn--primary" id="tr-modal-save">Зберегти</button>
      </div>
    `;
    qs('#tr-modal-cancel').addEventListener('click', closeModal);
    qs('#tr-modal-save').addEventListener('click', () => {
      const sets = Number(qs('#tr-edit-sets').value) || ex.sets;
      const reps = Number(qs('#tr-edit-reps').value) || ex.reps;
      state.today.exercises[idx].sets = sets;
      state.today.exercises[idx].reps = reps;
      renderExercises(state.today.exercises);
      renderSummary(state.today.exercises);
      closeModal();
      openToast('Вправа оновлена', 'success');
    });
  }

  function closeModal() {
    const overlay = qs('#tr-modal-overlay');
    overlay.setAttribute('aria-hidden', 'true');
    qs('#tr-modal').innerHTML = '';
  }

  function openPlanModal() {
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
    overlay.setAttribute('aria-hidden', 'false');
    modal.innerHTML = `
      <h3 style="margin:0 0 8px 0">Редагувати план</h3>
      <label class="cmp-label">Назва плану</label>
      <input id="tr-modal-plan-name" class="cmp-input" value="${(state.plan && state.plan.name) || 'Мій план'}">
      <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
        <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel">Скасувати</button>
        <button class="tr-btn tr-btn--primary" id="tr-modal-save-plan">Зберегти</button>
      </div>
    `;
    qs('#tr-modal-cancel').addEventListener('click', closeModal);
    qs('#tr-modal-save-plan').addEventListener('click', async () => {
      const name = qs('#tr-modal-plan-name').value.trim() || 'Мій план';
      await fetchJson(API.plans, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) });
      closeModal();
      openToast('План збережено', 'success');
      init();
    });
  }

  function openToast(text, type = 'success') {
    const t = document.createElement('div');
    t.className = `tr-toast ${type === 'warn' ? 'warn' : type === 'error' ? 'error' : 'success'}`;
    t.textContent = text;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add('show'), 20);
    setTimeout(() => t.remove(), 3500);
  }

  function wireQuickBuilder() {
    const muscle = qs('#tr-builder-muscle');
    const location = qs('#tr-builder-location');
    const exercise = qs('#tr-builder-exercise');
    const form = qs('#tr-quick-builder');

    muscle && muscle.addEventListener('change', async () => {
      const m = muscle.value;
      exercise.innerHTML = '<option>Завантаження...</option>';
      const list = await fetchJson(`${API.exercises}?muscle=${encodeURIComponent(m)}`) || [];
      state.exercisesBank = list;
      exercise.innerHTML = '<option value="">Оберіть вправу</option>';
      (list || []).forEach(ex => {
        const opt = document.createElement('option');
        opt.value = ex.id;
        opt.textContent = ex.name;
        exercise.appendChild(opt);
      });
    });

    form && form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const exId = exercise.value;
      const sets = Number(qs('#tr-builder-sets').value) || 3;
      const reps = Number(qs('#tr-builder-reps').value) || 10;
      const exObj = (state.exercisesBank || []).find(x => x.id === exId) || { id: exId, name: exercise.options[exercise.selectedIndex]?.text || 'Нова вправа', location: location.value };
      state.today = state.today || { exercises: [] };
      state.today.exercises = state.today.exercises || [];
      state.today.exercises.push({ id: exObj.id || `tmp-${Date.now()}`, name: exObj.name, sets, reps, location: exObj.location || location.value });
      renderExercises(state.today.exercises);
      renderSummary(state.today.exercises);
      openToast('Вправа додана в сесію', 'success');
      form.reset();
    });
  }

  function wireTooltips() {
    qsa('.tr-help').forEach(btn => {
      const tip = btn.dataset.tooltip || '';
      if (!tip) return;
      const anchor = btn;
      anchor.addEventListener('mouseenter', (e) => {
        let tt = anchor._tt;
        if (!tt) {
          tt = document.createElement('div');
          tt.className = 'tr-tooltip small';
          tt.innerHTML = `<div class="tr-tooltip-body">${escapeHtml(tip)}</div>`;
          document.body.appendChild(tt);
          anchor._tt = tt;
        }
        positionTooltip(anchor, tt);
        tt.classList.add('show');
      });
      anchor.addEventListener('mousemove', (ev) => {
        const tt = anchor._tt;
        if (tt) positionTooltip(anchor, tt, ev);
      });
      anchor.addEventListener('mouseleave', () => {
        const tt = anchor._tt;
        if (tt) tt.classList.remove('show');
      });
    });
  }

  function positionTooltip(anchor, tt, ev) {
    const rect = anchor.getBoundingClientRect();
    const left = rect.left + window.scrollX;
    const top = rect.bottom + window.scrollY + 8;
    tt.style.left = (left) + 'px';
    tt.style.top = (top) + 'px';
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (m) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
  }

  function wireModalOverlay() {
    const overlay = qs('#tr-modal-overlay');
    overlay && overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal();
    });
  }

  async function init() {
    wireHeaderButtons();
    wireQuickBuilder();
    wireTooltips();
    wireModalOverlay();
    const data = await loadFixturesIfNeeded();
    renderSession(data);
    renderPlanList(data.plan || []);
    renderRadar('#tr-radar', data.muscles || {});
  }

  window.NosiTraining = {
    init,
    openPlanModal,
    closeModal,
    renderRadar: (sel, data) => renderRadar(sel, data)
  };

  function renderRadar(sel, muscles) {
    if (window.NosiRadar && typeof window.NosiRadar.render === 'function') {
      window.NosiRadar.render(sel, muscles);
      return;
    }
    const el = (typeof sel === 'string') ? document.querySelector(sel) : sel;
    if (!el) return;
    el.innerHTML = '<div class="tr-visual-placeholder">Радарна діаграма (завантаження)</div>';
  }

  document.addEventListener('DOMContentLoaded', init);
})();
