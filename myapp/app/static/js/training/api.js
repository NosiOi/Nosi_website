const API = (function () {
  let DETECTED_BASE = null;
  const CANDIDATE_BASES = ['/api/training', '/api', '/api/v1', ''];
  const DEFAULT_TIMEOUT = 10000;

  function headers() {
    const h = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('token');
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
  }

  function timeoutFetch(url, opts = {}, ms = DEFAULT_TIMEOUT) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('timeout')), ms);
      fetch(url, opts).then(r => {
        clearTimeout(timer);
        resolve(r);
      }).catch(err => {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  async function handleResponse(res) {
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      const err = new Error(`${res.status} ${res.statusText}`);
      err.body = text;
      throw err;
    }
    if (res.status === 204) return null;
    try {
      return await res.json();
    } catch {
      return null;
    }
  }

  async function retry(fn, attempts = 2, backoff = 300) {
    let lastErr;
    for (let i = 0; i <= attempts; i++) {
      try {
        return await fn();
      } catch (e) {
        lastErr = e;
        await new Promise(r => setTimeout(r, backoff * (i + 1)));
      }
    }
    throw lastErr;
  }

  async function detectBase() {
    if (DETECTED_BASE !== null) return DETECTED_BASE;
    for (const base of CANDIDATE_BASES) {
      try {
        const url = (base ? `${base}/plans` : '/plans');
        const res = await fetch(url, { method: 'OPTIONS', headers: headers() }).catch(() => null);
        if (res && (res.ok || res.status === 405 || res.status === 200 || res.status === 204)) {
          DETECTED_BASE = base;
          return DETECTED_BASE;
        }
      } catch (e) {}
    }
    DETECTED_BASE = '/api'; 
    return DETECTED_BASE;
  }

  async function buildUrl(path) {
    const base = await detectBase();
    if (!path) return base || '';
    if (path.startsWith('/')) return (base ? base + path : path);
    return (base ? base + '/' + path : '/' + path);
  }

  return {
    listPlans() {
      return retry(async () => {
        const url = await buildUrl('/plans');
        return timeoutFetch(url, { headers: headers() }).then(handleResponse);
      });
    },
    getPlan(id) {
      return retry(async () => {
        const url = await buildUrl(`/plans/${encodeURIComponent(id)}`);
        return timeoutFetch(url, { headers: headers() }).then(handleResponse);
      });
    },
    createSession(payload) {
      return retry(async () => {
        const url = await buildUrl('/sessions');
        return timeoutFetch(url, {
          method: 'POST',
          headers: headers(),
          body: JSON.stringify(payload)
        }).then(handleResponse);
      });
    },
    getSession(id) {
      return retry(async () => {
        const url = await buildUrl(`/sessions/${encodeURIComponent(id)}`);
        return timeoutFetch(url, { headers: headers() }).then(handleResponse);
      });
    },
    patchSession(id, payload) {
      return retry(async () => {
        const url = await buildUrl(`/sessions/${encodeURIComponent(id)}`);
        return timeoutFetch(url, {
          method: 'PATCH',
          headers: headers(),
          body: JSON.stringify(payload)
        }).then(handleResponse);
      });
    },
    listExercises() {
      return retry(async () => {
        const url = await buildUrl('/exercises');
        return timeoutFetch(url, { headers: headers() }).then(handleResponse);
      });
    },
    post(path, payload) {
      return retry(async () => {
        const url = path.startsWith('/') ? path : await buildUrl(path);
        return timeoutFetch(url, {
          method: 'POST',
          headers: headers(),
          body: JSON.stringify(payload)
        }).then(handleResponse);
      });
    },
    safe(fn) {
      return fn().catch(err => {
        console.warn('API safe error', err);
        return null;
      });
    },
    detectBase
  };
})();
