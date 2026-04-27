/**
 * Client-side API helper for Alpine.js components
 * Automatically handles auth tokens and common error cases
 */
const api = {
    /**
     * Get the base API URL from the global config
     */
    getBaseUrl() {
        return window.API_URL || '';
    },

    /**
     * Get auth token from cookies
     */
    getAuthToken() {
        const name = 'auth_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookies = decodedCookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length);
            }
        }
        return null;
    },

    /**
     * Build headers with auth token
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    },

    /**
     * Handle API errors
     */
    async handleResponse(response, skipAuthRedirect = false) {
        // If unauthorized, redirect to login (unless explicitly skipped)
        if (response.status === 401 && !skipAuthRedirect) {
            window.location.href = '/auth/login';
            return null;
        }

        // If no content, return null
        if (response.status === 204) {
            return null;
        }

        // Try to parse JSON
        const data = await response.json().catch(() => null);

        // If response not ok, throw error with message
        if (!response.ok) {
            throw new Error(data?.message || `API error: ${response.status}`);
        }

        return data;
    },

    /**
     * Make GET request
     */
    async get(endpoint, params = null) {
        const url = new URL(`${this.getBaseUrl()}${endpoint}`);
        if (params) {
            Object.keys(params).forEach(key =>
                url.searchParams.append(key, params[key])
            );
        }

        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders()
        });

        return this.handleResponse(response);
    },

    /**
     * Make POST request
     */
    async post(endpoint, data = {}, options = {}) {
        const response = await fetch(`${this.getBaseUrl()}${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response, options.skipAuthRedirect);
    },

    /**
     * Make PUT request
     */
    async put(endpoint, data = {}) {
        const response = await fetch(`${this.getBaseUrl()}${endpoint}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    },

    /**
     * Make PATCH request
     */
    async patch(endpoint, data = {}) {
        const response = await fetch(`${this.getBaseUrl()}${endpoint}`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    },

    /**
     * Make DELETE request
     */
    async delete(endpoint) {
        const response = await fetch(`${this.getBaseUrl()}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });

        return this.handleResponse(response);
    }
};