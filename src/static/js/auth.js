// Authentication handling for Studio Wiseman Cabinetry Scheduler

// DOM elements
let loginForm;
let usernameInput;
let passwordInput;
let loginError;
let loginContainer;
let mainContent;

// Initialize authentication handling
document.addEventListener('DOMContentLoaded', function() {
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
    }
    
    // Add logout button event listener
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Check authentication status on page load
    checkAuthStatus();
});

// Check if user is authenticated
function checkAuthStatus() {
    console.log('Checking authentication status...');
    // Make a request to a protected endpoint
    fetch('/api/users/health')
        .then(response => {
            console.log('Auth check response:', response.status);
            if (response.status === 401) {
                // User is not authenticated, show login form
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
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
function handleLogout() {
    console.log('Logging out...');
    fetch('/api/users/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Logout failed');
        }
        return response.json();
    })
    .then(data => {
        console.log('Logout successful:', data);
        // Show login form and reload page
        showLoginForm();
        window.location.reload();
    })
    .catch(error => {
        console.error('Logout error:', error);
        // Even if there's an error, try to show the login form
        showLoginForm();
        window.location.reload();
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
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            return response;
        });
};
