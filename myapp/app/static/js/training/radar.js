(function () {
  const I18N = {
    tooltip: (label, v) => `${label}: ${Math.round((v || 0) * 100)}%`,
    ariaLabel: 'Радарна діаграма навантаження',
    legendToggleOn: 'Включено',
    legendToggleOff: 'Вимкнено'
  };

  function debounce(fn, ms = 150) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  }

  function createSVG(ns, tag, attrs = {}) {
    const el = document.createElementNS(ns, tag);
    for (const k in attrs) {
      el.setAttribute(k, attrs[k]);
    }
    return el;
  }

  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

  function render(target, muscles = {}, opts = {}) {
    const container = typeof target === 'string' ? document.querySelector(target) : target;
    if (!container) return;
    const labels = Object.keys(muscles || {});
    const values = labels.map(l => Math.max(0, Math.min(1, muscles[l] || 0)));
    const size = Math.min(container.clientWidth || 320, opts.maxSize || 520);
    const svgNS = 'http://www.w3.org/2000/svg';
    container.innerHTML = '';
    const svg = createSVG(svgNS, 'svg', { width: size, height: size, viewBox: `0 0 ${size} ${size}`, role: 'img', 'aria-label': opts.ariaLabel || I18N.ariaLabel });
    const cx = size / 2, cy = size / 2, r = size * 0.36;

    const defs = createSVG(svgNS, 'defs');
    const grad = createSVG(svgNS, 'linearGradient', { id: 'radarGrad', x1: '0%', x2: '100%' });
    const stop1 = createSVG(svgNS, 'stop', { offset: '0%', 'stop-color': 'rgba(255,255,255,0.04)' });
    const stop2 = createSVG(svgNS, 'stop', { offset: '100%', 'stop-color': 'rgba(255,255,255,0.02)' });
    grad.appendChild(stop1); grad.appendChild(stop2); defs.appendChild(grad); svg.appendChild(defs);

    for (let i = 4; i >= 1; i--) {
      const c = createSVG(svgNS, 'circle', { cx, cy, r: (r / 4) * i });
      c.classList.add('tr-radar-grid');
      c.setAttribute('fill', 'none');
      c.setAttribute('stroke', 'rgba(255,255,255,0.03)');
      c.setAttribute('stroke-width', '1');
      svg.appendChild(c);
    }

    const n = Math.max(labels.length, 6);
    const angleStep = (Math.PI * 2) / n;

    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      const line = createSVG(svgNS, 'line', { x1: cx, y1: cy, x2: x, y2: y });
      line.setAttribute('stroke', 'rgba(255,255,255,0.04)');
      line.setAttribute('stroke-width', '1');
      svg.appendChild(line);

      const lx = cx + Math.cos(angle) * (r + 18);
      const ly = cy + Math.sin(angle) * (r + 18);
      const label = createSVG(svgNS, 'text', { x: lx, y: ly, 'text-anchor': 'middle', 'dominant-baseline': 'middle' });
      label.classList.add('tr-radar-label');
      label.textContent = labels[i] || '';
      svg.appendChild(label);
    }

    const poly = createSVG(svgNS, 'polygon');
    poly.classList.add('tr-radar-polygon');
    poly.setAttribute('fill', opts.fill || 'url(#radarGrad)');
    poly.setAttribute('stroke', opts.stroke || 'rgba(255,255,255,0.12)');
    poly.setAttribute('stroke-width', '2');
    poly.setAttribute('opacity', '0.98');
    svg.appendChild(poly);

    const points = [];
    const pointEls = [];
    for (let i = 0; i < n; i++) {
      const p = createSVG(svgNS, 'circle', { r: Math.max(6, size * 0.02) });
      p.classList.add('tr-radar-point');
      p.setAttribute('fill', 'transparent');
      p.style.cursor = 'pointer';
      svg.appendChild(p);
      pointEls.push(p);
    }

    container.appendChild(svg);

    const legend = container.parentElement ? container.parentElement.querySelector('#tr-legend') : null;
    if (legend) {
      legend.innerHTML = '';
      labels.forEach((lab, i) => {
        const item = document.createElement('div');
        item.className = 'tr-legend-item';
        item.dataset.index = i;
        item.dataset.active = 'true';
        const sw = document.createElement('span');
        sw.className = `tr-legend-swatch ${i % 3 === 0 ? 'yellow' : i % 3 === 1 ? 'purple' : 'teal'}`;
        const lbl = document.createElement('span');
        lbl.className = 'tr-legend-label';
        lbl.textContent = lab;
        item.appendChild(sw);
        item.appendChild(lbl);
        item.addEventListener('click', () => {
          const active = item.dataset.active === 'true';
          item.dataset.active = active ? 'false' : 'true';
          item.classList.toggle('is-muted', active);
          const p = pointEls[i];
          if (p) p.style.opacity = active ? '0.12' : '1';
          const svgLabel = svg.querySelectorAll('.tr-radar-label')[i];
          if (svgLabel) svgLabel.style.opacity = active ? '0.35' : '1';
        });
        legend.appendChild(item);
      });
    }

    const startVals = new Array(n).fill(0);
    const targetVals = values.slice();
    const duration = opts.duration || 600;
    const t0 = performance.now();

    function animate(now) {
      const t = Math.min(1, (now - t0) / duration);
      const e = easeOutCubic(t);
      const pts = [];
      for (let i = 0; i < n; i++) {
        const v = startVals[i] + (targetVals[i] - startVals[i]) * e;
        const angle = -Math.PI / 2 + i * angleStep;
        const x = cx + Math.cos(angle) * r * v;
        const y = cy + Math.sin(angle) * r * v;
        pts.push(`${x},${y}`);
        const pEl = pointEls[i];
        if (pEl) { pEl.setAttribute('cx', x); pEl.setAttribute('cy', y); }
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
        el.addEventListener('mouseenter', ev => showTooltip(ev, I18N.tooltip(lab || '', values[idx] || 0)));
        el.addEventListener('mousemove', ev => moveTooltip(ev));
        el.addEventListener('mouseleave', hideTooltip);
        el.addEventListener('focus', ev => showTooltip(ev, I18N.tooltip(lab || '', values[idx] || 0)));
        el.addEventListener('blur', hideTooltip);
        el.setAttribute('tabindex', '0');
        el.setAttribute('aria-label', `${lab} ${Math.round((values[idx] || 0) * 100)}%`);
      })(labels[i] || '', i);
    }

    if (!container._radarResizeHandler) {
      container._radarResizeHandler = debounce(() => render(container, muscles, opts), 200);
      window.addEventListener('resize', container._radarResizeHandler);
    }

    container._lastRadar = { labels, values, size };
  }

  window.NosiRadar = { render };
})();
