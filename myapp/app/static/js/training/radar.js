(function () {
  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function render(selectorOrEl, muscles) {
    const container = (typeof selectorOrEl === 'string') ? document.querySelector(selectorOrEl) : selectorOrEl;
    if (!container) return;
    const labels = Object.keys(muscles || {});
    const values = labels.map(l => Math.max(0, Math.min(1, muscles[l] || 0)));
    const size = Math.min(container.clientWidth || 320, 420);
    const svgNS = "http://www.w3.org/2000/svg";
    container.innerHTML = '';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
    const cx = size / 2, cy = size / 2, r = size * 0.36;
    for (let i = 4; i >= 1; i--) {
      const c = document.createElementNS(svgNS, 'circle');
      c.setAttribute('cx', cx); c.setAttribute('cy', cy); c.setAttribute('r', (r / 4) * i);
      c.setAttribute('class', 'tr-radar-grid');
      c.setAttribute('fill', 'none');
      c.setAttribute('stroke', 'rgba(255,255,255,0.03)');
      c.setAttribute('stroke-width', '1');
      svg.appendChild(c);
    }
    const n = Math.max(labels.length, 6);
    labels.forEach((lab, i) => {
      const angle = (Math.PI * 2) * (i / n) - Math.PI / 2;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      const line = document.createElementNS(svgNS, 'line');
      line.setAttribute('x1', cx); line.setAttribute('y1', cy);
      line.setAttribute('x2', x); line.setAttribute('y2', y);
      line.setAttribute('stroke', 'rgba(255,255,255,0.03)');
      line.setAttribute('stroke-width', '1');
      svg.appendChild(line);
      const tx = cx + Math.cos(angle) * (r + 18);
      const ty = cy + Math.sin(angle) * (r + 18);
      const text = document.createElementNS(svgNS, 'text');
      text.setAttribute('x', tx); text.setAttribute('y', ty);
      text.setAttribute('fill', '#e9e9ef');
      text.setAttribute('font-size', '11');
      text.setAttribute('text-anchor', Math.cos(angle) > 0.1 ? 'start' : Math.cos(angle) < -0.1 ? 'end' : 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.textContent = lab;
      svg.appendChild(text);
    });
    const points = values.map((v, i) => {
      const angle = (Math.PI * 2) * (i / n) - Math.PI / 2;
      const rr = v * r;
      return `${cx + Math.cos(angle) * rr},${cy + Math.sin(angle) * rr}`;
    }).join(' ');
    const poly = document.createElementNS(svgNS, 'polygon');
    poly.setAttribute('points', points);
    poly.setAttribute('class', 'tr-radar-polygon');
    svg.appendChild(poly);
    values.forEach((v, i) => {
      const angle = (Math.PI * 2) * (i / n) - Math.PI / 2;
      const rr = v * r;
      const x = cx + Math.cos(angle) * rr;
      const y = cy + Math.sin(angle) * rr;
      const p = document.createElementNS(svgNS, 'circle');
      p.setAttribute('cx', x); p.setAttribute('cy', y); p.setAttribute('r', 8);
      p.setAttribute('class', 'tr-radar-point');
      p.setAttribute('fill', 'transparent');
      p.style.cursor = 'pointer';
      p.addEventListener('mouseenter', (ev) => {
        showTooltip(container, ev, `${labels[i]}: ${Math.round((v||0)*100)}%`);
      });
      p.addEventListener('mousemove', (ev) => {
        moveTooltip(container, ev);
      });
      p.addEventListener('mouseleave', () => {
        hideTooltip(container);
      });
      svg.appendChild(p);
    });
    container.appendChild(svg);
    const legend = container.parentElement.querySelector('#tr-legend');
    if (legend) {
      legend.innerHTML = '';
      labels.forEach((lab, i) => {
        const el = document.createElement('div');
        el.className = 'tr-legend-item';
        el.dataset.index = i;
        el.innerHTML = `<span class="tr-legend-swatch ${i%3===0?'yellow':i%3===1?'purple':'teal'}"></span><span class="tr-legend-label">${lab}</span>`;
        el.addEventListener('click', () => {
          const active = el.dataset.active === 'true';
          el.dataset.active = active ? 'false' : 'true';
        });
        legend.appendChild(el);
      });
    }
  }

  function showTooltip(container, ev, text) {
    let tt = container._radarTooltip;
    if (!tt) {
      tt = document.createElement('div');
      tt.className = 'tr-radar-tooltip';
      document.body.appendChild(tt);
      container._radarTooltip = tt;
    }
    tt.innerHTML = `<div class="tr-tooltip-body">${text}</div>`;
    tt.classList.add('show');
    moveTooltip(container, ev);
  }
  function moveTooltip(container, ev) {
    const tt = container._radarTooltip;
    if (!tt) return;
    const left = ev.clientX + 12;
    const top = ev.clientY + 12;
    tt.style.left = left + 'px';
    tt.style.top = top + 'px';
  }
  function hideTooltip(container) {
    const tt = container._radarTooltip;
    if (!tt) return;
    tt.classList.remove('show');
  }

  window.NosiRadar = { render };
})();
