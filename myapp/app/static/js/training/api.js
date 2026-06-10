const API = (function () {
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
    getTrainingPlan(week = 1) {
      return retry(() => timeoutFetch(`/api/training/plan?week=${encodeURIComponent(week)}`, { headers: headers() }).then(handleResponse));
    },
    listExercises() {
      return retry(() => timeoutFetch(`/api/exercises`, { headers: headers() }).then(handleResponse));
    },
    getExercise(id) {
      return retry(() => timeoutFetch(`/api/exercises/${encodeURIComponent(id)}`, { headers: headers() }).then(handleResponse));
    },
    listEquipment() {
      return retry(() => timeoutFetch(`/api/equipment`, { headers: headers() }).then(handleResponse));
    },
    listMuscles() {
      return retry(() => timeoutFetch(`/api/muscles`, { headers: headers() }).then(handleResponse));
    },
    getTrainingToday() {
      return retry(() => timeoutFetch(`/api/training/today`, { headers: headers() }).then(handleResponse));
    },
    getAnalytics() {
      return retry(() => timeoutFetch(`/api/training/analytics`, { headers: headers() }).then(handleResponse));
    },
    getRecommendations() {
      return retry(() => timeoutFetch(`/api/training/recommendations`, { headers: headers() }).then(handleResponse));
    },
    createSession(payload) {
      return retry(() => timeoutFetch(`/api/training/session/start`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(payload)
      }).then(handleResponse));
    },
    addExerciseToSession(sessionId, exerciseId, payload) {
      return retry(() => timeoutFetch(`/api/training/session/${encodeURIComponent(sessionId)}/exercise/${encodeURIComponent(exerciseId)}`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(payload)
      }).then(handleResponse));
    },
    finishSession(sessionId) {
      return retry(() => timeoutFetch(`/api/training/session/${encodeURIComponent(sessionId)}/finish`, {
        method: 'POST',
        headers: headers()
      }).then(handleResponse));
    },
    getSession(id) {
      return retry(() => timeoutFetch(`/api/session/${encodeURIComponent(id)}`, { headers: headers() }).then(handleResponse));
    },
    post(path, payload) {
      return retry(() => timeoutFetch(path, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(payload)
      }).then(handleResponse));
    },
    safe(fn) {
      return fn().catch(err => {
        console.warn('API safe error', err);
        return null;
      });
    }
  };
})();
