(function () {
  'use strict';
  const I18N = {
    tooltip: (label, v) => `${label}: ${Math.round((v || 0) * 100)}%`,
    ariaLabel: 'Радарна діаграма навантаження',
    empty: 'Немає даних'
  };
  function qs(sel, root = document) { return (root || document).querySelector(sel); }
  function qsa(sel, root = document) { return Array.from((root || document).querySelectorAll(sel)); }
  function createSVG(ns, tag, attrs = {}) {
    const el = document.createElementNS(ns, tag);
    for (const k in attrs) {
      if (attrs[k] !== null && attrs[k] !== undefined) el.setAttribute(k, String(attrs[k]));
    }
    return el;
  }
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  function clamp(v, a = 0, b = 1) { return Math.max(a, Math.min(b, v)); }
  function normalizeMuscles(muscles) {
    if (!muscles || typeof muscles !== 'object') return {};
    const out = {};
    Object.keys(muscles).forEach(k => {
      const v = Number(muscles[k]);
      out[k] = Number.isFinite(v) ? clamp(v, 0, 1) : 0;
    });
    return out;
  }
  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }
  function render(selectorOrEl, muscles = {}, opts = {}) {
    const container = (typeof selectorOrEl === 'string') ? document.querySelector(selectorOrEl) : selectorOrEl;
    if (!container) return;
    const data = normalizeMuscles(muscles);
    const labels = Object.keys(data);
    const values = labels.map(l => data[l]);
    const svgNS = 'http://www.w3.org/2000/svg';
    clearChildren(container);
    const size = Math.min(Math.max(container.clientWidth || 320, 220), opts.maxSize || 520);
    const svg = createSVG(svgNS, 'svg', { width: size, height: size, viewBox: `0 0 ${size} ${size}`, role: 'img', 'aria-label': opts.ariaLabel || I18N.ariaLabel });
    svg.style.display = 'block';
    const cx = size / 2, cy = size / 2, r = Math.floor(size * 0.36);
    const defs = createSVG(svgNS, 'defs');
    svg.appendChild(defs);
    const gridGroup = createSVG(svgNS, 'g', { class: 'tr-radar-grid-group' });
    for (let i = 4; i >= 1; i--) {
      const ring = createSVG(svgNS, 'circle', { cx, cy, r: (r / 4) * i, class: 'tr-radar-grid grid-ring' });
      ring.setAttribute('fill', 'none');
      ring.setAttribute('stroke', 'rgba(255,255,255,0.03)');
      ring.setAttribute('stroke-width', '1');
      gridGroup.appendChild(ring);
    }
    svg.appendChild(gridGroup);
    const n = Math.max(labels.length, 6);
    const angleStep = (Math.PI * 2) / n;
    const axesGroup = createSVG(svgNS, 'g', { class: 'tr-radar-axes' });
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      const line = createSVG(svgNS, 'line', { x1: cx, y1: cy, x2: x, y2: y, class: 'axis-line' });
      line.setAttribute('stroke', 'rgba(255,255,255,0.03)');
      line.setAttribute('stroke-width', '1');
      axesGroup.appendChild(line);
      const lx = cx + Math.cos(angle) * (r + 18);
      const ly = cy + Math.sin(angle) * (r + 18);
      const label = createSVG(svgNS, 'text', { x: lx, y: ly, 'text-anchor': Math.abs(Math.cos(angle)) > 0.1 ? (Math.cos(angle) > 0 ? 'start' : 'end') : 'middle', 'dominant-baseline': 'middle', class: 'label-text' });
      label.textContent = labels[i] || '';
      axesGroup.appendChild(label);
    }
    svg.appendChild(axesGroup);
    const poly = createSVG(svgNS, 'polygon', { class: 'tr-radar-polygon' });
    poly.setAttribute('fill', opts.fill || 'rgba(255,255,255,0.04)');
    poly.setAttribute('stroke', opts.stroke || 'rgba(255,255,255,0.12)');
    poly.setAttribute('stroke-width', '2');
    poly.setAttribute('opacity', '0.98');
    svg.appendChild(poly);
    const pointsGroup = createSVG(svgNS, 'g', { class: 'tr-radar-points' });
    const pointEls = [];
    for (let i = 0; i < n; i++) {
      const p = createSVG(svgNS, 'circle', { r: Math.max(6, Math.round(size * 0.02)), class: 'tr-radar-point' });
      p.setAttribute('fill', 'transparent');
      p.style.cursor = 'pointer';
      p.setAttribute('data-index', i);
      pointsGroup.appendChild(p);
      pointEls.push(p);
    }
    svg.appendChild(pointsGroup);
    container.appendChild(svg);
    const legend = container.parentElement ? container.parentElement.querySelector('#tr-legend') : null;
    if (legend) {
      legend.innerHTML = '';
      labels.forEach((lab, i) => {
        const el = document.createElement('div');
        el.className = 'tr-legend-item';
        el.dataset.index = i;
        el.dataset.active = 'true';
        el.innerHTML = `<span class="tr-legend-swatch ${i % 3 === 0 ? 'yellow' : i % 3 === 1 ? 'purple' : 'teal'}"></span><span class="tr-legend-label">${lab}</span>`;
        el.addEventListener('click', () => {
          const active = el.dataset.active === 'true';
          el.dataset.active = active ? 'false' : 'true';
          el.classList.toggle('is-muted', active);
          const p = pointEls[i];
          if (p) p.style.opacity = active ? '0.18' : '1';
          const svgLabel = svg.querySelectorAll('.label-text')[i];
          if (svgLabel) svgLabel.style.opacity = active ? '0.35' : '1';
        });
        legend.appendChild(el);
      });
    }
    const startVals = new Array(n).fill(0);
    const targetVals = new Array(n).fill(0);
    for (let i = 0; i < n; i++) targetVals[i] = values[i] || 0;
    const duration = opts.duration || 700;
    const t0 = performance.now();
    function animate(now) {
      const t = Math.min(1, (now - t0) / duration);
      const e = easeOutCubic(t);
      const pts = [];
      for (let i = 0; i < n; i++) {
        const v = startVals[i] + (targetVals[i] - startVals[i]) * e;
        const angle = -Math.PI / 2 + i * angleStep;
        const rr = r * v;
        const x = cx + Math.cos(angle) * rr;
        const y = cy + Math.sin(angle) * rr;
        pts.push(`${x},${y}`);
        const pEl = pointEls[i];
        if (pEl) {
          pEl.setAttribute('cx', x);
          pEl.setAttribute('cy', y);
          pEl.setAttribute('r', Math.max(6, Math.round(size * 0.02) * (1 + 0.25 * v)));
          pEl.setAttribute('fill', (labels[i] ? (i % 3 === 0 ? 'var(--nf-yellow)' : i % 3 === 1 ? 'var(--nf-purple)' : 'var(--nf-teal)') : 'var(--nf-yellow)'));
          pEl.style.opacity = labels[i] ? '1' : '0.6';
        }
      }
      poly.setAttribute('points', pts.join(' '));
      if (t < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
    function showTooltip(ev, text) {
      let tt = container._radarTooltip;
      if (!tt) {
        tt = document.createElement('div');
        tt.className = 'tr-radar-tooltip';
        tt.setAttribute('role', 'status');
        document.body.appendChild(tt);
        container._radarTooltip = tt;
      }
      tt.innerHTML = `<div class="tr-tooltip-body">${text}</div>`;
      tt.classList.add('show');
      moveTooltip(ev);
    }
    function moveTooltip(ev) {
      const tt = container._radarTooltip;
      if (!tt) return;
      const left = Math.min(window.innerWidth - 220, ev.clientX + 12);
      const top = Math.min(window.innerHeight - 80, ev.clientY + 12);
      tt.style.left = `${left}px`;
      tt.style.top = `${top}px`;
    }
    function hideTooltip() {
      const tt = container._radarTooltip;
      if (!tt) return;
      tt.classList.remove('show');
    }
    for (let i = 0; i < pointEls.length; i++) {
      ((lab, idx) => {
        const el = pointEls[idx];
        el.addEventListener('mouseenter', ev => {
          const val = targetVals[idx] || 0;
          const label = labels[idx] || I18N.empty;
          showTooltip(ev, I18N.tooltip(label, val));
        });
        el.addEventListener('mousemove', ev => moveTooltip(ev));
        el.addEventListener('mouseleave', hideTooltip);
        el.addEventListener('focus', ev => {
          const val = targetVals[idx] || 0;
          const label = labels[idx] || I18N.empty;
          showTooltip(ev, I18N.tooltip(label, val));
        });
        el.addEventListener('blur', hideTooltip);
        el.setAttribute('tabindex', '0');
        el.setAttribute('aria-label', `${lab || I18N.empty} ${Math.round((targetVals[idx] || 0) * 100)}%`);
      })(labels[i] || '', i);
    }
    if (!container._radarResizeHandler) {
      container._radarResizeHandler = debounce(() => render(container, muscles, opts), 200);
      window.addEventListener('resize', container._radarResizeHandler);
    }
    container._lastRadar = { labels, values, size };
  }
  function debounce(fn, ms = 150) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
  window.NosiRadar = { render };
})();
