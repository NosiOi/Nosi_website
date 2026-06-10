const API = (function () {
  const base = '/api';

  async function handleResponse(res) {
    const text = await res.text();
    let body = null;
    try { body = text ? JSON.parse(text) : null; } catch (e) { body = text; }
    if (!res.ok) {
      const err = new Error((body && body.message) || res.statusText || 'API error');
      err.status = res.status;
      err.body = body;
      throw err;
    }
    return body;
  }

  function fetchJson(path, opts = {}) {
    const cfg = Object.assign({ credentials: 'same-origin', headers: { 'Accept': 'application/json' } }, opts);
    if (cfg.body && typeof cfg.body === 'object' && !(cfg.body instanceof FormData)) {
      cfg.headers['Content-Type'] = 'application/json';
      cfg.body = JSON.stringify(cfg.body);
    }
    return fetch(base + path, cfg).then(handleResponse);
  }

  return {
    listMuscles() { return fetchJson('/muscles'); },
    listEquipment() { return fetchJson('/equipment'); },
    listExercises(params = {}) {
      const qs = new URLSearchParams();
      Object.keys(params).forEach(k => { if (params[k] != null && params[k] !== '') qs.set(k, params[k]); });
      const path = '/exercises' + (qs.toString() ? `?${qs.toString()}` : '');
      return fetchJson(path);
    },
    getExercise(id) { return fetchJson(`/exercises/${id}`); },
    getTrainingToday() { return fetchJson('/training/today'); },
    getSession(id) { return fetchJson(`/session/${id}`); },
    createPlan(payload) { return fetchJson('/plans', { method: 'POST', body: payload }); },
    getUserPreferences() { return fetchJson('/user/preferences'); },
    saveUserPreferences(payload) { return fetchJson('/user/preferences', { method: 'POST', body: payload }); }
  };
})();
