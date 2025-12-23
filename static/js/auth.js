// static/js/auth.js - LOAD IN BASE.HTML
class JobPortalAuth {
    static async getAccessToken() {
        let token = localStorage.getItem('access_token');
        if (!token) return null;
        
        // Simple expiry check
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (payload.exp * 1000 < Date.now()) {
                token = await this.refreshToken();
            }
        } catch (e) {
            token = null;
        }
        return token;
    }
    
    static async apiCall(url, options = {}) {
        const token = await this.getAccessToken();
        if (!token) {
            window.location.href = '/login/';
            return;
        }
        
        options.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        const response = await fetch(url, options);
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login/';
        }
        return response;
    }
    
    static async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return null;
        
        const response = await fetch('/jobs/api/token/refresh/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const tokens = await response.json();
            localStorage.setItem('access_token', tokens.access);
            localStorage.setItem('refresh_token', tokens.refresh);
            return tokens.access;
        }
        return null;
    }
}

// USAGE: Simple everywhere!
const profile = await JobPortalAuth.apiCall('/jobs/api/profile/').then(r => r.json());
