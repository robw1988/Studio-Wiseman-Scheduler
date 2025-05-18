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
        showLoginForm();
        return;
    }
    
    // Check authentication status on page load
    checkAuthStatus();
});

// Check if user is authenticated
function checkAuthStatus() {
    console.log('Checking authentication status...');
    
    // Force login form to show initially
    if (window.location.pathname === '/login') {
        console.log('On login page, showing login form');
        showLoginForm();
        return;
    }
    
    // Make a request to a protected endpoint
    fetch('/api/users/health')
        .then(response => {
            console.log('Auth check response status:', response.status);
            if (response.status === 401) {
                // User is not authenticated, show login form
                isAuthenticated = false;
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            isAuthenticated = true;
            return response.json();
        })
        .then(data => {
            // User is authenticated, hide login form and show main content
            console.log('User is authenticated:', data);
            hideLoginForm();
        })
        .catch(error => {
            if (error === 'Unauthorized') {
                // Already handled above
                console.log('User needs to log in');
                showLoginForm();
            } else {
                console.error('Error checking auth status:', error);
                // If there's any error, show the login form as a fallback
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
        isAuthenticated = true;
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
        // Set authenticated state to false
        isAuthenticated = false;
        // Redirect to login page with logout parameter
        window.location.href = '/?logout=true';
    })
    .catch(error => {
        console.error('Logout error:', error);
        // Even if there's an error, try to show the login form
        isAuthenticated = false;
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
        isAuthenticated = false;
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
                isAuthenticated = false;
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            return response;
        });
};
