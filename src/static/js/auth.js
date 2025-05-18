// Authentication handling for Studio Wiseman Cabinetry Scheduler

// DOM elements
let loginForm;
let usernameInput;
let passwordInput;
let loginError;
let loginContainer;
let mainContent;
let isAuthenticated = false;

// Initialize authentication handling
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth.js initializing...');
    
    // Get DOM elements
    loginForm = document.getElementById('login-form');
    usernameInput = document.getElementById('username');
    passwordInput = document.getElementById('password');
    loginError = document.getElementById('login-error');
    loginContainer = document.getElementById('login-container');
    mainContent = document.getElementById('main-content');
    
    // Set up event listeners
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('Login form event listener attached');
    } else {
        console.error('Login form not found in DOM');
    }
    
    // Add logout button event listener
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
        console.log('Logout button event listener attached');
    } else {
        console.error('Logout button not found in DOM');
    }
    
    // Check if we're in a post-logout state
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('logout')) {
        console.log('Detected logout parameter, showing login form');
        sessionStorage.removeItem('authenticated');
        showLoginForm();
        return;
    }
    
    // Check authentication status on page load
    checkAuthStatus();
});

// Check if user is authenticated
function checkAuthStatus() {
    console.log('Checking authentication status...');
    
    // Force login form to show on initial page load if not authenticated in session
    if (!sessionStorage.getItem('authenticated')) {
        console.log('No authenticated session found, showing login form');
        showLoginForm();
        return;
    }
    
    // If we have a session, still verify with backend
    fetch('/api/users/health')
        .then(response => {
            console.log('Auth check response status:', response.status);
            if (response.status === 401) {
                // User is not authenticated, show login form
                sessionStorage.removeItem('authenticated');
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            return response.json();
        })
        .then(data => {
            // User is authenticated, hide login form and show main content
            console.log('User is authenticated:', data);
            sessionStorage.setItem('authenticated', 'true');
            hideLoginForm();
        })
        .catch(error => {
            if (error === 'Unauthorized') {
                // Already handled above
                console.log('User needs to log in');
                sessionStorage.removeItem('authenticated');
                showLoginForm();
            } else {
                console.error('Error checking auth status:', error);
                // If there's any error, show the login form as a fallback
                sessionStorage.removeItem('authenticated');
                showLoginForm();
            }
        });
}

// Handle login form submission
function handleLogin(event) {
    event.preventDefault();
    console.log('Login form submitted');
    
    // Get form values
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    // Validate form
    if (!username || !password) {
        showLoginError('Please enter both username and password');
        return;
    }
    
    // Clear previous errors
    hideLoginError();
    
    // Send login request
    fetch('/api/users/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        console.log('Login response status:', response.status);
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Login failed');
            });
        }
        return response.json();
    })
    .then(data => {
        // Login successful
        console.log('Login successful:', data);
        sessionStorage.setItem('authenticated', 'true');
        hideLoginForm();
        // Reload the page to initialize the authenticated session
        window.location.reload();
    })
    .catch(error => {
        console.error('Login error:', error);
        showLoginError(error.message);
    });
}

// Handle logout
function handleLogout(event) {
    if (event) {
        event.preventDefault();
    }
    
    console.log('Logging out...');
    sessionStorage.removeItem('authenticated');
    
    // Try both POST and GET methods for logout
    fetch('/api/users/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Logout response status:', response.status);
        if (!response.ok) {
            // If POST fails, try GET
            if (response.status === 405) {
                console.log('POST method not allowed, trying GET');
                return fetch('/api/users/logout');
            }
            throw new Error('Logout failed');
        }
        return response.json();
    })
    .then(data => {
        console.log('Logout successful:', data);
        // Redirect to login page with logout parameter
        window.location.href = '/?logout=true';
    })
    .catch(error => {
        console.error('Logout error:', error);
        // Even if there's an error, try to show the login form
        // Redirect to login page with logout parameter
        window.location.href = '/?logout=true';
    });
}

// Show login form
function showLoginForm() {
    console.log('Showing login form');
    if (loginContainer && mainContent) {
        loginContainer.style.display = 'block';
        mainContent.style.display = 'none';
    } else {
        console.error('Login container or main content not found');
        console.log('loginContainer:', loginContainer);
        console.log('mainContent:', mainContent);
    }
}

// Hide login form
function hideLoginForm() {
    console.log('Hiding login form');
    if (loginContainer && mainContent) {
        loginContainer.style.display = 'none';
        mainContent.style.display = 'block';
    } else {
        console.error('Login container or main content not found');
        console.log('loginContainer:', loginContainer);
        console.log('mainContent:', mainContent);
    }
}

// Show login error message
function showLoginError(message) {
    if (loginError) {
        loginError.textContent = message;
        loginError.style.display = 'block';
    }
}

// Hide login error message
function hideLoginError() {
    if (loginError) {
        loginError.textContent = '';
        loginError.style.display = 'none';
    }
}

// Handle unauthorized responses globally
function handleUnauthorizedResponse(response) {
    if (response.status === 401) {
        sessionStorage.removeItem('authenticated');
        showLoginForm();
        return Promise.reject('Unauthorized');
    }
    return response;
}

// Add global fetch interceptor for unauthorized responses
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    return originalFetch(url, options)
        .then(response => {
            if (response.status === 401) {
                console.log('Unauthorized response detected:', url);
                sessionStorage.removeItem('authenticated');
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            return response;
        });
};
