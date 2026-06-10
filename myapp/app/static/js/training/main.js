(function () {
  'use strict';

  const state = {
    todayRaw: null,          // payload from /api/training/today
    exercisesBank: [],
    currentSession: null,    // normalized session object for UI
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

  function renderRadar() {
    const container = qs('#tr-radar');
    if (!container) return;
    const radarData = state.currentSession?.muscles || {};
    if (window.NosiRadar) NosiRadar.render(container, radarData, { duration: 700 });
    else container.textContent = Object.keys(radarData).length ? JSON.stringify(radarData) : 'Радар недоступний';
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

  function onExerciseInput(e) {
  }

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
      reps: ex.reps || (ex.meta && ex.meta.reps) || ex.default_reps || '—',
      sets: ex.sets || (ex.meta && ex.meta.exercises) || [],
      raw: ex
    };
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
      const exercises = await API.listExercises();
      state.exercisesBank = Array.isArray(exercises) ? exercises : [];
    } catch (e) {
      state.exercisesBank = [];
    }

    renderAll();
  }

  function renderAll() {
    renderHeader();
    renderRadar();
    renderSessionPanel();
    renderQuickStats();
  }

  function init() {
    document.addEventListener('DOMContentLoaded', () => {
      loadInitialData();

      const searchForm = qs('#tr-ex-search-form');
      if (searchForm) {
        searchForm.addEventListener('submit', async (ev) => {
          ev.preventDefault();
          const q = qs('#tr-ex-search-input')?.value || '';
          try {
            const res = await API.listExercises({ q });
            renderExercisesList(res || []);
          } catch (err) {
            openToast('Помилка пошуку вправ', 'error');
          }
        });
      }
    });
  }

  window.TrainingUI = { state, loadInitialData, renderAll };

  init();
})();
