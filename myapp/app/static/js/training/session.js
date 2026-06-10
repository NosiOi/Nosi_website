(function () {
  function qs(s, r = document) { return (r || document).querySelector(s); }
  function qsa(s, r = document) { return Array.from((r || document).querySelectorAll(s)); }

  let sessionData = null;
  let currentIndex = 0;
  let restTimer = null;
  let restRemaining = 0;
  let totalStart = null;
  let paused = false;
  let autosaveTimer = null;

  async function initSessionFromQuery() {
    const params = new URLSearchParams(location.search);
    const id = params.get('session');
    const focus = params.get('focus');
    if (!id) return;
    try {
      const res = await fetch(`/api/training/sessions/${encodeURIComponent(id)}`);
      if (res.ok) sessionData = await res.json();
    } catch (e) {
      console.warn('Fetch session error', e);
    }
    if (!sessionData) {
      sessionData = {
        id,
        title: 'Тестова сесія',
        exercises: [
          { id: 'ex1', name: 'Жим лежачи', sets: 4, reps: 8, location: 'зал' },
          { id: 'ex2', name: 'Підтягування', sets: 3, reps: 6, location: 'зал' }
        ]
      };
    }
    currentIndex = focus ? Number(focus) : 0;
    renderSession();
    wireControls();
    totalStart = sessionData.started_at ? new Date(sessionData.started_at).getTime() : Date.now();
    updateTotalTimer();
    restoreAutosave();
  }

  function renderSession() {
    if (!sessionData) return;
    qs('#tr-live-title').textContent = sessionData.title || 'Live Session';
    qs('#tr-live-step').textContent = `${currentIndex + 1} / ${sessionData.exercises.length}`;
    const ex = sessionData.exercises[currentIndex];
    qs('#tr-current-ex-name').textContent = ex.name;
    qs('#tr-current-ex-sub').textContent = `${ex.sets}×${ex.reps} · ${ex.location || 'будь-де'}`;
    qs('#tr-current-location').textContent = ex.location || '—';
    renderSets(ex);
    renderOverview();
  }

  function renderSets(ex) {
    const list = qs('#tr-sets-list');
    if (!list) return;
    list.innerHTML = '';
    for (let i = 0; i < (ex.sets || 1); i++) {
      const row = document.createElement('div');
      row.className = 'tr-set-row';
      row.innerHTML = `
        <div class="tr-set-index">${i + 1}</div>
        <div style="min-width:120px">
          <input class="cmp-input tr-set-weight" type="number" placeholder="кг" step="0.5" aria-label="Вага підходу ${i + 1}">
        </div>
        <div style="min-width:120px">
          <input class="cmp-input tr-set-reps" type="number" placeholder="повт." value="${ex.reps}" aria-label="Повторення підходу ${i + 1}">
        </div>
        <div class="tr-set-controls">
          <button class="tr-btn tr-btn--primary tr-set-done" data-set="${i}">Готово</button>
        </div>
      `;
      list.appendChild(row);
    }
    qsa('.tr-set-done').forEach(b => b.addEventListener('click', onSetDone));
  }

  function onSetDone(e) {
    const setIndex = Number(e.currentTarget.dataset.set);
    const row = e.currentTarget.closest('.tr-set-row');
    const weight = row.querySelector('.tr-set-weight').value || 0;
    const reps = row.querySelector('.tr-set-reps').value || 0;
    e.currentTarget.textContent = 'Збережено';
    e.currentTarget.disabled = true;
    e.currentTarget.classList.remove('tr-btn--primary');
    e.currentTarget.classList.add('tr-btn--ghost');
    startRest(60);
    updateOverviewProgress();
    scheduleAutosave();
  }

  function startRest(seconds) {
    restRemaining = seconds;
    const el = qs('#tr-rest-timer');
    if (el) el.textContent = formatTime(restRemaining);
    if (restTimer) clearInterval(restTimer);
    restTimer = setInterval(() => {
      restRemaining--;
      if (el) el.textContent = formatTime(restRemaining);
      if (restRemaining <= 0) {
        clearInterval(restTimer);
        restTimer = null;
        if (el) el.textContent = '00:00';
        openToast('Час відпочинку завершено', 'success');
      }
    }, 1000);
  }

  function stopRest() {
    if (restTimer) {
      clearInterval(restTimer);
      restTimer = null;
      const el = qs('#tr-rest-timer');
      if (el) el.textContent = '00:00';
    }
  }

  function wireControls() {
    qs('#tr-next-ex') && qs('#tr-next-ex').addEventListener('click', nextExercise);
    qs('#tr-prev-ex') && qs('#tr-prev-ex').addEventListener('click', prevExercise);
    qs('#tr-rest-start') && qs('#tr-rest-start').addEventListener('click', () => startRest(60));
    qs('#tr-rest-stop') && qs('#tr-rest-stop').addEventListener('click', stopRest);
    qs('#tr-save-notes') && qs('#tr-save-notes').addEventListener('click', saveNotes);
    qs('#tr-live-end') && qs('#tr-live-end').addEventListener('click', endSession);
    qs('#tr-pause') && qs('#tr-pause').addEventListener('click', pauseSession);
    qs('#tr-resume') && qs('#tr-resume').addEventListener('click', resumeSession);
    qs('#tr-save-progress') && qs('#tr-save-progress').addEventListener('click', saveProgress);
    qs('#tr-abort') && qs('#tr-abort').addEventListener('click', abortSession);
  }

  function nextExercise() {
    if (!sessionData) return;
    if (currentIndex < sessionData.exercises.length - 1) {
      currentIndex++;
      renderSession();
    } else {
      openToast('Це остання вправа', 'warn');
    }
  }

  function prevExercise() {
    if (!sessionData) return;
    if (currentIndex > 0) {
      currentIndex--;
      renderSession();
    } else {
      openToast('Це перша вправа', 'warn');
    }
  }

  function updateOverviewProgress() {
    const done = qsa('.tr-set-done[disabled]').length;
    const total = qsa('.tr-set-row').length;
    const fill = qs('#tr-progress-fill');
    if (fill) fill.style.width = `${Math.round((done / Math.max(1, total)) * 100)}%`;
    qs('#tr-progress-text') && (qs('#tr-progress-text').textContent = `${done} / ${total}`);
    qs('#tr-overview-sets-done') && (qs('#tr-overview-sets-done').textContent = done);
  }

  function renderOverview() {
    qs('#tr-overview-ex-count') && (qs('#tr-overview-ex-count').textContent = sessionData.exercises.length);
    qs('#tr-overview-sets-done') && (qs('#tr-overview-sets-done').textContent = 0);
    qs('#tr-overview-volume') && (qs('#tr-overview-volume').textContent = '—');
    qs('#tr-overview-pace') && (qs('#tr-overview-pace').textContent = '—');
    qs('#tr-overview-main-muscles') && (qs('#tr-overview-main-muscles').textContent = '—');
  }

  function saveNotes() {
    const notesEl = qs('#tr-session-notes');
    const notes = notesEl ? notesEl.value || '' : '';
    if (!sessionData) return openToast('Немає сесії для збереження', 'warn');
    fetch(`/api/training/sessions/${encodeURIComponent(sessionData.id)}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    }).then(() => openToast('Нотатки збережено', 'success'))
      .catch(() => openToast('Помилка збереження нотаток', 'error'));
  }

  function saveProgress() {
    openToast('Прогрес збережено (локально)', 'success');
    scheduleAutosave();
  }

  function endSession() {
    if (!confirm('Завершити сесію?')) return;
    openToast('Сесія завершена', 'success');
    setTimeout(() => location.href = '/training', 600);
  }

  function abortSession() {
    if (!confirm('Скасувати сесію? Всі незбережені дані будуть втрачені.')) return;
    openToast('Сесію скасовано', 'warn');
    setTimeout(() => location.href = '/training', 600);
  }

  function pauseSession() {
    paused = true;
    const p = qs('#tr-pause'); const r = qs('#tr-resume');
    if (p) p.style.display = 'none';
    if (r) r.style.display = '';
    openToast('Сесія на паузі', 'warn');
  }

  function resumeSession() {
    paused = false;
    const p = qs('#tr-pause'); const r = qs('#tr-resume');
    if (r) r.style.display = 'none';
    if (p) p.style.display = '';
    openToast('Сесію відновлено', 'success');
  }

  function updateTotalTimer() {
    const el = qs('#tr-live-total');
    if (!el) return;
    setInterval(() => {
      if (!totalStart) return;
      const diff = Date.now() - totalStart;
      el.textContent = formatTime(Math.floor(diff / 1000));
    }, 1000);
  }

  function formatTime(sec) {
    sec = Math.max(0, Math.floor(sec));
    const mm = String(Math.floor(sec / 60)).padStart(2, '0');
    const ss = String(sec % 60).padStart(2, '0');
    return `${mm}:${ss}`;
  }

  function scheduleAutosave() {
    if (autosaveTimer) clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(() => {
      if (sessionData) localStorage.setItem('nosi_live_session', JSON.stringify(sessionData));
      if (sessionData && sessionData.id) {
        fetch(`/api/training/sessions/${encodeURIComponent(sessionData.id)}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: sessionData })
        }).catch(() => {});
      }
    }, 800);
  }

  function restoreAutosave() {
    const raw = localStorage.getItem('nosi_live_session');
    if (!raw) return;
    try {
      const saved = JSON.parse(raw);
      if (saved && saved.id === sessionData.id) sessionData = saved;
    } catch { }
  }

  function openToast(text, type = 'success') {
    const t = document.createElement('div');
    t.className = `tr-toast ${type === 'warn' ? 'warn' : type === 'error' ? 'error' : 'success'}`;
    t.textContent = text;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add('show'), 20);
    setTimeout(() => t.remove(), 3500);
  }

  document.addEventListener('DOMContentLoaded', initSessionFromQuery);
  window.NosiSession = { initSessionFromQuery };
})();
