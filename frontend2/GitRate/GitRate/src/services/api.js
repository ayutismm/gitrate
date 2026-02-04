const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
    async rateDeveloper(username) {
        const response = await fetch(`${API_BASE_URL}/rate/${username}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to rate developer');
        }
        return response.json();
    },

    async getUserData(username) {
        const response = await fetch(`${API_BASE_URL}/user/${username}/data`);
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        return response.json();
    },

    async healthCheck() {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            throw new Error('Health check failed');
        }
        return response.json();
    }
};
