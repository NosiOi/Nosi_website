(() => {
  const els = {
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
    todayDay: null,
    currentSession: null, 
    autosaveTimer: null
  };

  function q(sel, ctx = document) { return ctx.querySelector(sel); }
  function qAll(sel, ctx = document) { return Array.from(ctx.querySelectorAll(sel)); }
  function el(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }

  function formatDurationMinutes(ms) {
    if (!ms) return '—';
    const mins = Math.round(ms / 60000);
    return `${mins}`;
  }

  function debounce(fn, wait = 500) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), wait);
    };
  }

  function renderHeaderStats() {
    // тимчасові значення — замінити на реальні з state або API
    els.weekLoad.textContent = state.activePlan ? 'Середній' : '—';
    els.focusMuscles.textContent = state.activePlan?.meta?.focus || '—';
    els.weekSessions.textContent = '0 · 0';
    els.fatigue.textContent = 'Нормальний';
  }

  function renderPlanPanel() {
    els.legend.innerHTML = '';
    const muscles = state.activePlan?.meta?.muscles || [];
    muscles.forEach(m => {
      const item = el('div', 'tr-legend-item');
      item.textContent = m;
      els.legend.appendChild(item);
    });

    els.premiumMuscles.innerHTML = '';
    const allMuscles = ['Груди','Спина','Ноги','Плечі','Руки','Прес']; // fallback
    allMuscles.forEach(name => {
      const btn = el('button', 'tr-muscle-btn');
      btn.type = 'button';
      btn.textContent = name;
      btn.dataset.muscle = name;
      btn.addEventListener('click', () => btn.classList.toggle('is-selected'));
      els.premiumMuscles.appendChild(btn);
    });
  }

  function renderSessionPanel() {
    if (!state.currentSession) {
      els.sessionTitle.textContent = 'Немає активної сесії';
      els.sessionType.textContent = '—';
      els.sessionDuration.textContent = '— хв';
      els.exercisesList.innerHTML = '';
      return;
    }

    els.sessionTitle.textContent = state.currentSession.title || 'Поточна сесія';
    els.sessionType.textContent = state.currentSession.type || '—';
    const durationMs = state.currentSession.started_at ? (Date.now() - new Date(state.currentSession.started_at).getTime()) : 0;
    els.sessionDuration.textContent = `${formatDurationMinutes(durationMs)} хв`;

    // exercisesч
    const exercises = state.currentSession.data?.exercises || [];
    els.exercisesList.innerHTML = '';
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
          <label class="tr-set-label">S${si+1}</label>
          <input class="tr-set-input tr-input" data-set="${si}" data-ex="${idx}" value="${s.weight || ''}" placeholder="кг">
          <button class="tr-set-done tr-btn tr-btn--ghost" data-ex="${idx}" data-set="${si}">✓</button>
        `;
        right.appendChild(setRow);
      });

      li.appendChild(left);
      li.appendChild(right);
      els.exercisesList.appendChild(li);
    });

    qAll('.tr-set-input', els.exercisesList).forEach(inp => {
      inp.addEventListener('input', debounce(onSetInputChange, 400));
    });
    qAll('.tr-set-done', els.exercisesList).forEach(btn => {
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

  async function onStartSessionClick() {
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
      saveSessionToLocal();
      renderSessionPanel();
      startLiveTimer();
    } catch (err) {
      console.error('Create session error', err);
      alert('Не вдалося створити сесію. Спробуйте пізніше.');
    }
  }

  function buildExercisesFromPlan(plan) {
    const day = plan?.meta?.days?.[0] || { exercises: [] };
    return (day.exercises || []).map(ex => ({
      exercise_id: ex.exercise_id || null,
      name: ex.name || 'Вправа',
      reps: ex.reps || null,
      sets: (ex.sets || [{ weight: null }]).map(s => ({ weight: s.target || null, done: false }))
    }));
  }

  let liveInterval = null;
  function startLiveTimer() {
    if (liveInterval) return;
    liveInterval = setInterval(() => {
      renderSessionPanel();
    }, 1000 * 10);
  }
  function stopLiveTimer() {
    if (!liveInterval) return;
    clearInterval(liveInterval);
    liveInterval = null;
  }

  // Autosave
  function saveSessionToLocal() {
    if (!state.currentSession) return;
    localStorage.setItem('nosi_current_session', JSON.stringify(state.currentSession));
    debouncedPatchSession();
  }

  function loadSessionFromLocal() {
    const raw = localStorage.getItem('nosi_current_session');
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  const debouncedPatchSession = debounce(async function () {
    if (!state.currentSession || !state.currentSession.id) return;
    try {
      await API.patchSession(state.currentSession.id, { data: state.currentSession.data });
    } catch (err) {
      console.warn('Patch session failed', err);
    }
  }, 1000);

  function scheduleAutosave() {
    if (state.autosaveTimer) clearTimeout(state.autosaveTimer);
    state.autosaveTimer = setTimeout(() => {
      saveSessionToLocal();
    }, 800);
  }

  async function init() {
    attachUIHandlers();
    try {
      const plans = await API.listPlans();
      state.plans = plans || [];
      state.activePlan = state.plans[0] || null;
    } catch (err) {
      console.warn('Could not load plans', err);
      state.plans = [];
      state.activePlan = null;
    }

    const saved = loadSessionFromLocal();
    if (saved) {
      state.currentSession = saved;
    }

    renderHeaderStats();
    renderPlanPanel();
    renderSessionPanel();
    renderNextSession();
    renderRecs();
  }

  function renderNextSession() {
    els.nextTitle.textContent = 'Завтра: Силова сесія';
    els.nextType.textContent = 'Сила';
    els.nextMuscles.textContent = 'Груди, Трицепс';
    els.nextDuration.textContent = '60';
  }

  function renderRecs() {
    els.recs.innerHTML = '<div class="tr-rec">Підтримуйте прогрес: додайте 2.5% ваги кожні 2 тижні.</div>';
  }

  function attachUIHandlers() {
    if (els.startBtn) els.startBtn.addEventListener('click', onStartSessionClick);
    if (els.liveStartBtn) els.liveStartBtn.addEventListener('click', onStartSessionClick);
    if (els.openPlanBtn) els.openPlanBtn.addEventListener('click', () => {
      // відкриваємо план — редірект на сторінку плану
      if (state.activePlan) {
        window.location.href = `/training/plans/${state.activePlan.id}`;
      } else {
        alert('У вас немає активного плану');
      }
    });
    if (els.savePremiumBtn) els.savePremiumBtn.addEventListener('click', onSavePremiumMuscles);
    if (els.editPlanBtn) els.editPlanBtn.addEventListener('click', () => {
      window.location.href = '/training/plans';
    });
    if (els.nextOpen) els.nextOpen.addEventListener('click', () => {
      window.location.href = '/training/sessions/next';
    });

    qAll('.tr-help').forEach(btn => {
      btn.addEventListener('mouseenter', (e) => {
        const tip = e.currentTarget.dataset.tooltip;
        if (!tip) return;
        const t = el('div', 'tr-tooltip');
        t.textContent = tip;
        t.style.position = 'absolute';
        t.style.zIndex = 9999;
        document.body.appendChild(t);
        const rect = e.currentTarget.getBoundingClientRect();
        t.style.left = `${rect.right + 8}px`;
        t.style.top = `${rect.top}px`;
        e.currentTarget._tooltipEl = t;
      });
      btn.addEventListener('mouseleave', (e) => {
        const t = e.currentTarget._tooltipEl;
        if (t) t.remove();
        e.currentTarget._tooltipEl = null;
      });
    });
  }

  function onSavePremiumMuscles() {
    const selected = qAll('.tr-muscle-btn.is-selected', els.premiumMuscles).map(b => b.dataset.muscle);
    console.log('Save premium muscles', selected);
    alert('Цільові м’язи збережено');
  }

  // --- Start
  document.addEventListener('DOMContentLoaded', init);
})();
