(function(){
  'use strict';

  const state = {
    today:null,
    plans:[],
    activePlan:null,
    exercisesBank:[],
    currentSession:null,
    ui:{ modalOpen:false },
    offlineQueueKey:'nosi_offline_queue_v2'
  };

  function qs(sel, root=document){ return (root||document).querySelector(sel); }
  function qsa(sel, root=document){ return Array.from((root||document).querySelectorAll(sel)); }
  function el(tag, cls){ const e=document.createElement(tag); if(cls) e.className=cls; return e; }
  function nowIso(){ return new Date().toISOString(); }
  function safeJSONParse(s,fallback=null){ try{ return JSON.parse(s); }catch{ return fallback; } }
  function debounce(fn,ms=300){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),ms); }; }
  function openToast(text,type='info',timeout=2400){
    const container = qs('#tr-toast-container');
    if(!container) return;
    const t = el('div','tr-toast');
    if(type==='success') t.classList.add('success');
    if(type==='warn') t.classList.add('warn');
    if(type==='error') t.classList.add('error');
    t.innerHTML = `<div class="title">${text}</div>`;
    container.appendChild(t);
    requestAnimationFrame(()=>t.classList.add('show'));
    setTimeout(()=>{ t.classList.remove('show'); setTimeout(()=>t.remove(),300); }, timeout);
  }

  const OfflineQueue = (function(){
    const KEY = state.offlineQueueKey;
    function load(){ return safeJSONParse(localStorage.getItem(KEY),[]); }
    function save(q){ localStorage.setItem(KEY, JSON.stringify(q)); }
    async function flush(){
      const q = load();
      if(!q.length) return;
      const remaining = [];
      for(const item of q){
        try{
          if(item.type==='patchSession') await API.patchSession(item.id,item.payload);
          else if(item.type==='createSession') await API.createSession(item.payload);
          else if(item.type==='post') await API.post(item.path,item.payload);
        }catch(e){ remaining.push(item); }
      }
      save(remaining);
    }
    function push(item){ const q=load(); q.push(item); save(q); }
    return { load, save, flush, push };
  })();

  function renderHeader(today){
    const titleEl = qs('#tr-session-title');
    const typeEl = qs('#tr-session-type');
    const durEl = qs('#tr-session-duration');
    if(titleEl) titleEl.textContent = today?.title || 'Сьогодні';
    if(typeEl) typeEl.textContent = today?.type || '—';
    if(durEl) durEl.textContent = (today?.duration ? `${today.duration}` : '—') + ' хв';
  }

  function renderRadar(){
    const container = qs('#tr-radar');
    if(!container) return;
    const radarData = state.activePlan?.meta?.radar || state.today?.muscles || {};
    if(window.NosiRadar) NosiRadar.render(container, radarData, { duration:700, maxSize: Math.min(container.clientWidth, 420) });
    else container.textContent = 'Радар недоступний';
  }

  function renderLegend(){
    const legend = qs('#tr-legend');
    if(!legend) return;
    legend.innerHTML = '';
    const muscles = state.activePlan?.meta?.muscles || Object.keys(state.today?.muscles || {});
    (muscles || []).forEach((m,i)=>{
      const item = el('div','tr-legend-item');
      item.dataset.index = i;
      const sw = el('span',`tr-legend-swatch ${i%3===0?'yellow':i%3===1?'purple':'teal'}`);
      const lbl = el('span','tr-legend-label');
      lbl.textContent = m;
      item.appendChild(sw);
      item.appendChild(lbl);
      item.addEventListener('click', ()=>{ item.classList.toggle('is-muted'); });
      legend.appendChild(item);
    });
  }

  function renderPlanSelector(){
    const planName = state.activePlan?.name || 'Немає активного плану';
    const elTitle = qs('#tr-session-title');
    if(elTitle) elTitle.setAttribute('data-plan', planName);
  }

  function renderExercisesList(exercises){
    const list = qs('#tr-exercises');
    if(!list) return;
    list.innerHTML = '';
    exercises.forEach((ex, idx)=>{
      const li = el('li','tr-exercise-row');
      li.dataset.index = idx;
      const left = el('div','tr-ex-left');
      left.innerHTML = `<strong class="tr-ex-name">${ex.name}</strong><div class="tr-ex-meta">${(ex.sets && ex.sets.length) || (ex.sets || 1)} підходи · ${ex.reps || '—'} повт.</div>`;
      const right = el('div','tr-ex-right');
      const sets = ex.sets || Array.from({length:ex.sets||1}).map(()=>({weight:null,reps:ex.reps||''}));
      sets.forEach((s,si)=>{
        const setRow = el('div','tr-set-row');
        const weightVal = (s && s.weight != null) ? s.weight : '';
        setRow.innerHTML = `<label class="tr-set-label">S${si+1}</label>
          <input class="tr-set-input tr-input" data-set="${si}" data-ex="${idx}" value="${weightVal}" placeholder="кг" aria-label="Вага підходу ${si+1}">
          <input class="tr-set-reps tr-input" data-set="${si}" data-ex="${idx}" value="${s && s.reps ? s.reps : ex.reps || ''}" placeholder="повт." aria-label="Повторення підходу ${si+1}">
          <button class="tr-set-done tr-btn tr-btn--ghost" data-ex="${idx}" data-set="${si}" type="button">${s && s.done ? '✓' : 'Готово'}</button>`;
        right.appendChild(setRow);
      });
      li.appendChild(left);
      li.appendChild(right);
      list.appendChild(li);
    });
    qsa('.tr-set-input', list).forEach(inp=>inp.addEventListener('input', debounce(onExerciseInput,300)));
    attachExerciseHandlers();
  }

  function renderQuickStats(){
    qs('#tr-week-load') && (qs('#tr-week-load').textContent = state.activePlan?.meta?.weekly_load || '—');
    qs('#tr-focus-muscles') && (qs('#tr-focus-muscles').textContent = state.activePlan?.meta?.focus || '—');
    qs('#tr-week-sessions') && (qs('#tr-week-sessions').textContent = state.activePlan ? `${state.activePlan.meta?.planned_sessions||0} · ${state.activePlan.meta?.done_sessions||0}` : '—');
    qs('#tr-fatigue') && (qs('#tr-fatigue').textContent = state.activePlan?.meta?.fatigue || '—');
  }

  function renderRecommendations(){
    const container = qs('#tr-recs');
    if(!container) return;
    container.innerHTML = '';
    const recs = state.activePlan?.meta?.recommendations || state.today?.recommendations || ['Підтримуйте прогрес: додавайте 2.5% ваги кожні 2 тижні.'];
    recs.forEach(r=>{
      const d = el('div','tr-rec');
      d.textContent = r;
      container.appendChild(d);
    });
  }

  function onExerciseInput(e){
    const exIdx = Number(e.target.dataset.ex);
    const setIdx = Number(e.target.dataset.set);
    if(!state.currentSession || !state.currentSession.data) return;
    const val = e.target.value.trim();
    const ex = state.currentSession.data.exercises[exIdx];
    if(!ex) return;
    ex.sets = ex.sets || [];
    ex.sets[setIdx] = ex.sets[setIdx] || {};
    ex.sets[setIdx].weight = val ? Number(val) : null;
    scheduleSessionAutosave();
  }

  function onExerciseSetDone(e){
    const exIdx = Number(e.currentTarget.dataset.ex);
    const setIdx = Number(e.currentTarget.dataset.set);
    if(!state.currentSession || !state.currentSession.data) return;
    const ex = state.currentSession.data.exercises[exIdx];
    if(!ex) return;
    ex.sets = ex.sets || [];
    ex.sets[setIdx] = ex.sets[setIdx] || {};
    ex.sets[setIdx].done = true;
    e.currentTarget.textContent = '✓';
    e.currentTarget.disabled = true;
    scheduleSessionAutosave();
    renderSessionProgress();
  }

  function renderSessionProgress(){
    const done = qsa('.tr-set-done').filter(b=>b.textContent.trim()==='✓').length;
    const total = qsa('.tr-set-row').length || 0;
    const fill = qs('#tr-progress-fill');
    if(fill) fill.style.width = `${Math.round((done/Math.max(1,total))*100)}%`;
    qs('#tr-progress-text') && (qs('#tr-progress-text').textContent = `${done} / ${total}`);
    qs('#tr-overview-sets-done') && (qs('#tr-overview-sets-done').textContent = done);
  }

  function loadLocalSession(){ return safeJSONParse(localStorage.getItem('nosi_current_session'), null); }
  function saveLocalSession(){ if(!state.currentSession) return; localStorage.setItem('nosi_current_session', JSON.stringify(state.currentSession)); }

  const scheduleSessionAutosave = debounce(function(){
    saveLocalSession();
    if(state.currentSession && state.currentSession.id && !String(state.currentSession.id).startsWith('local-')){
      API.patchSession(state.currentSession.id, { data: state.currentSession.data }).catch(err=>{
        OfflineQueue.push({ type:'patchSession', id: state.currentSession.id, payload:{ data: state.currentSession.data } });
      });
    }else{
      OfflineQueue.push({ type:'patchSession', id: state.currentSession.id || `local-${Date.now()}`, payload:{ data: state.currentSession.data } });
    }
  },800);

  async function startSessionFlow(){
    if(state.currentSession) return;
    const payload = { plan_id: state.activePlan?.id || null, title:`Сесія ${new Date().toLocaleString()}`, started_at: nowIso() };
    try{
      const created = await API.createSession(payload);
      state.currentSession = { id: created.id, plan_id: created.plan_id, title: created.title, started_at: created.started_at, data:{ exercises: buildExercisesFromPlan(state.activePlan) } };
      saveLocalSession();
      renderSessionPanel();
      startLiveTimer();
    }catch(err){
      state.currentSession = { id:`local-${Date.now()}`, plan_id: state.activePlan?.id || null, title: payload.title, started_at: payload.started_at, data:{ exercises: buildExercisesFromPlan(state.activePlan) } };
      OfflineQueue.push({ type:'createSession', payload });
      saveLocalSession();
      renderSessionPanel();
      startLiveTimer();
    }
  }

  function buildExercisesFromPlan(plan){
    const day = plan?.meta?.days?.[0] || { exercises: [] };
    return (day.exercises || []).map(ex=>({
      exercise_id: ex.exercise_id || null,
      name: ex.name || 'Вправа',
      reps: ex.reps || null,
      sets: (ex.sets || [{ target:null }]).map(s=>({ weight: s.target || null, reps: s.reps || ex.reps || null, done:false }))
    }));
  }

  function renderSessionPanel(){
    if(!state.currentSession){
      qs('#tr-session-title') && (qs('#tr-session-title').textContent = 'Немає активної сесії');
      qs('#tr-session-type') && (qs('#tr-session-type').textContent = '—');
      qs('#tr-session-duration') && (qs('#tr-session-duration').textContent = '— хв');
      renderExercisesList([]);
      return;
    }
    qs('#tr-session-title') && (qs('#tr-session-title').textContent = state.currentSession.title || 'Поточна сесія');
    qs('#tr-session-type') && (qs('#tr-session-type').textContent = state.currentSession.type || '—');
    const started = state.currentSession.started_at ? new Date(state.currentSession.started_at).getTime() : null;
    const durationMs = started ? (Date.now() - started) : 0;
    qs('#tr-session-duration') && (qs('#tr-session-duration').textContent = `${Math.round(durationMs/60000)} хв`);
    renderExercisesList(state.currentSession.data?.exercises || []);
    renderSessionProgress();
  }

  let liveInterval = null;
  function startLiveTimer(){ if(liveInterval) return; liveInterval = setInterval(()=>{ renderSessionPanel(); },5000); }
  function stopLiveTimer(){ if(!liveInterval) return; clearInterval(liveInterval); liveInterval = null; }

  function openModal(html){
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
    if(!overlay || !modal) return;
    overlay.setAttribute('aria-hidden','false');
    modal.innerHTML = html;
    state.ui.modalOpen = true;
  }
  function closeModal(){
    const overlay = qs('#tr-modal-overlay');
    const modal = qs('#tr-modal');
    if(!overlay || !modal) return;
    overlay.setAttribute('aria-hidden','true');
    modal.innerHTML = '';
    state.ui.modalOpen = false;
  }

  function openPlanQuickEditor(){
    openModal(`<h3 style="margin:0 0 8px 0">Редагувати план</h3>
      <label class="cmp-label">Назва</label>
      <input id="tr-modal-plan-name" class="cmp-input" value="${state.activePlan?.name || 'Мій план'}">
      <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
        <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel" type="button">Скасувати</button>
        <button class="tr-btn tr-btn--primary" id="tr-modal-save" type="button">Зберегти</button>
      </div>`);
    qs('#tr-modal-cancel') && qs('#tr-modal-cancel').addEventListener('click', closeModal);
    qs('#tr-modal-save') && qs('#tr-modal-save').addEventListener('click', async ()=>{
      const name = qs('#tr-modal-plan-name').value.trim() || 'Мій план';
      try{ await API.post(`/plans/${state.activePlan?.id||''}`, { name }); }catch(e){}
      closeModal();
      await refreshPlans();
      renderPlanPanel();
    });
  }

  function renderBalanceHints(){
    const list = qs('#tr-balance-list');
    if(!list) return;
    list.innerHTML = '';
    const hints = state.activePlan?.meta?.balance_hints || ['Розподіли навантаження між великими групами','Зверни увагу на відновлення після важких днів'];
    hints.forEach(h=>{
      const li = el('li','tr-balance-item');
      li.textContent = h;
      list.appendChild(li);
    });
  }

  function renderNextSessionPreview(){
    qs('#tr-next-session-title') && (qs('#tr-next-session-title').textContent = state.activePlan?.meta?.next_session?.title || '—');
    qs('#tr-next-type') && (qs('#tr-next-type').textContent = state.activePlan?.meta?.next_session?.type || '—');
    qs('#tr-next-muscles') && (qs('#tr-next-muscles').textContent = (state.activePlan?.meta?.next_session?.muscles || []).join(', ') || '—');
    qs('#tr-next-duration') && (qs('#tr-next-duration').textContent = state.activePlan?.meta?.next_session?.duration ? `${state.activePlan.meta.next_session.duration}` : '—');
  }

  async function refreshPlans(){
    try{
      const plans = await API.listPlans();
      state.plans = plans || [];
      state.activePlan = state.plans[0] || state.activePlan;
    }catch(e){ console.warn('Could not load plans', e); }
  }

  function attachUI(){
    const startBtn = qs('#tr-start');
    const liveStart = qs('#tr-live-start');
    const openPlan = qs('#tr-open-plan');
    const savePremium = qs('#tr-save-premium-muscles');
    const nextOpen = qs('#tr-next-open');

    if(startBtn) startBtn.addEventListener('click', startSessionFlow);
    if(liveStart) liveStart.addEventListener('click', startSessionFlow);
    if(openPlan) openPlan.addEventListener('click', ()=>{ if(state.activePlan) window.location.href = `/training/plans/${state.activePlan.id}`; else openToast('У вас немає активного плану','warn'); });
    if(savePremium) savePremium.addEventListener('click', onSavePremium);
    if(nextOpen) nextOpen.addEventListener('click', ()=>window.location.href = '/training/sessions/next');

    const editPlanBtn = qs('#tr-edit-plan');
    if(editPlanBtn) editPlanBtn.addEventListener('click', openPlanQuickEditor);

    const overlay = qs('#tr-modal-overlay');
    if(overlay) overlay.addEventListener('click', (e)=>{ if(e.target===overlay) closeModal(); });

    document.addEventListener('keydown',(e)=>{
      if(e.key==='s' && (e.ctrlKey||e.metaKey)){ e.preventDefault(); if(state.currentSession) scheduleSessionAutosave(); }
      if(e.key==='Escape' && state.ui.modalOpen) closeModal();
    });

    window.addEventListener('online', ()=>{ OfflineQueue.flush().catch(err=>console.warn('Flush failed',err)); });
  }

  async function onSavePremium(){
    const selected = qsa('.tr-muscle-btn.is-selected', qs('#tr-premium-muscles') || document).map(b=>b.dataset.muscle);
    try{
      await API.post('/user/preferences', { key:'premium_muscles', value: JSON.stringify(selected) });
      openToast('Цільові м’язи збережено','success');
    }catch(e){
      OfflineQueue.push({ type:'post', path:'/user/preferences', payload:{ key:'premium_muscles', value: JSON.stringify(selected) } });
      openToast('Збереження в чергу (offline)','warn');
    }
  }

  function attachExerciseHandlers(){
    const list = qs('#tr-exercises');
    if(!list) return;
    list.removeEventListener && list.removeEventListener('click', exerciseListClick);
    list.addEventListener('click', exerciseListClick);
    qsa('.tr-set-done', list).forEach(btn=>{
      btn.removeEventListener && btn.removeEventListener('click', onExerciseSetDone);
      btn.addEventListener('click', onExerciseSetDone);
    });
  }

  function exerciseListClick(e){
    const btn = e.target.closest('.tr-set-done');
    if(!btn) return;
    const exIdx = Number(btn.dataset.ex);
    const setIdx = Number(btn.dataset.set);
    if(!state.currentSession || !state.currentSession.data) return;
    const ex = state.currentSession.data.exercises[exIdx];
    if(!ex) return;
    ex.sets = ex.sets || [];
    ex.sets[setIdx] = ex.sets[setIdx] || {};
    ex.sets[setIdx].done = true;
    btn.textContent = '✓';
    btn.disabled = true;
    scheduleSessionAutosave();
    renderSessionProgress();
  }

  function loadExercisesForBuilder(exSelectSel='#tr-builder-exercise', muscleSelectSel='#tr-builder-muscle'){
    const exSel = document.querySelector(exSelectSel);
    const mSel = document.querySelector(muscleSelectSel);
    if(!exSel || !mSel) return;
    const musclesSet = new Set();
    (state.exercisesBank || []).forEach(ex=>{ if(ex.muscle) musclesSet.add(ex.muscle); });
    mSel.innerHTML = '<option value="">Оберіть м\'яз</option>';
    Array.from(musclesSet).sort().forEach(m=>{
      const o = document.createElement('option');
      o.value = m;
      o.textContent = m;
      mSel.appendChild(o);
    });
    function populateExercises(filterMuscle=''){
      exSel.innerHTML = '<option value="">Оберіть вправу</option>';
      (state.exercisesBank || []).filter(ex=>{
        if(!filterMuscle) return true;
        return String(ex.muscle||'').toLowerCase() === String(filterMuscle).toLowerCase();
      }).forEach(ex=>{
        const o = document.createElement('option');
        o.value = ex.id || ex.name;
        o.textContent = ex.name + (ex.equipment ? ` · ${ex.equipment}` : '');
        o.dataset.muscle = ex.muscle || '';
        exSel.appendChild(o);
      });
    }
    populateExercises();
    mSel.addEventListener('change', ()=>populateExercises(mSel.value));
    window._loadExercisesForBuilder = populateExercises;
  }

  function wireBuilderAdd(buttonSel='#tr-builder-add'){
    const btn = document.querySelector(buttonSel);
    if(!btn) return;
    btn.addEventListener('click', ()=>{
      const exSel = document.querySelector('#tr-builder-exercise');
      const muscleSel = document.querySelector('#tr-builder-muscle');
      const locSel = document.querySelector('#tr-builder-location');
      const setsInp = document.querySelector('#tr-builder-sets');
      const repsInp = document.querySelector('#tr-builder-reps');
      if(!exSel || !exSel.value){ openToast('Оберіть вправу','warn'); return; }
      const exName = exSel.options[exSel.selectedIndex].textContent;
      const exId = exSel.value;
      const muscle = muscleSel ? muscleSel.value : '';
      const location = locSel ? locSel.value : '';
      const sets = Math.max(1, Number(setsInp?.value || 1));
      const reps = Math.max(1, Number(repsInp?.value || 1));
      const newEx = { exercise_id: exId, name: exName, muscle, location, reps, sets: Array.from({length:sets}).map(()=>({ weight:null, reps, done:false })) };
      if(!state.currentSession){
        state.currentSession = { id:`local-${Date.now()}`, title:`Локальна сесія ${new Date().toLocaleString()}`, started_at:new Date().toISOString(), data:{ exercises: [] } };
      }
      state.currentSession.data = state.currentSession.data || { exercises: [] };
      state.currentSession.data.exercises.push(newEx);
      saveLocalSession();
      renderSessionPanel();
      openToast('Вправа додана в сесію','success');
    });
  }

  async function loadInitialData(){
    try{
      const plansFromApi = await API.safe(()=>API.listPlans());
      if(plansFromApi && Array.isArray(plansFromApi) && plansFromApi.length){
        state.plans = plansFromApi;
      } else {
        state.plans = [];
      }
      state.activePlan = state.plans[0] || null;
    }catch(e){ state.plans = []; state.activePlan = null; }

    try{
      const exercises = await API.safe(()=>API.listExercises());
      state.exercisesBank = Array.isArray(exercises) ? exercises : [];
      if(!state.exercisesBank.length){
        state.exercisesBank = [
          { id:'ex-fixt-1', name:'Жим лежачи', muscle:'Груди', equipment:'Штанга' },
          { id:'ex-fixt-2', name:'Підтягування', muscle:'Спина', equipment:'Турнік' },
          { id:'ex-fixt-3', name:'Присідання', muscle:'Ноги', equipment:'Штанга' }
        ];
      }
    }catch(e){ state.exercisesBank = [
      { id:'ex-fixt-1', name:'Жим лежачи', muscle:'Груди', equipment:'Штанга' },
      { id:'ex-fixt-2', name:'Підтягування', muscle:'Спина', equipment:'Турнік' },
      { id:'ex-fixt-3', name:'Присідання', muscle:'Ноги', equipment:'Штанга' }
    ]; }

    try{
      const res = await fetch('/api/training/today',{ headers:{ 'Content-Type':'application/json' } });
      if(res.ok) state.today = await res.json();
      else state.today = null;
    }catch(e){ state.today = null; }
  }

  async function init(){
    attachUI();
    await loadInitialData();
    const saved = loadLocalSession();
    if(saved) state.currentSession = saved;
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
    try{ loadExercisesForBuilder('#tr-builder-exercise','#tr-builder-muscle'); wireBuilderAdd('#tr-builder-add'); }catch(e){}
    OfflineQueue.flush().catch(()=>{});
  }

  function renderPlanPanel(){
    renderPlanSelector();
    renderRadar();
    renderLegend();
    renderBalanceHints();
  }

  window.TrainingMain = { state, init, refreshPlans, renderRadar, renderSessionPanel, startSessionFlow, OfflineQueue, buildExercisesFromPlan };

  document.addEventListener('DOMContentLoaded', init);
})();
