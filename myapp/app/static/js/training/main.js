(function () {
  'use strict';
  const state = {
    today: null,
    plan: null,
    plans: [],
    exercisesBank: [],
    currentSession: null,
    ui: { modalOpen: false },
    offlineQueueKey: 'nosi_offline_queue_v3'
  };
  function qs(sel, root = document) { return (root || document).querySelector(sel); }
  function qsa(sel, root = document) { return Array.from((root || document).querySelectorAll(sel)); }
  function el(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function nowIso() { return new Date().toISOString(); }
  function safeJSONParse(s, fallback = null) { if (typeof s !== 'string') return fallback; try { return JSON.parse(s); } catch { return fallback; } }
  function debounce(fn, ms = 300) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
  function openToast(text, type = 'info', timeout = 2400) {
    const container = qs('#tr-toast-container');
    if (!container) return;
    const t = el('div', 'tr-toast');
    if (type === 'success') t.classList.add('success');
    if (type === 'warn') t.classList.add('warn');
    if (type === 'error') t.classList.add('error');
    t.innerHTML = `<div class="title">${text}</div>`;
    container.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, timeout);
  }
  const OfflineQueue = (function () {
    const KEY = state.offlineQueueKey;
    function load() {
      const raw = localStorage.getItem(KEY);
      const parsed = safeJSONParse(raw, []);
      return Array.isArray(parsed) ? parsed : [];
    }
    function save(q) { localStorage.setItem(KEY, JSON.stringify(Array.isArray(q) ? q : [])); }
    async function flush() {
      const q = load();
      if (!q.length) return;
      const remaining = [];
      for (const item of q) {
        try {
          if (item.type === 'addExercise') await API.addExerciseToSession(item.sessionId, item.exerciseId, item.payload);
          if (item.type === 'createSession') await API.createSession(item.payload);
          if (item.type === 'finishSession') await API.finishSession(item.sessionId);
        } catch (e) { remaining.push(item); }
      }
      save(remaining);
    }
    function push(item) { const q = load(); q.push(item); save(q); }
    return { load, save, flush, push };
  })();
  async function loadInitialData() {
    try {
      const plan = await API.safe(() => API.getTrainingPlan(1));
      state.plan = plan || null;
      state.plans = state.plan ? [state.plan] : [];
    } catch (e) {
      state.plan = null;
      state.plans = [];
    }
    try {
      const exercises = await API.safe(() => API.listExercises());
      state.exercisesBank = Array.isArray(exercises) ? exercises : [];
    } catch (e) {
      state.exercisesBank = [];
    }
    try {
      const today = await API.safe(() => API.getTrainingToday());
      state.today = today || null;
    } catch (e) {
      state.today = null;
    }
    if (!state.exercisesBank.length) {
      state.exercisesBank = [
        { id: 'ex-fixt-1', name: 'Жим лежачи', muscle: 'Груди', equipment: 'Штанга' },
        { id: 'ex-fixt-2', name: 'Підтягування', muscle: 'Спина', equipment: 'Турнік' },
        { id: 'ex-fixt-3', name: 'Присідання', muscle: 'Ноги', equipment: 'Штанга' }
      ];
    }
  }
  function renderHeader() {
    const titleEl = qs('#tr-session-title');
    const typeEl = qs('#tr-session-type');
    const durEl = qs('#tr-session-duration');
    if (titleEl) titleEl.textContent = state.plan?.name || state.today?.title || 'Тренування';
    if (typeEl) typeEl.textContent = state.plan?.type || state.today?.type || '—';
    if (durEl) durEl.textContent = state.plan?.duration ? `${state.plan.duration} хв` : (state.today?.duration ? `${state.today.duration} хв` : '—');
  }
  function renderRadar() {
    const container = qs('#tr-radar');
    if (!container) return;
    const radarData = state.plan?.meta?.radar || state.today?.muscles || {};
    if (window.NosiRadar) NosiRadar.render(container, radarData, { duration: 700 });
    else container.textContent = 'Радар недоступний';
  }
  function renderLegend() {
    const legend = qs('#tr-legend');
    if (!legend) return;
    legend.innerHTML = '';
    const muscles = state.plan?.meta?.muscles || Object.keys(state.today?.muscles || {});
    (muscles || []).forEach((m, i) => {
      const item = el('div', 'tr-legend-item');
      item.dataset.index = i;
      const sw = el('span', `tr-legend-swatch ${i % 3 === 0 ? 'yellow' : i % 3 === 1 ? 'purple' : 'teal'}`);
      const lbl = el('span', 'tr-legend-label');
      lbl.textContent = m;
      item.appendChild(sw);
      item.appendChild(lbl);
      item.addEventListener('click', () => { item.classList.toggle('is-muted'); });
      legend.appendChild(item);
    });
  }
  function renderPlanSelector() {
    const elTitle = qs('#tr-session-title');
    if (elTitle) elTitle.setAttribute('data-plan', state.plan?.name || 'Немає активного плану');
  }
  function renderPlanPanel() {
    renderPlanSelector();
    renderHeader();
    renderRadar();
    renderLegend();
    renderBalanceHints();
  }
  function renderBalanceHints() {
    const list = qs('#tr-balance-list');
    if (!list) return;
    list.innerHTML = '';
    const hints = state.plan?.meta?.balance_hints || ['Розподіли навантаження між великими групами'];
    hints.forEach(h => {
      const li = el('li', 'tr-balance-item');
      li.textContent = h;
      list.appendChild(li);
    });
  }
  function renderExercisesList(exercises) {
    const list = qs('#tr-exercises');
    if (!list) return;
    list.innerHTML = '';
    exercises.forEach((ex, idx) => {
      const li = el('li', 'tr-exercise-row');
      li.dataset.index = idx;
      const left = el('div', 'tr-ex-left');
      left.innerHTML = `<strong class="tr-ex-name">${ex.name}</strong><div class="tr-ex-meta">${(ex.sets && ex.sets.length) || (ex.sets || 1)} підходи · ${ex.reps || '—'} повт.</div>`;
      const right = el('div', 'tr-ex-right');
      const sets = ex.sets || Array.from({ length: ex.sets || 1 }).map(() => ({ weight: null, reps: ex.reps || '' }));
      sets.forEach((s, si) => {
        const setRow = el('div', 'tr-set-row');
        const weightVal = (s && s.weight != null) ? s.weight : '';
        setRow.innerHTML = `<label class="tr-set-label">S${si + 1}</label>
          <input class="tr-set-input tr-input" data-set="${si}" data-ex="${idx}" value="${weightVal}" placeholder="кг" aria-label="Вага підходу ${si + 1}">
          <input class="tr-set-reps tr-input" data-set="${si}" data-ex="${idx}" value="${s && s.reps ? s.reps : ex.reps || ''}" placeholder="повт." aria-label="Повторення підходу ${si + 1}">
          <button class="tr-set-done tr-btn tr-btn--ghost" data-ex="${idx}" data-set="${si}" type="button">${s && s.done ? '✓' : 'Готово'}</button>`;
        right.appendChild(setRow);
      });
      li.appendChild(left);
      li.appendChild(right);
      list.appendChild(li);
    });
    qsa('.tr-set-input', list).forEach(inp => inp.addEventListener('input', debounce(onExerciseInput, 300)));
    attachExerciseHandlers();
  }
  function renderSessionPanel() {
  const titleEl = qs('#tr-session-title');
  const typeEl = qs('#tr-session-type');
  const durEl = qs('#tr-session-duration');
  if (!state.currentSession) {
    if (titleEl) titleEl.textContent = 'Немає активної сесії';
    if (typeEl) typeEl.textContent = '—';
    if (durEl) durEl.textContent = '— хв';
    renderExercisesList([]);
    return;
  }
  if (titleEl) titleEl.textContent = state.currentSession.title || 'Поточна сесія';
  if (typeEl) typeEl.textContent = state.currentSession.type || '—';
  const started = state.currentSession.started_at ? new Date(state.currentSession.started_at).getTime() : null;
  const durationMs = started ? (Date.now() - started) : 0;
  if (durEl) durEl.textContent = `${Math.round(durationMs / 60000)} хв`;
  renderExercisesList(state.currentSession.data?.exercises || []);
  renderSessionProgress();
}

  function renderQuickStats() {
    qs('#tr-week-load') && (qs('#tr-week-load').textContent = state.plan?.meta?.weekly_load || '—');
    qs('#tr-focus-muscles') && (qs('#tr-focus-muscles').textContent = state.plan?.meta?.focus || '—');
    qs('#tr-week-sessions') && (qs('#tr-week-sessions').textContent = state.plan ? `${state.plan.meta?.planned_sessions||0} · ${state.plan.meta?.done_sessions||0}` : '—');
    qs('#tr-fatigue') && (qs('#tr-fatigue').textContent = state.plan?.meta?.fatigue || '—');
  }
  function renderRecommendations() {
    const container = qs('#tr-recs');
    if (!container) return;
    container.innerHTML = '';
    const recs = state.plan?.meta?.recommendations || state.today?.recommendations || ['Підтримуйте прогрес: додавайте 2.5% ваги кожні 2 тижні.'];
    recs.forEach(r => {
      const d = el('div', 'tr-rec');
      d.textContent = r;
      container.appendChild(d);
    });
  }
  function onExerciseInput(e) {
    const exIdx = Number(e.target.dataset.ex);
    const setIdx = Number(e.target.dataset.set);
    if (!state.currentSession || !state.currentSession.data) return;
    const val = e.target.value.trim();
    const ex = state.currentSession.data.exercises[exIdx];
    if (!ex) return;
    ex.sets = ex.sets || [];
    ex.sets[setIdx] = ex.sets[setIdx] || {};
    ex.sets[setIdx].weight = val ? Number(val) : null;
    scheduleSessionAutosave();
  }
  function onExerciseSetDone(e) {
    const exIdx = Number(e.currentTarget.dataset.ex);
    const setIdx = Number(e.currentTarget.dataset.set);
    if (!state.currentSession || !state.currentSession.data) return;
    const ex = state.currentSession.data.exercises[exIdx];
    if (!ex) return;
    ex.sets = ex.sets || [];
    ex.sets[setIdx] = ex.sets[setIdx] || {};
    ex.sets[setIdx].done = true;
    e.currentTarget.textContent = '✓';
    e.currentTarget.disabled = true;
    scheduleSessionAutosave();
    renderSessionProgress();
  }
  function renderSessionProgress() {
    const done = qsa('.tr-set-done').filter(b => b.textContent.trim() === '✓').length;
    const total = qsa('.tr-set-row').length || 0;
    const fill = qs('#tr-progress-fill');
    if (fill) fill.style.width = `${Math.round((done / Math.max(1, total)) * 100)}%`;
    qs('#tr-progress-text') && (qs('#tr-progress-text').textContent = `${done} / ${total}`);
    qs('#tr-overview-sets-done') && (qs('#tr-overview-sets-done').textContent = done);
  }
  function loadLocalSession() { return safeJSONParse(localStorage.getItem('nosi_current_session'), null); }
  function saveLocalSession() { if (!state.currentSession) return; localStorage.setItem('nosi_current_session', JSON.stringify(state.currentSession)); }
  const scheduleSessionAutosave = debounce(function () {
    saveLocalSession();
    if (state.currentSession && state.currentSession.id && !String(state.currentSession.id).startsWith('local-')) {
      OfflineQueue.push({ type: 'addExercise', sessionId: state.currentSession.id, exerciseId: 'autosave', payload: { data: state.currentSession.data } });
    } else {
      OfflineQueue.push({ type: 'createSession', payload: { title: state.currentSession?.title || 'Локальна сесія', started_at: state.currentSession?.started_at || nowIso() } });
    }
  }, 800);
  async function startSessionFlow() {
    if (state.currentSession) return;
    const payload = { plan_id: state.plan?.id || null, title: `Сесія ${new Date().toLocaleString()}`, started_at: nowIso() };
    try {
      const created = await API.createSession(payload);
      if (created && created.id) {
        state.currentSession = { id: created.id, plan_id: created.plan_id, title: created.title, started_at: created.started_at, data: { exercises: [] } };
        saveLocalSession();
        renderSessionPanel();
      } else {
        throw new Error('no-created-id');
      }
    } catch (err) {
      state.currentSession = { id: `local-${Date.now()}`, plan_id: state.plan?.id || null, title: payload.title, started_at: payload.started_at, data: { exercises: [] } };
      OfflineQueue.push({ type: 'createSession', payload });
      saveLocalSession();
      renderSessionPanel();
      openToast('Старт сесії помилка, збережено локально', 'warn');
    }
  }
  function buildExercisesFromPlan(plan) {
    const day = plan?.meta?.days?.[0] || { exercises: [] };
    return (day.exercises || []).map(ex => ({
      exercise_id: ex.exercise_id || null,
      name: ex.name || 'Вправа',
      reps: ex.reps || null,
      sets: (ex.sets || [{ target: null }]).map(s => ({ weight: s.target || null, reps: s.reps || ex.reps || null, done: false }))
    }));
  }
  function attachExerciseHandlers() {
    const list = qs('#tr-exercises');
    if (!list) return;
    list.removeEventListener && list.removeEventListener('click', exerciseListClick);
    list.addEventListener('click', exerciseListClick);
    qsa('.tr-set-done', list).forEach(btn => {
      btn.removeEventListener && btn.removeEventListener('click', onExerciseSetDone);
      btn.addEventListener('click', onExerciseSetDone);
    });
  }
  function exerciseListClick(e) {
    const btn = e.target.closest('.tr-set-done');
    if (!btn) return;
    const exIdx = Number(btn.dataset.ex);
    const setIdx = Number(btn.dataset.set);
    if (!state.currentSession || !state.currentSession.data) return;
    const ex = state.currentSession.data.exercises[exIdx];
    if (!ex) return;
    ex.sets = ex.sets || [];
    ex.sets[setIdx] = ex.sets[setIdx] || {};
    ex.sets[setIdx].done = true;
    btn.textContent = '✓';
    btn.disabled = true;
    scheduleSessionAutosave();
    renderSessionProgress();
  }
  function loadExercisesForBuilder(exSelectSel = '#tr-builder-exercise', muscleSelectSel = '#tr-builder-muscle') {
    const exSel = document.querySelector(exSelectSel);
    const mSel = document.querySelector(muscleSelectSel);
    if (!exSel || !mSel) return;
    const musclesSet = new Set();
    (state.exercisesBank || []).forEach(ex => { if (ex.muscle) musclesSet.add(ex.muscle); });
    mSel.innerHTML = '<option value="">Оберіть м\'яз</option>';
    Array.from(musclesSet).sort().forEach(m => {
      const o = document.createElement('option');
      o.value = m;
      o.textContent = m;
      mSel.appendChild(o);
    });
    function populateExercises(filterMuscle = '') {
      exSel.innerHTML = '<option value="">Оберіть вправу</option>';
      (state.exercisesBank || []).filter(ex => {
        if (!filterMuscle) return true;
        return String(ex.muscle || '').toLowerCase() === String(filterMuscle).toLowerCase();
      }).forEach(ex => {
        const o = document.createElement('option');
        o.value = ex.id || ex.name;
        o.textContent = ex.name + (ex.equipment ? ` · ${ex.equipment}` : '');
        o.dataset.muscle = ex.muscle || '';
        exSel.appendChild(o);
      });
    }
    populateExercises();
    mSel.addEventListener('change', () => populateExercises(mSel.value));
    window._loadExercisesForBuilder = populateExercises;
  }
  function wireBuilderAdd(buttonSel = '#tr-builder-add') {
    const btn = document.querySelector(buttonSel);
    if (!btn) return;
    btn.addEventListener('click', async () => {
      const exSel = document.querySelector('#tr-builder-exercise');
      const muscleSel = document.querySelector('#tr-builder-muscle');
      const locSel = document.querySelector('#tr-builder-location');
      const setsInp = document.querySelector('#tr-builder-sets');
      const repsInp = document.querySelector('#tr-builder-reps');
      if (!exSel || !exSel.value) { openToast('Оберіть вправу', 'warn'); return; }
      const exName = exSel.options[exSel.selectedIndex].textContent;
      const exId = exSel.value;
      const muscle = muscleSel ? muscleSel.value : '';
      const location = locSel ? locSel.value : '';
      const sets = Math.max(1, Number(setsInp?.value || 1));
      const reps = Math.max(1, Number(repsInp?.value || 1));
      const newEx = { exercise_id: exId, name: exName, muscle, location, reps, sets: Array.from({ length: sets }).map(() => ({ weight: null, reps, done: false })) };
      if (!state.currentSession) {
        state.currentSession = { id: `local-${Date.now()}`, title: `Локальна сесія ${new Date().toLocaleString()}`, started_at: new Date().toISOString(), data: { exercises: [] } };
      }
      state.currentSession.data = state.currentSession.data || { exercises: [] };
      state.currentSession.data.exercises.push(newEx);
      saveLocalSession();
      renderSessionPanel();
      try {
        if (state.currentSession && state.currentSession.id && !String(state.currentSession.id).startsWith('local-')) {
          await API.addExerciseToSession(state.currentSession.id, exId, { exercise: newEx });
        } else {
          OfflineQueue.push({ type: 'addExercise', sessionId: state.currentSession.id || `local-${Date.now()}`, exerciseId: exId, payload: { exercise: newEx } });
        }
      } catch (e) {
        OfflineQueue.push({ type: 'addExercise', sessionId: state.currentSession.id || `local-${Date.now()}`, exerciseId: exId, payload: { exercise: newEx } });
      }
      openToast('Вправа додана в сесію', 'success');
    });
  }
  function attachUI() {
    const startBtn = qs('#tr-start');
    const openPlan = qs('#tr-open-plan');
    const editPlanBtn = qs('#tr-edit-plan');
    const overlay = qs('#tr-modal-overlay');
    if (startBtn) startBtn.addEventListener('click', startSessionFlow);
    if (openPlan) openPlan.addEventListener('click', () => { if (state.plan) window.location.href = `/plan/view`; else openToast('У вас немає активного плану', 'warn'); });
    if (editPlanBtn) editPlanBtn.addEventListener('click', () => {});
    if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
    document.addEventListener('keydown', (e) => {
      if (e.key === 's' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); if (state.currentSession) scheduleSessionAutosave(); }
      if (e.key === 'Escape' && state.ui.modalOpen) closeModal();
    });
    window.addEventListener('online', () => { OfflineQueue.flush().catch(() => { }); });
  }
  function openModal(html) {
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
    if (!overlay || !modal) return;
    overlay.setAttribute('aria-hidden', 'false');
    modal.innerHTML = html;
    state.ui.modalOpen = true;
  }
  function closeModal() {
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
    if (!overlay || !modal) return;
    overlay.setAttribute('aria-hidden', 'true');
    modal.innerHTML = '';
    state.ui.modalOpen = false;
  }
  async function init() {
    attachUI();
    await loadInitialData();
    const saved = loadLocalSession();
    if (saved) state.currentSession = saved;
    renderHeader();
    renderRadar();
    renderLegend();
    renderPlanPanel();
    renderQuickStats();
    renderSessionPanel();
    renderBalanceHints();
    renderNextSessionPreview();
    renderRecommendations();
    try { loadExercisesForBuilder('#tr-builder-exercise', '#tr-builder-muscle'); wireBuilderAdd('#tr-builder-add'); } catch (e) { }
    OfflineQueue.flush().catch(() => { });
  }
  function renderNextSessionPreview() {
    qs('#tr-next-session-title') && (qs('#tr-next-session-title').textContent = state.plan?.meta?.next_session?.title || '—');
    qs('#tr-next-type') && (qs('#tr-next-type').textContent = state.plan?.meta?.next_session?.type || '—');
    qs('#tr-next-muscles') && (qs('#tr-next-muscles').textContent = (state.plan?.meta?.next_session?.muscles || []).join(', ') || '—');
    qs('#tr-next-duration') && (qs('#tr-next-duration').textContent = state.plan?.meta?.next_session?.duration ? `${state.plan.meta.next_session.duration}` : '—');
  }
  window.TrainingMain = { state, init, startSessionFlow, renderSessionPanel, renderRadar, OfflineQueue };
  document.addEventListener('DOMContentLoaded', init);
})();
