import { renderRadar } from './radar.js';
import { openPlanModal } from './plan.js';
import { startLiveFromData } from './session.js';

const state = { user: null, today: null, plan: null, radar: null };

async function fetchToday(){
  try {
    const res = await fetch('/api/training/today');
    if(!res.ok) throw new Error('no data');
    const data = await res.json();
    state.today = data;
    state.radar = data.muscles || {};
    renderSession(data);
    renderRadar('#tr-radar', data.muscles || {});
    renderPlanList(data.plan || []);
    renderRecs(data.recommendations || []);
  } catch(e){
    console.error(e);
    document.getElementById('tr-session-title').textContent = 'No session';
  }
}

function renderSession(data){
  document.getElementById('tr-session-title').textContent = data.title || 'Today';
  const ul = document.getElementById('tr-exercises');
  ul.innerHTML = '';
  (data.exercises || []).forEach((ex, idx) => {
    const li = document.createElement('li');
    li.className = 'tr-exercise-item fade-in';
    li.innerHTML = `<div><div class="tr-ex-name">${ex.name}</div><div class="tr-ex-meta">${ex.sets}×${ex.reps} · ${ex.location}</div></div>
                    <div><button class="tr-btn tr-btn--ghost" data-idx="${idx}">Edit</button></div>`;
    ul.appendChild(li);
  });
}

function renderPlanList(plans){
  const el = document.getElementById('tr-plan-list');
  el.innerHTML = '';
  plans.forEach(p => {
    const div = document.createElement('div');
    div.className = 'tr-plan-item';
    div.innerHTML = `<div>${p.name}</div><div><button class="tr-btn tr-btn--ghost" data-id="${p.id}">Open</button></div>`;
    el.appendChild(div);
  });
}

function renderRecs(recs){
  const el = document.getElementById('tr-recs');
  el.innerHTML = recs.length ? recs.map(r=>`<div>${r}</div>`).join('') : '<div class="tr-muted">No recommendations</div>';
}

document.getElementById('tr-open-plan').addEventListener('click', openPlanModal);
document.getElementById('tr-edit-plan').addEventListener('click', openPlanModal);
document.getElementById('tr-start').addEventListener('click', () => {
  if(state.today && state.today.sessionId) startLiveFromData(state.today);
});

window.addEventListener('DOMContentLoaded', fetchToday);
