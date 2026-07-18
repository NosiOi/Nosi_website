export const RecoveryAPI = {
    getSleep() {
        return fetch("/api/recovery/sleep").then(r => r.json());
    },
    saveSleep(data) {
        return fetch("/api/recovery/sleep", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }
};
