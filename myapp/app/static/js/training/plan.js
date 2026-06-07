export function openPlanModal(){
  const overlay = document.getElementById('tr-modal-overlay');
  const modal = document.getElementById('tr-modal');
  overlay.setAttribute('aria-hidden','false');
  modal.innerHTML = `<h3 style="margin:0 0 8px 0">Edit Plan</h3>
    <p class="cmp-card-sub">Quick plan editor</p>
    <div style="margin-top:12px">
      <label class="cmp-label">Plan name</label>
      <input class="cmp-input" id="tr-plan-name" value="My Plan">
    </div>
    <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end;">
      <button class="tr-btn tr-btn--ghost" id="tr-modal-cancel">Cancel</button>
      <button class="tr-btn tr-btn--primary" id="tr-modal-save">Save</button>
    </div>`;
  document.getElementById('tr-modal-cancel').addEventListener('click', closeModal);
  document.getElementById('tr-modal-save').addEventListener('click', async ()=>{
    const name = document.getElementById('tr-plan-name').value;
    // minimal POST
    await fetch('/api/plans', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name})});
    closeModal();
    location.reload();
  });
}

function closeModal(){
  document.getElementById('tr-modal-overlay').setAttribute('aria-hidden','true');
}
document.getElementById('tr-modal-overlay').addEventListener('click', (e)=>{
  if(e.target.id === 'tr-modal-overlay') closeModal();
});
