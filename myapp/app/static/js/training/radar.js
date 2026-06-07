export function renderRadar(selectorOrEl, muscles){
  const container = (typeof selectorOrEl === 'string') ? document.querySelector(selectorOrEl) : selectorOrEl;
  if(!container) return;
  const labels = Object.keys(muscles);
  const values = labels.map(l => Math.max(0, Math.min(1, muscles[l]))); // 0..1
  const size = Math.min(container.clientWidth, 320);
  const cx = size/2, cy = size/2, r = size*0.36;
  const svgNS = "http://www.w3.org/2000/svg";
  container.innerHTML = '';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);
  svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
  for(let i=4;i>=1;i--){
    const ring = document.createElementNS(svgNS,'circle');
    ring.setAttribute('cx',cx); ring.setAttribute('cy',cy);
    ring.setAttribute('r', (r/4)*i);
    ring.setAttribute('fill','none');
    ring.setAttribute('stroke','rgba(255,255,255,0.03)');
    ring.setAttribute('stroke-width','1');
    svg.appendChild(ring);
  }
  const n = labels.length || 6;
  labels.forEach((lab, i) => {
    const angle = (Math.PI*2)*(i/n) - Math.PI/2;
    const x = cx + Math.cos(angle)*r;
    const y = cy + Math.sin(angle)*r;
    const line = document.createElementNS(svgNS,'line');
    line.setAttribute('x1',cx); line.setAttribute('y1',cy);
    line.setAttribute('x2',x); line.setAttribute('y2',y);
    line.setAttribute('stroke','rgba(255,255,255,0.04)');
    line.setAttribute('stroke-width','1');
    svg.appendChild(line);
    const tx = cx + Math.cos(angle)*(r+18);
    const ty = cy + Math.sin(angle)*(r+18);
    const text = document.createElementNS(svgNS,'text');
    text.setAttribute('x',tx); text.setAttribute('y',ty);
    text.setAttribute('fill','#e9e9ef');
    text.setAttribute('font-size','11');
    text.setAttribute('text-anchor', Math.cos(angle)>0.1 ? 'start' : Math.cos(angle)<-0.1 ? 'end' : 'middle');
    text.setAttribute('dominant-baseline','middle');
    text.textContent = lab;
    svg.appendChild(text);
  });
  const points = values.map((v,i)=>{
    const angle = (Math.PI*2)*(i/n) - Math.PI/2;
    const rr = v * r;
    return `${cx + Math.cos(angle)*rr},${cy + Math.sin(angle)*rr}`;
  }).join(' ');
  const poly = document.createElementNS(svgNS,'polygon');
  poly.setAttribute('points', points);
  poly.setAttribute('fill','rgba(255,212,59,0.12)'); // yellow fill subtle
  poly.setAttribute('stroke','rgba(255,212,59,0.95)');
  poly.setAttribute('stroke-width','2');
  poly.setAttribute('stroke-linejoin','round');
  svg.appendChild(poly);

  const tooltip = document.createElement('div');
  tooltip.style.position='absolute'; tooltip.style.pointerEvents='none';
  tooltip.style.padding='6px 8px'; tooltip.style.background='rgba(0,0,0,0.7)';
  tooltip.style.color='#fff'; tooltip.style.borderRadius='6px'; tooltip.style.fontSize='12px'; tooltip.style.display='none';
  container.style.position='relative';
  container.appendChild(svg);
  container.appendChild(tooltip);

  labels.forEach((lab,i)=>{
    const angle = (Math.PI*2)*(i/n) - Math.PI/2;
    const rr = values[i]*r;
    const x = cx + Math.cos(angle)*rr;
    const y = cy + Math.sin(angle)*rr;
    const circ = document.createElementNS(svgNS,'circle');
    circ.setAttribute('cx', x); circ.setAttribute('cy', y); circ.setAttribute('r', 10);
    circ.setAttribute('fill','transparent');
    circ.style.cursor='pointer';
    circ.addEventListener('mouseenter', (ev)=>{
      tooltip.style.display='block';
      tooltip.textContent = `${lab}: ${Math.round(values[i]*100)}%`;
    });
    circ.addEventListener('mousemove', (ev)=>{
      tooltip.style.left = (ev.offsetX + 12) + 'px';
      tooltip.style.top = (ev.offsetY + 12) + 'px';
    });
    circ.addEventListener('mouseleave', ()=> tooltip.style.display='none');
    svg.appendChild(circ);
  });

  const legend = document.getElementById('tr-legend');
  if(legend){
    legend.innerHTML = '';
    labels.forEach((lab,i)=>{
      const el = document.createElement('div');
      el.className = 'tr-legend-item';
      el.style.display='inline-flex'; el.style.alignItems='center'; el.style.gap='8px'; el.style.marginRight='8px';
      el.innerHTML = `<span style="width:12px;height:12px;border-radius:3px;background: ${i%2? 'var(--nf-purple)':'var(--nf-teal)'};display:inline-block"></span><span style="color:var(--nf-muted);font-size:13px">${lab}</span>`;
      legend.appendChild(el);
    });
  }
}
