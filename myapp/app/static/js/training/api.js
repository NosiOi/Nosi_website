const API = (function () {
  const base = '/api/training';

  function handleResp(res) {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  }

  function authHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    return headers;
  }

  return {
    listPlans() {
      return fetch(`${base}/plans`, { headers: authHeaders() }).then(handleResp);
    },
    getPlan(id) {
      return fetch(`${base}/plans/${id}`, { headers: authHeaders() }).then(handleResp);
    },
    createSession(payload) {
      return fetch(`${base}/sessions`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(payload)
      }).then(handleResp);
    },
    getSession(id) {
      return fetch(`${base}/sessions/${id}`, { headers: authHeaders() }).then(handleResp);
    },
    patchSession(id, payload) {
      return fetch(`${base}/sessions/${id}`, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify(payload)
      }).then(handleResp);
    },
    listExercises() {
      return fetch('/api/exercises', { headers: authHeaders() }).then(handleResp);
    }
  };
})();
