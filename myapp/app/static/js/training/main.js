(function () {
  'use strict';

  const state = {
    todayRaw: null,
    exercisesBank: [],
    currentSession: null,
    ui: { modalOpen: false }
  };

  function qs(sel, root = document) { return (root || document).querySelector(sel); }
  function qsa(sel, root = document) { return Array.from((root || document).querySelectorAll(sel)); }
  function el(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function debounce(fn, ms = 300) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
  function openToast(text, type = 'info', timeout = 2400) {
    const container = qs('#tr-toast-container');
    if (!container) return;
    const t = el('div', 'tr-toast');
    if (type === 'success') t.classList.add('success');
    if (type === 'warn') t.classList.add('warn');
    if (type === 'error') t.classList.add('error');
    t.textContent = text;
    container.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, timeout);
  }

  function renderHeader() {
    const titleEl = qs('#tr-session-title');
    const typeEl = qs('#tr-session-type');
    const durEl = qs('#tr-session-duration');
    const title = state.currentSession?.title || 'Тренування';
    const type = state.currentSession?.type || '—';
    const dur = state.currentSession?.duration ? `${state.currentSession.duration} хв` : '—';
    if (titleEl) titleEl.textContent = title;
    if (typeEl) typeEl.textContent = type;
    if (durEl) durEl.textContent = dur;
  }

  function renderExercisesList(exercises = []) {
    const list = qs('#tr-exercises');
    if (!list) return;
    list.innerHTML = '';
    exercises.forEach((ex, idx) => {
      const li = el('li', 'tr-exercise-row');
      li.dataset.index = idx;
      const left = el('div', 'tr-ex-left');
      const name = ex.name || ex.title || 'Без назви';
      const reps = ex.reps || ex.default_reps || '—';
      const setsCount = (ex.sets && ex.sets.length) || ex.sets || 1;
      left.innerHTML = `<strong class="tr-ex-name">${name}</strong><div class="tr-ex-meta">${setsCount} підходи · ${reps} повт.</div>`;
      const right = el('div', 'tr-ex-right');

      const sets = ex.sets || Array.from({ length: setsCount }).map(() => ({ weight: '', reps }));
      sets.forEach((s, si) => {
        const setRow = el('div', 'tr-set-row');
        const weightVal = (s && s.weight != null) ? s.weight : '';
        setRow.innerHTML = `<label class="tr-set-label">S${si + 1}</label>
          <input class="tr-set-input tr-input" data-set="${si}" data-ex="${idx}" value="${weightVal}" placeholder="кг" aria-label="Вага підходу ${si + 1}">
          <input class="tr-set-reps tr-input" data-set="${si}" data-ex="${idx}" value="${s && s.reps ? s.reps : reps}" placeholder="повт." aria-label="Повторення підходу ${si + 1}">
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

  function attachExerciseHandlers() {
    qsa('.tr-set-done').forEach(btn => {
      btn.removeEventListener('click', onSetDone);
      btn.addEventListener('click', onSetDone);
    });
  }

  function onSetDone(e) {
    const exIdx = Number(e.currentTarget.dataset.ex);
    const setIdx = Number(e.currentTarget.dataset.set);
    openToast(`Позначено підхід ${setIdx + 1} вправи ${exIdx + 1}`, 'success', 1200);
  }

  function onExerciseInput(e) {}

  function normalizeTrainingToday(payload) {
    if (!payload) return null;
    const exercises = Array.isArray(payload.exercises) ? payload.exercises.map(normalizeExerciseFromBackend) : [];
    let meta = {};
    try {
      if (payload.meta && typeof payload.meta === 'string') meta = JSON.parse(payload.meta);
      else if (payload.meta && typeof payload.meta === 'object') meta = payload.meta;
      else if (payload.plan && Array.isArray(payload.plan) && payload.plan[0] && payload.plan[0].meta) {
        meta = typeof payload.plan[0].meta === 'string' ? JSON.parse(payload.plan[0].meta || '{}') : (payload.plan[0].meta || {});
      }
    } catch (e) { meta = {}; }

    return {
      sessionId: payload.sessionId || null,
      title: payload.title || (payload.plan && payload.plan[0] && payload.plan[0].name) || 'Сесія',
      exercises,
      muscles: payload.muscles || {},
      meta
    };
  }

  function normalizeExerciseFromBackend(ex) {
    return {
      id: ex.id || ex.exercise_id || null,
      name: ex.name || ex.title || 'Без назви',
      reps: ex.reps || ex.default_reps || '—',
      sets: ex.sets || (ex.meta && ex.meta.exercises) || [],
      raw: ex
    };
  }

  function normalizeSessionFromBackend(s) {
    if (!s) return null;
    let dataObj = {};
    try { dataObj = s.data ? JSON.parse(s.data) : {}; } catch (e) { dataObj = {}; }
    return {
      id: s.id,
      title: s.title || 'Сесія',
      plan_id: s.plan_id || null,
      started_at: s.started_at || null,
      finished_at: s.finished_at || null,
      data: dataObj,
      exercises: dataObj.exercises || []
    };
  }

  async function onCreateSessionNow(title = 'Нова сесія') {
    try {
      const payload = { title, data: JSON.stringify({ exercises: [] }) };
      const session = await API.createSession(payload);
      state.currentSession = normalizeSessionFromBackend(session);
      renderAll();
      openToast('Сесія запущена', 'success');
    } catch (err) {
      console.error(err);
      openToast('Не вдалося запустити сесію', 'error');
    }
  }

  async function onStartSessionFromPlan(planId) {
    try {
      const session = await API.startSessionFromPlan(planId);
      state.currentSession = normalizeSessionFromBackend(session);
      renderAll();
      openToast('Сесія з плану запущена', 'success');
    } catch (err) {
      console.error(err);
      openToast('Не вдалося запустити сесію з плану', 'error');
    }
  }

  async function onAddExerciseToSession(exerciseId, sets = 3, reps = '8') {
    if (!state.currentSession || !state.currentSession.id) {
      openToast('Спочатку створіть або виберіть сесію', 'warn');
      return;
    }
    try {
      const payload = { exercise_id: exerciseId, sets, reps };
      const res = await API.addExerciseToSession(state.currentSession.id, payload);
      state.currentSession = normalizeSessionFromBackend(res);
      renderAll();
      openToast('Вправа додана до сесії', 'success');
    } catch (err) {
      console.error(err);
      openToast('Не вдалося додати вправу', 'error');
    }
  }

  async function onSaveSessionProgress() {
    if (!state.currentSession || !state.currentSession.id) {
      openToast('Немає активної сесії для збереження', 'warn');
      return;
    }
    try {
      const payload = { data: JSON.stringify(state.currentSession.data || {}) };
      const res = await API.updateSessionData(state.currentSession.id, payload);
      state.currentSession = normalizeSessionFromBackend(res);
      openToast('Прогрес збережено', 'success');
    } catch (err) {
      console.error(err);
      openToast('Не вдалося зберегти прогрес', 'error');
    }
  }

  async function onFinishSession() {
    if (!state.currentSession || !state.currentSession.id) {
      openToast('Немає активної сесії', 'warn');
      return;
    }
    try {
      const res = await API.finishSession(state.currentSession.id);
      state.currentSession = normalizeSessionFromBackend(res);
      renderAll();
      openToast('Сесію завершено', 'success');
    } catch (err) {
      console.error(err);
      openToast('Не вдалося завершити сесію', 'error');
    }
  }

  function onSelectPlan(plan) {
    if (!plan) return;
    state.currentSession = state.currentSession || { id: null, data: { exercises: [] } };
    state.currentSession.title = plan.name || `План ${plan.id}`;
    renderAll();
  }

  async function loadInitialData() {
    try {
      const today = await API.getTrainingToday();
      state.todayRaw = today || null;
      state.currentSession = normalizeTrainingToday(state.todayRaw);
    } catch (err) {
      console.error('API safe error', err);
      openToast('Не вдалося завантажити сьогоднішню сесію', 'error');
      state.todayRaw = null;
      state.currentSession = null;
    }

    try {
      const res = await API.listExercises({ per_page: 100 });
      state.exercisesBank = Array.isArray(res.items) ? res.items : [];
    } catch (e) {
      state.exercisesBank = [];
      console.error('Не вдалося завантажити вправи', e);
    }

    renderAll();
  }

  async function initBuilder() {
    const muscleSelect = qs('#tr-builder-muscle');
    const locationSelect = qs('#tr-builder-location');
    const exerciseSelect = qs('#tr-builder-exercise');
    const addBtn = qs('#tr-builder-add');

    let allExercises = [];
    try {
      const res = await API.listExercises({ per_page: 500 });
      allExercises = res.items || [];
    } catch (e) {
      console.error("Не вдалося завантажити вправи", e);
      return;
    }

    const muscles = new Set();
    allExercises.forEach(ex => {
      (ex.muscles || []).forEach(m => muscles.add(m.slug));
    });

    muscles.forEach(slug => {
      const opt = document.createElement('option');
      opt.value = slug;
      opt.textContent = slug;
      muscleSelect.appendChild(opt);
    });

    function updateExerciseList() {
      const selectedMuscle = muscleSelect.value;
      exerciseSelect.innerHTML = '<option value="">Оберіть вправу</option>';

      const filtered = allExercises.filter(ex => {
        const matchMuscle = selectedMuscle ? (ex.muscles || []).some(m => m.slug === selectedMuscle) : true;
        return matchMuscle;
      });

      filtered.forEach(ex => {
        const opt = document.createElement('option');
        opt.value = ex.id;
        opt.textContent = ex.name;
        exerciseSelect.appendChild(opt);
      });
    }

    muscleSelect.addEventListener('change', updateExerciseList);
    locationSelect.addEventListener('change', updateExerciseList);

    addBtn.addEventListener('click', () => {
      const exId = exerciseSelect.value;
      const sets = Number(qs('#tr-builder-sets').value);
      const reps = Number(qs('#tr-builder-reps').value);

      if (!exId) {
        openToast("Оберіть вправу", "warn");
        return;
      }

      TrainingUI.onAddExerciseToSession(Number(exId), sets, reps);
    });

    updateExerciseList();
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
    renderExercisesList(state.currentSession.exercises || []);
  }

  function renderQuickStats() {
    qs('#tr-week-load') && (qs('#tr-week-load').textContent = state.currentSession?.meta?.weekly_load || '—');
    qs('#tr-focus-muscles') && (qs('#tr-focus-muscles').textContent = state.currentSession?.meta?.focus || '—');
    qs('#tr-week-sessions') && (qs('#tr-week-sessions').textContent = state.currentSession?.meta ? `${state.currentSession.meta.planned_sessions||0} · ${state.currentSession.meta.done_sessions||0}` : '—');
    qs('#tr-fatigue') && (qs('#tr-fatigue').textContent = state.currentSession?.meta?.fatigue || '—');
  }

  function renderAll() {
    renderHeader();
    renderSessionPanel();
    renderQuickStats();
  }

  function init() {
    document.addEventListener('DOMContentLoaded', () => {
      loadInitialData();
      initBuilder();

      const searchForm = qs('#tr-ex-search-form');
      if (searchForm) {
        searchForm.addEventListener('submit', async (ev) => {
          ev.preventDefault();
          const q = qs('#tr-ex-search-input')?.value || '';
          try {
            const res = await API.listExercises({ q });
            renderExercisesList(res.items || []);
          } catch (err) {
            openToast('Помилка пошуку вправ', 'error');
          }
        });
      }

      qs('#btn-start-now')?.addEventListener('click', () => onCreateSessionNow());
      qs('#btn-save-progress')?.addEventListener('click', () => onSaveSessionProgress());
      qs('#btn-finish-session')?.addEventListener('click', () => onFinishSession());

      document.addEventListener('click', function (ev) {
        const btn = ev.target.closest('[data-action]');
        if (!btn) return;

        const action = btn.dataset.action;
        switch (action) {
          case 'start-now':
            TrainingUI.onCreateSessionNow && TrainingUI.onCreateSessionNow();
            break;
          case 'save-progress':
            TrainingUI.onSaveSessionProgress && TrainingUI.onSaveSessionProgress();
            break;
          case 'finish-session':
            TrainingUI.onFinishSession && TrainingUI.onFinishSession();
            break;
          case 'add-exercise':
            {
              const exId = btn.dataset.exerciseId;
              if (!exId) { openToast('Не вказано id вправи', 'warn'); break; }
              TrainingUI.onAddExerciseToSession && TrainingUI.onAddExerciseToSession(Number(exId));
            }
            break;
          case 'start-plan':
            {
              const planId = btn.dataset.planId;
              if (!planId) { openToast('Не вказано id плану', 'warn'); break; }
              TrainingUI.onStartSessionFromPlan && TrainingUI.onStartSessionFromPlan(Number(planId));
            }
            break;
        }
      });
    });
  }

  window.TrainingUI = {
    state,
    loadInitialData,
    renderAll,
    onAddExerciseToSession,
    onStartSessionFromPlan,
    onCreateSessionNow,
    onSaveSessionProgress,
    onFinishSession,
    onSelectPlan,
    debugCheck: function () {
      console.log('currentSession', state.currentSession);
      console.log('exercisesBank length', state.exercisesBank.length);
      console.log('DOM buttons:',
        { start: !!document.querySelector('#btn-start-now'), save: !!document.querySelector('#btn-save-progress'), finish: !!document.querySelector('#btn-finish-session') }
      );
    }
  };

  init();
})();
