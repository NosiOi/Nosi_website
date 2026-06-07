export function startLiveFromData(data){
  if(data && data.sessionId){
    window.location.href = `/dashboard/training/session?session=${data.sessionId}`;
  }
}

// If on session page, you can implement step logic here
if(window.location.pathname.includes('/training/session')){
  // basic example: fetch session by id and render
  (async ()=>{
    const params = new URLSearchParams(location.search);
    const id = params.get('session');
    if(!id) return;
    const res = await fetch(`/api/session/${id}`);
    if(!res.ok) return;
    const data = await res.json();
    document.getElementById('tr-live-title').textContent = data.title || 'Live Session';
    // render first step
    const area = document.getElementById('tr-live-step-area');
    area.innerHTML = `<div style="padding:18px"><strong>${data.exercises[0].name}</strong><p>${data.exercises[0].sets}×${data.exercises[0].reps}</p></div>`;
    // wire next/prev
    document.getElementById('tr-live-next').addEventListener('click', ()=> alert('Next step (implement)'));
  })();
}
