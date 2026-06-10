(function () {
  'use strict';

  const ROUTES = {
    today: '/api/training/today',
    plans: '/api/training/plans',
    plan: (id) => `/api/training/plans/${encodeURIComponent(id)}`,
    exercises: '/api/exercises',
    sessions: '/api/training/sessions',
    session: (id) => `/api/training/sessions/${encodeURIComponent(id)}`,
    preferences: '/api/user/preferences'
  };

  const SELECTORS = {
    headerTitle: '#tr-session-title',
    headerType: '#tr-session-type',
    headerDuration: '#tr-session-duration',
    radar: '#tr-radar',
    legend: '#tr-legend',
    exercisesList: '#tr-exercises',
    weekLoad: '#tr-week-load',
    focusMuscles: '#tr-focus-muscles',
    weekSessions: '#tr-week-sessions',
    fatigue: '#tr-fatigue',
    premiumMuscles: '#tr-premium-muscles',
    savePremiumBtn: '#tr-save-premium-muscles',
    startBtn: '#tr-start',
    liveStartBtn: '#tr-live-start',
    openPlanBtn: '#tr-open-plan',
    nextTitle: '#tr-next-session-title',
    nextType: '#tr-next-type',
    nextMuscles: '#tr-next-muscles',
    nextDuration: '#tr-next-duration',
    nextOpen: '#tr-next-open',
    recs: '#tr-recs',
    modalOverlay: '#tr-modal-overlay',
    modal: '#tr-modal',
    balanceList: '#tr-balance-list'
  };

  const state = {
    today: null,
    plans: [],
    activePlan: null,
    exercisesBank: [],
    currentSession: null,
    ui: {
      planSelectorOpen: false,
      modalOpen: false
    },
    offlineQueueKey: 'nosi_offline_queue_v2'
  };

  function qs(sel, root = document) { return (root || document).querySelector(sel); }
  function qsa(sel, root = document) { return Array.from((root || document).querySelectorAll(sel)); }
  function el(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function nowIso() { return new Date().toISOString(); }
  function clamp(v, a = 0, b = 1) { return Math.max(a, Math.min(b, v)); }
  function safeJSONParse(s, fallback = null) { try { return JSON.parse(s); } catch { return fallback; } }
  function debounce(fn, ms = 300) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
  function formatMinutes(ms) { if (!ms && ms !== 0) return '—'; return String(Math.round(ms / 60000)); }
  function formatTimeAgo(iso) { if (!iso) return '—'; const diff = Date.now() - new Date(iso).getTime(); const mins = Math.round(diff / 60000); if (mins < 1) return 'щойно'; if (mins < 60) return `${mins} хв`; const hrs = Math.round(mins / 60); if (hrs < 24) return `${hrs} год`; const days = Math.round(hrs / 24); return `${days} дн`; }

  const OfflineQueue = (function () {
    const KEY = state.offlineQueueKey;
    function load() { return safeJSONParse(localStorage.getItem(KEY), []); }
    function save(q) { localStorage.setItem(KEY, JSON.stringify(q)); }
    async function flush() {
      const q = load();
      if (!q.length) return;
      const remaining = [];
      for (const item of q) {
        try {
          if (item.type === 'patchSession') {
            await API.patchSession(item.id, item.payload);
          } else if (item.type === 'createSession') {
            await API.createSession(item.payload);
          } else if (item.type === 'post') {
            await API.post(item.path, item.payload);
          }
        } catch (e) {
          remaining.push(item);
        }
      }
      save(remaining);
    }
    function push(item) {
      const q = load();
      q.push(item);
      save(q);
    }
    return { load, save, flush, push };
  })();

  const API = window.API || (function () {
    function headers() {
      const h = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('token');
      if (token) h['Authorization'] = `Bearer ${token}`;
      return h;
    }
    async function handle(res) {
      if (!res.ok) {
        const text = await res.text().catch(() => '');
        const err = new Error(`${res.status} ${res.statusText}`);
        err.body = text;
        throw err;
      }
      return res.status === 204 ? null : res.json().catch(() => null);
    }
    return {
      listPlans() { return fetch(ROUTES.plans, { headers: headers() }).then(handle); },
      getPlan(id) { return fetch(ROUTES.plan(id), { headers: headers() }).then(handle); },
      listExercises() { return fetch(ROUTES.exercises, { headers: headers() }).then(handle); },
      createSession(payload) { return fetch(ROUTES.sessions, { method: 'POST', headers: headers(), body: JSON.stringify(payload) }).then(handle); },
      patchSession(id, payload) { return fetch(ROUTES.session(id), { method: 'PATCH', headers: headers(), body: JSON.stringify(payload) }).then(handle); },
      getSession(id) { return fetch(ROUTES.session(id), { headers: headers() }).then(handle); },
      post(path, payload) { return fetch(path, { method: 'POST', headers: headers(), body: JSON.stringify(payload) }).then(handle); }
    };
  })();

  function renderHeader(today) {
    const titleEl = qs(SELECTORS.headerTitle);
    const typeEl = qs(SELECTORS.headerType);
    const durEl = qs(SELECTORS.headerDuration);
    if (!titleEl || !typeEl || !durEl) return;
    titleEl.textContent = today?.title || 'Сьогодні';
    typeEl.textContent = today?.type || '—';
    durEl.textContent = (today?.duration ? `${today.duration}` : '—') + ' хв';
  }

  function renderRadar() {
    const container = qs(SELECTORS.radar);
    if (!container) return;
    const radarData = state.activePlan?.meta?.radar || state.today?.muscles || {};
    if (window.NosiRadar) {
      NosiRadar.render(container, radarData, { duration: 700 });
    } else {
      container.textContent = 'Радар недоступний';
    }
  }

  function renderLegend() {
    const legend = qs(SELECTORS.legend);
    if (!legend) return;
    legend.innerHTML = '';
    const muscles = state.activePlan?.meta?.muscles || Object.keys(state.today?.muscles || {});
    (muscles || []).forEach((m, i) => {
      const item = el('div', 'tr-legend-item');
      item.dataset.index = i;
      const sw = el('span', `tr-legend-swatch ${i % 3 === 0 ? 'yellow' : i % 3 === 1 ? 'purple' : 'teal'}`);
      const lbl = el('span', 'tr-legend-label');
      lbl.textContent = m;
      item.appendChild(sw);
      item.appendChild(lbl);
      item.addEventListener('click', () => {
        item.classList.toggle('is-muted');
      });
      legend.appendChild(item);
    });
  }

  function renderPlanSelector() {
    const planName = state.activePlan?.name || 'Немає активного плану';
    const el = qs('#tr-session-title');
    if (el) el.setAttribute('data-plan', planName);
  }

  function renderExercisesList(exercises) {
    const list = qs(SELECTORS.exercisesList);
    if (!list) return;
    list.innerHTML = '';
    exercises.forEach((ex, idx) => {
      const li = el('li', 'tr-exercise-row');
      li.dataset.index = idx;
      const left = el('div', 'tr-ex-left');
      left.innerHTML = `<strong class="tr-ex-name">${ex.name}</strong>
                        <div class="tr-ex-meta">${ex.sets?.length || ex.sets || 1} підходи · ${ex.reps || '—'} повт.</div>`;
      const right = el('div', 'tr-ex-right');
      (ex.sets || Array.from({ length: ex.sets || 1 })).forEach((s, si) => {
        const setRow = el('div', 'tr-set-row');
        const weightVal = (s && s.weight != null) ? s.weight : '';
        setRow.innerHTML = `
          <label class="tr-set-label">S${si + 1}</label>
          <input class="tr-set-input tr-input" data-set="${si}" data-ex="${idx}" value="${weightVal}" placeholder="кг" aria-label="Вага підходу ${si + 1}">
          <input class="tr-set-reps tr-input" data-set="${si}" data-ex="${idx}" value="${s && s.reps ? s.reps : ex.reps || ''}" placeholder="повт." aria-label="Повторення підходу ${si + 1}">
          <button class="tr-set-done tr-btn tr-btn--ghost" data-ex="${idx}" data-set="${si}">${s && s.done ? '✓' : 'Готово'}</button>
        `;
        right.appendChild(setRow);
      });
      li.appendChild(left);
      li.appendChild(right);
      list.appendChild(li);
    });

    qsa('.tr-set-input', list).forEach(inp => {
      inp.addEventListener('input', debounce(onExerciseInput, 300));
    });
    qsa('.tr-set-done', list).forEach(btn => {
      btn.addEventListener('click', onExerciseSetDone);
    });
  }

  function renderQuickStats() {
    qs(SELECTORS.weekLoad) && (qs(SELECTORS.weekLoad).textContent = state.activePlan?.meta?.weekly_load || '—');
    qs(SELECTORS.focusMuscles) && (qs(SELECTORS.focusMuscles).textContent = state.activePlan?.meta?.focus || '—');
    qs(SELECTORS.weekSessions) && (qs(SELECTORS.weekSessions).textContent = state.activePlan ? `${state.activePlan.meta?.planned_sessions || 0} · ${state.activePlan.meta?.done_sessions || 0}` : '—');
    qs(SELECTORS.fatigue) && (qs(SELECTORS.fatigue).textContent = state.activePlan?.meta?.fatigue || '—');
  }

  function renderRecommendations() {
    const container = qs(SELECTORS.recs);
    if (!container) return;
    container.innerHTML = '';
    const recs = state.activePlan?.meta?.recommendations || state.today?.recommendations || ['Підтримуйте прогрес: додавайте 2.5% ваги кожні 2 тижні.'];
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
    e.currentTarget.classList.remove('tr-btn--ghost');
    e.currentTarget.classList.add('tr-btn--ghost');
    scheduleSessionAutosave();
    renderSessionProgress();
  }

  function renderSessionProgress() {
    const done = qsa('.tr-set-done[disabled], .tr-set-done:disabled').length || qsa('.tr-set-done').filter(b => b.textContent.trim() === '✓').length;
    const total = qsa('.tr-set-row').length || 0;
    const fill = qs('#tr-progress-fill');
    if (fill) fill.style.width = `${Math.round((done / Math.max(1, total)) * 100)}%`;
    qs('#tr-progress-text') && (qs('#tr-progress-text').textContent = `${done} / ${total}`);
    qs('#tr-overview-sets-done') && (qs('#tr-overview-sets-done').textContent = done);
  }

  function loadLocalSession() {
    const raw = localStorage.getItem('nosi_current_session');
    return safeJSONParse(raw, null);
  }

  function saveLocalSession() {
    if (!state.currentSession) return;
    localStorage.setItem('nosi_current_session', JSON.stringify(state.currentSession));
  }

  const scheduleSessionAutosave = debounce(function () {
    saveLocalSession();
    if (state.currentSession && state.currentSession.id && !String(state.currentSession.id).startsWith('local-')) {
      API.patchSession(state.currentSession.id, { data: state.currentSession.data }).catch(err => {
        OfflineQueue.push({ type: 'patchSession', id: state.currentSession.id, payload: { data: state.currentSession.data } });
      });
    } else {
      OfflineQueue.push({ type: 'patchSession', id: state.currentSession.id || `local-${Date.now()}`, payload: { data: state.currentSession.data } });
    }
  }, 800);

  async function startSessionFlow() {
    if (state.currentSession) {
      return;
    }
    const payload = {
      plan_id: state.activePlan?.id || null,
      title: `Сесія ${new Date().toLocaleString()}`,
      started_at: nowIso()
    };
    try {
      const created = await API.createSession(payload);
      state.currentSession = {
        id: created.id,
        plan_id: created.plan_id,
        title: created.title,
        started_at: created.started_at,
        data: { exercises: buildExercisesFromPlan(state.activePlan) }
      };
      saveLocalSession();
      renderSessionPanel();
      startLiveTimer();
    } catch (err) {
      state.currentSession = {
        id: `local-${Date.now()}`,
        plan_id: state.activePlan?.id || null,
        title: payload.title,
        started_at: payload.started_at,
        data: { exercises: buildExercisesFromPlan(state.activePlan) }
      };
      OfflineQueue.push({ type: 'createSession', payload });
      saveLocalSession();
      renderSessionPanel();
      startLiveTimer();
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

  function renderSessionPanel() {
    if (!state.currentSession) {
      qs(SELECTORS.headerTitle) && (qs(SELECTORS.headerTitle).textContent = 'Немає активної сесії');
      qs(SELECTORS.headerType) && (qs(SELECTORS.headerType).textContent = '—');
      qs(SELECTORS.headerDuration) && (qs(SELECTORS.headerDuration).textContent = '— хв');
      renderExercisesList([]);
      return;
    }
    qs(SELECTORS.headerTitle) && (qs(SELECTORS.headerTitle).textContent = state.currentSession.title || 'Поточна сесія');
    qs(SELECTORS.headerType) && (qs(SELECTORS.headerType).textContent = state.currentSession.type || '—');
    const started = state.currentSession.started_at ? new Date(state.currentSession.started_at).getTime() : null;
    const durationMs = started ? (Date.now() - started) : 0;
    qs(SELECTORS.headerDuration) && (qs(SELECTORS.headerDuration).textContent = `${formatMinutes(durationMs)} хв`);
    renderExercisesList(state.currentSession.data?.exercises || []);
    renderSessionProgress();
  }

  let liveInterval = null;
  function startLiveTimer() {
    if (liveInterval) return;
    liveInterval = setInterval(() => {
      renderSessionPanel();
    }, 5000);
  }
  function stopLiveTimer() {
    if (!liveInterval) return;
    clearInterval(liveInterval);
    liveInterval = null;
  }

  function openModal(html) {
    const overlay = qs(SELECTORS.modalOverlay);
    const modal = qs(SELECTORS.modal);
    if (!overlay || !modal) return;
    overlay.setAttribute('aria-hidden', 'false');
    modal.innerHTML = html;
    state.ui.modalOpen = true;
  }
  function closeModal() {
    const overlay = qs(SELECTORS.modalOverlay);
    const modal = qs(SELECTORS.modal);
    if (!overlay || !modal) return;
    overlay.setAttribute('aria-hidden', 'true');
    modal.innerHTML = '';
    state.ui.modalOpen = false;
  }

  function openPlanQuickEditor() {
    openModal(`
      <h3 style="margin:0 0 8px 0">Редагувати план</h3>
      <label class="cmp-label">Назва</label>
      <input id="tr-modal-plan-name" class="cmp-input" value="${state.activePlan?.name || 'Мій план'}">
      <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
        <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel">Скасувати</button>
        <button class="tr-btn tr-btn--primary" id="tr-modal-save">Зберегти</button>
      </div>
    `);
    qs('#tr-modal-cancel') && qs('#tr-modal-cancel').addEventListener('click', closeModal);
    qs('#tr-modal-save') && qs('#tr-modal-save').addEventListener('click', async () => {
      const name = qs('#tr-modal-plan-name').value.trim() || 'Мій план';
      try {
        await API.post(ROUTES.plan(state.activePlan?.id || ''), { name });
      } catch (e) {
        console.warn('Save plan error', e);
      }
      closeModal();
      await refreshPlans();
      renderPlanPanel();
    });
  }

  function renderBalanceHints() {
    const list = qs(SELECTORS.balanceList);
    if (!list) return;
    list.innerHTML = '';
    const hints = state.activePlan?.meta?.balance_hints || ['Розподіли навантаження між великими групами', 'Зверни увагу на відновлення після важких днів'];
    hints.forEach(h => {
      const li = el('li', 'tr-balance-item');
      li.textContent = h;
      list.appendChild(li);
    });
  }

  function renderNextSessionPreview() {
    qs(SELECTORS.nextTitle) && (qs(SELECTORS.nextTitle).textContent = state.activePlan?.meta?.next_session?.title || '—');
    qs(SELECTORS.nextType) && (qs(SELECTORS.nextType).textContent = state.activePlan?.meta?.next_session?.type || '—');
    qs(SELECTORS.nextMuscles) && (qs(SELECTORS.nextMuscles).textContent = (state.activePlan?.meta?.next_session?.muscles || []).join(', ') || '—');
    qs(SELECTORS.nextDuration) && (qs(SELECTORS.nextDuration).textContent = state.activePlan?.meta?.next_session?.duration ? `${state.activePlan.meta.next_session.duration}` : '—');
  }

  async function refreshPlans() {
    try {
      const plans = await API.listPlans();
      state.plans = plans || [];
      state.activePlan = state.plans[0] || state.activePlan;
    } catch (e) {
      console.warn('Could not load plans', e);
    }
  }

  async function loadInitialData() {
    try {
      const plans = await API.listPlans();
      state.plans = plans || [];
      state.activePlan = state.plans[0] || null;
    } catch (e) {
      state.plans = [];
      state.activePlan = null;
    }
    try {
      const exercises = await API.listExercises();
      state.exercisesBank = exercises || [];
    } catch (e) {
      state.exercisesBank = [];
    }
    try {
      const res = await fetch(ROUTES.today, { headers: { 'Content-Type': 'application/json' } });
      if (res.ok) state.today = await res.json();
    } catch (e) {
      state.today = null;
    }
  }

  function attachUI() {
    const startBtn = qs(SELECTORS.startBtn);
    const liveStart = qs(SELECTORS.liveStartBtn);
    const openPlan = qs(SELECTORS.openPlanBtn);
    const savePremium = qs(SELECTORS.savePremiumBtn);
    const nextOpen = qs(SELECTORS.nextOpen);

    if (startBtn) startBtn.addEventListener('click', startSessionFlow);
    if (liveStart) liveStart.addEventListener('click', startSessionFlow);
    if (openPlan) openPlan.addEventListener('click', () => {
      if (state.activePlan) window.location.href = `/training/plans/${state.activePlan.id}`;
      else alert('У вас немає активного плану');
    });
    if (savePremium) savePremium.addEventListener('click', onSavePremium);
    if (nextOpen) nextOpen.addEventListener('click', () => window.location.href = '/training/sessions/next');

    const editPlanBtn = qs('#tr-edit-plan');
    if (editPlanBtn) editPlanBtn.addEventListener('click', openPlanQuickEditor);

    const overlay = qs(SELECTORS.modalOverlay);
    if (overlay) overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        if (state.currentSession) scheduleSessionAutosave();
      }
      if (e.key === 'Escape' && state.ui.modalOpen) {
        closeModal();
      }
    });

    window.addEventListener('online', () => {
      OfflineQueue.flush().catch(err => console.warn('Flush failed', err));
    });
  }

  async function onSavePremium() {
    const selected = qsa('.tr-muscle-btn.is-selected', qs(SELECTORS.premiumMuscles)).map(b => b.dataset.muscle);
    try {
      await API.post(ROUTES.preferences, { key: 'premium_muscles', value: JSON.stringify(selected) });
      alert('Цільові м’язи збережено');
    } catch (e) {
      OfflineQueue.push({ type: 'post', path: ROUTES.preferences, payload: { key: 'premium_muscles', value: JSON.stringify(selected) } });
      alert('Збереження в чергу (offline)');
    }
  }

  async function init() {
    attachUI();
    await loadInitialData();
    const saved = loadLocalSession();
    if (saved) state.currentSession = saved;
    renderHeader(state.today);
    renderRadar();
    renderLegend();
    renderPlanSelector();
    renderQuickStats();
    renderPlanPanel();
    renderSessionPanel();
    renderBalanceHints();
    renderNextSessionPreview();
    renderRecommendations();
    OfflineQueue.flush().catch(() => {});
  }

  function renderPlanPanel() {
    renderPlanSelector();
    renderRadar();
    renderLegend();
    renderBalanceHints();
  }

  window.TrainingMain = {
    state,
    init,
    refreshPlans,
    renderRadar,
    renderSessionPanel,
    startSessionFlow,
    OfflineQueue,
    buildExercisesFromPlan
  };

  document.addEventListener('DOMContentLoaded', init);
})();
