// Authentication utilities
function getToken() {
    return localStorage.getItem('token') || getCookie('auth_token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
    // We don't delete the cookie here as that's handled server-side
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

function getAuthHeaders() {
    const token = getToken();
    return {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
    };
}

function showError(message, elementId = 'error-message') {
    const errorDiv = document.getElementById(elementId);
    if (!errorDiv) {
        return;
    }
    const errorText = errorDiv.querySelector('.error-text');
    errorText.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.classList.add('visible');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
        errorDiv.classList.remove('visible');
    }, 5000);
}

function clearError(elementId = 'error-message') {
    const errorDiv = document.getElementById(elementId);
    if (!errorDiv) return;
    errorDiv.style.display = 'none';
    errorDiv.classList.remove('visible');
}

// Update UI based on authentication status
function updateAuthUI() {
    const token = getToken();
    const isLoggedIn = !!token;
    
    const loginLink = document.getElementById('login-link');
    const registerLink = document.getElementById('register-link');
    const logoutLink = document.getElementById('logout-link');
    
    if (loginLink) loginLink.style.display = isLoggedIn ? 'none' : 'block';
    if (registerLink) registerLink.style.display = isLoggedIn ? 'none' : 'block';
    if (logoutLink) logoutLink.style.display = isLoggedIn ? 'block' : 'none';
}

// Handle navigation with authentication
function handleNavigation(e) {
    e.preventDefault();
    const token = getToken();
    
    fetch(this.href, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.text();
        }
    })
    .then(html => {
        if (html) {
            document.open();
            document.write(html);
            document.close();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Initialize authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
    
    // Add auth headers to all navigation links
    document.querySelectorAll('.auth-link').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
    
    // Handle logout
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            removeToken();
            window.location.href = '/';
        });
    }
}); 