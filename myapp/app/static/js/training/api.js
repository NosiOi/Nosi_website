const API = (function () {
  const BASE = '/api/training';
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

  return {
    listPlans() {
      return retry(() => timeoutFetch(`${BASE}/plans`, { headers: headers() }).then(handleResponse));
    },
    getPlan(id) {
      return retry(() => timeoutFetch(`${BASE}/plans/${encodeURIComponent(id)}`, { headers: headers() }).then(handleResponse));
    },
    createSession(payload) {
      return retry(() => timeoutFetch(`${BASE}/sessions`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(payload)
      }).then(handleResponse));
    },
    getSession(id) {
      return retry(() => timeoutFetch(`${BASE}/sessions/${encodeURIComponent(id)}`, { headers: headers() }).then(handleResponse));
    },
    patchSession(id, payload) {
      return retry(() => timeoutFetch(`${BASE}/sessions/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        headers: headers(),
        body: JSON.stringify(payload)
      }).then(handleResponse));
    },
    listExercises() {
      return retry(() => timeoutFetch('/api/exercises', { headers: headers() }).then(handleResponse));
    },
    post(path, payload) {
      return retry(() => timeoutFetch(path, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(payload)
      }).then(handleResponse));
    },
    //safe call that returns null on error
    safe(fn) {
      return fn().catch(err => {
        console.warn('API safe error', err);
        return null;
      });
    }
  };
})();
