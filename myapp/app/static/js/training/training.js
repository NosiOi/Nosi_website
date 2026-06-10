(function () {
  const D = {
    startBtn: document.getElementById('tr-start'),
    editPlanBtn: document.getElementById('tr-edit-plan'),
    weekLoad: document.getElementById('tr-week-load'),
    focusMuscles: document.getElementById('tr-focus-muscles'),
    weekSessions: document.getElementById('tr-week-sessions'),
    fatigue: document.getElementById('tr-fatigue'),
    radar: document.getElementById('tr-radar'),
    legend: document.getElementById('tr-legend'),
    premiumMuscles: document.getElementById('tr-premium-muscles'),
    savePremiumBtn: document.getElementById('tr-save-premium-muscles'),
    balanceList: document.getElementById('tr-balance-list'),
    sessionTitle: document.getElementById('tr-session-title'),
    sessionType: document.getElementById('tr-session-type'),
    sessionDuration: document.getElementById('tr-session-duration'),
    exercisesList: document.getElementById('tr-exercises'),
    liveStartBtn: document.getElementById('tr-live-start'),
    openPlanBtn: document.getElementById('tr-open-plan'),
    nextTitle: document.getElementById('tr-next-session-title'),
    nextType: document.getElementById('tr-next-type'),
    nextMuscles: document.getElementById('tr-next-muscles'),
    nextDuration: document.getElementById('tr-next-duration'),
    nextOpen: document.getElementById('tr-next-open'),
    recs: document.getElementById('tr-recs')
  };

  const state = {
    plans: [],
    activePlan: null,
    currentSession: null,
    exercisesBank: []
  };

  function el(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function qAll(sel, ctx = document) { return Array.from((ctx || document).querySelectorAll(sel)); }
  function debounce(fn, ms = 400) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
  function formatMinutes(ms) { if (!ms) return '—'; return String(Math.round(ms / 60000)); }

  async function loadInitial() {
    const plans = await API.safe(() => API.listPlans());
    state.plans = plans || [];
    state.activePlan = state.plans[0] || null;
    const exercises = await API.safe(() => API.listExercises());
    state.exercisesBank = exercises || [];
  }

  function renderHeader() {
    D.weekLoad.textContent = state.activePlan?.meta?.weekly_load || '—';
    D.focusMuscles.textContent = state.activePlan?.meta?.focus || '—';
    D.weekSessions.textContent = state.activePlan ? `${state.activePlan.meta?.planned_sessions || 0} · ${state.activePlan.meta?.done_sessions || 0}` : '—';
    D.fatigue.textContent = state.activePlan?.meta?.fatigue || '—';
  }

  function renderPlanPanel() {
    D.legend.innerHTML = '';
    const muscles = state.activePlan?.meta?.muscles || [];
    muscles.forEach(m => {
      const item = el('div', 'tr-legend-item');
      item.textContent = m;
      D.legend.appendChild(item);
    });

    D.premiumMuscles.innerHTML = '';
    const all = state.activePlan?.meta?.all_muscles || ['Груди', 'Спина', 'Ноги', 'Плечі', 'Руки', 'Кор'];
    all.forEach(name => {
      const btn = el('button', 'tr-muscle-btn');
      btn.type = 'button';
      btn.textContent = name;
      btn.dataset.muscle = name;
      btn.addEventListener('click', () => btn.classList.toggle('is-selected'));
      D.premiumMuscles.appendChild(btn);
    });

    if (D.radar) {
      const radarData = state.activePlan?.meta?.radar || {};
      NosiRadar.render(D.radar, radarData, { duration: 700 });
    }
  }

  function buildExercisesFromPlan(plan) {
    const day = plan?.meta?.days?.[0] || { exercises: [] };
    return (day.exercises || []).map(ex => ({
      exercise_id: ex.exercise_id || null,
      name: ex.name || 'Вправа',
      reps: ex.reps || null,
      sets: (ex.sets || [{ target: null }]).map(s => ({ weight: s.target || null, done: false }))
    }));
  }

  function renderSessionPanel() {
    if (!state.currentSession) {
      D.sessionTitle.textContent = 'Немає активної сесії';
      D.sessionType.textContent = '—';
      D.sessionDuration.textContent = '— хв';
      D.exercisesList.innerHTML = '';
      return;
    }

    D.sessionTitle.textContent = state.currentSession.title || 'Поточна сесія';
    D.sessionType.textContent = state.currentSession.type || '—';
    const started = state.currentSession.started_at ? new Date(state.currentSession.started_at).getTime() : null;
    const durationMs = started ? (Date.now() - started) : 0;
    D.sessionDuration.textContent = `${formatMinutes(durationMs)} хв`;

    D.exercisesList.innerHTML = '';
    const exercises = state.currentSession.data?.exercises || [];
    exercises.forEach((ex, idx) => {
      const li = el('li', 'tr-exercise-row');
      li.setAttribute('data-index', idx);

      const left = el('div', 'tr-ex-left');
      left.innerHTML = `<strong class="tr-ex-name">${ex.name}</strong>
                        <div class="tr-ex-meta">${ex.sets.length} підходи · ${ex.reps || '—'} повт.</div>`;

      const right = el('div', 'tr-ex-right');
      ex.sets.forEach((s, si) => {
        const setRow = el('div', 'tr-set-row');
        setRow.innerHTML = `
          <label class="tr-set-label">S${si + 1}</label>
          <input class="tr-set-input tr-input" data-set="${si}" data-ex="${idx}" value="${s.weight ?? ''}" placeholder="кг">
          <button class="tr-set-done tr-btn ${s.done ? 'tr-btn--ghost' : 'tr-btn--primary'}" data-ex="${idx}" data-set="${si}">${s.done ? '✓' : 'Готово'}</button>
        `;
        right.appendChild(setRow);
      });

      li.appendChild(left);
      li.appendChild(right);
      D.exercisesList.appendChild(li);
    });

    qAll('.tr-set-input', D.exercisesList).forEach(inp => {
      inp.addEventListener('input', debounce(onSetInputChange, 300));
    });
    qAll('.tr-set-done', D.exercisesList).forEach(btn => {
      btn.addEventListener('click', onSetDoneClick);
    });
  }

  function onSetInputChange(e) {
    const exIdx = Number(e.target.dataset.ex);
    const setIdx = Number(e.target.dataset.set);
    const val = e.target.value.trim();
    if (!state.currentSession) return;
    state.currentSession.data.exercises[exIdx].sets[setIdx].weight = val ? Number(val) : null;
    scheduleAutosave();
  }

  function onSetDoneClick(e) {
    const exIdx = Number(e.currentTarget.dataset.ex);
    const setIdx = Number(e.currentTarget.dataset.set);
    const setObj = state.currentSession.data.exercises[exIdx].sets[setIdx];
    setObj.done = true;
    renderSessionPanel();
    scheduleAutosave();
  }

  function saveLocalSession() {
    if (!state.currentSession) return;
    localStorage.setItem('nosi_current_session', JSON.stringify(state.currentSession));
    debouncedPatch();
  }

  function loadLocalSession() {
    const raw = localStorage.getItem('nosi_current_session');
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  const debouncedPatch = debounce(async function () {
    if (!state.currentSession || !state.currentSession.id) return;
    try {
      await API.patchSession(state.currentSession.id, { data: state.currentSession.data });
    } catch (err) {
      console.warn('Помилка синхронізації', err);
      OfflineQueue.push({ type: 'patchSession', id: state.currentSession.id, payload: { data: state.currentSession.data } });
    }
  }, 1000);

  const OfflineQueue = (function () {
    const KEY = 'nosi_offline_queue_v1';
    function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; } }
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
          } else {
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
    return { flush, push, load, save, pushItem: push };
  })();

  async function startSession() {
    if (state.currentSession) {
      startLiveTimer();
      return;
    }
    try {
      const payload = {
        plan_id: state.activePlan?.id || null,
        title: `Сесія ${new Date().toLocaleString()}`,
        started_at: new Date().toISOString()
      };
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
      console.warn('Старт сесії помилка', err);
      OfflineQueue.pushItem({ type: 'createSession', payload });
      state.currentSession = {
        id: `local-${Date.now()}`,
        plan_id: state.activePlan?.id || null,
        title: payload.title,
        started_at: payload.started_at,
        data: { exercises: buildExercisesFromPlan(state.activePlan) }
      };
      saveLocalSession();
      renderSessionPanel();
      startLiveTimer();
    }
  }

  let liveInterval = null;
  function startLiveTimer() {
    if (liveInterval) return;
    liveInterval = setInterval(() => renderSessionPanel(), 5000);
  }
  function stopLiveTimer() {
    if (!liveInterval) return;
    clearInterval(liveInterval);
    liveInterval = null;
  }

  function attachHandlers() {
    if (D.startBtn) D.startBtn.addEventListener('click', startSession);
    if (D.liveStartBtn) D.liveStartBtn.addEventListener('click', startSession);
    if (D.openPlanBtn) D.openPlanBtn.addEventListener('click', () => {
      if (state.activePlan) window.location.href = `/training/plans/${state.activePlan.id}`;
      else alert('У вас немає активного плану');
    });
    if (D.savePremiumBtn) D.savePremiumBtn.addEventListener('click', onSavePremium);
    if (D.editPlanBtn) D.editPlanBtn.addEventListener('click', () => window.location.href = '/training/plans');
    if (D.nextOpen) D.nextOpen.addEventListener('click', () => window.location.href = '/training/sessions/next');

    window.addEventListener('online', () => {
      OfflineQueue.flush().catch(e => console.warn('Flush error', e));
    });
  }

  function onSavePremium() {
    const selected = qAll('.tr-muscle-btn.is-selected', D.premiumMuscles).map(b => b.dataset.muscle);
    API.post('/api/user/preferences', { key: 'premium_muscles', value: JSON.stringify(selected) }).catch(() => {
      OfflineQueue.pushItem({ path: '/api/user/preferences', payload: { key: 'premium_muscles', value: JSON.stringify(selected) } });
    });
    alert('Цільові м’язи збережено');
  }

  async function init() {
    attachHandlers();
    await loadInitial();
    const saved = loadLocalSession();
    if (saved) state.currentSession = saved;
    renderHeader();
    renderPlanPanel();
    renderSessionPanel();
    renderNext();
    renderRecs();
    OfflineQueue.flush().catch(() => {});
  }

  function renderNext() {
    D.nextTitle.textContent = 'Завтра: Силова сесія';
    D.nextType.textContent = 'Сила';
    D.nextMuscles.textContent = 'Груди, Трицепс';
    D.nextDuration.textContent = '60';
  }

  function renderRecs() {
    D.recs.innerHTML = '<div class="tr-rec">Підтримуйте прогрес: додавайте 2.5% ваги кожні 2 тижні.</div>';
  }

  document.addEventListener('DOMContentLoaded', init);
  window.NosiTraining = { state, startSession, saveLocalSession, OfflineQueue };
})();
