// Authentication handling for Studio Wiseman Cabinetry Scheduler

// DOM elements
let loginForm;
let usernameInput;
let passwordInput;
let loginError;
let loginContainer;
let mainContent;
let logoutBtn;

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
    logoutBtn = document.getElementById('logout-btn');
    
    // Set up event listeners
    if (loginForm) {
        console.log('Login form event listener attached');
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Set up logout button if it exists
    if (logoutBtn) {
        console.log('Logout button event listener attached');
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Check authentication status on page load
    checkAuthStatus();
});

// Check if user is authenticated
function checkAuthStatus() {
    console.log('Checking authentication status...');
    
    // Make a request to a protected endpoint
    fetch('/api/users/health', {
        method: 'GET',
        credentials: 'include', // Important: include credentials (cookies) with request
        headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    })
    .then(response => {
        console.log('Auth status response:', response.status);
        if (response.status === 401) {
            // User is not authenticated, show login form
            console.log('Received 401 from health check, showing login form');
            showLoginForm();
            return Promise.reject('Unauthorized');
        }
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        } else {
            console.error('Health check response is not JSON:', contentType);
            showLoginForm();
            return Promise.reject('Invalid response format');
        }
    })
    .then(data => {
        // User is authenticated, hide login form and show main content
        console.log('Health check successful, user is authenticated:', data);
        hideLoginForm();
    })
    .catch(error => {
        if (error === 'Unauthorized') {
            // Already handled above
            console.log('User needs to log in');
        } else if (error === 'Invalid response format') {
            // Already handled above
            console.log('Invalid response format from health check');
        } else {
            console.error('Error checking auth status:', error);
            // Show login form on any error
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
    
    console.log('Attempting login...');
    
    // Send login request
    fetch('/api/users/login', {
        method: 'POST',
        credentials: 'include', // Important: include credentials (cookies) with request
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        console.log('Login response status:', response.status);
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data.error || 'Login failed');
                }
                return data;
            });
        } else {
            console.error('Login response is not JSON:', contentType);
            throw new Error('Server returned an invalid response format. Please try again later.');
        }
    })
    .then(data => {
        // Login successful
        console.log('Login successful:', data);
        
        // Don't reload the page - just hide login form and show main content
        hideLoginForm();
        
        // Initialize the dashboard
        if (typeof initializeDashboard === 'function') {
            console.log('Initializing dashboard...');
            initializeDashboard();
        } else {
            console.log('Dashboard initialization function not found, continuing...');
        }
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
    
    fetch('/api/users/logout', {
        method: 'POST',
        credentials: 'include', // Important: include credentials (cookies) with request
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    })
    .then(response => {
        console.log('Logout response status:', response.status);
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error('Logout failed');
                }
                return data;
            });
        } else if (response.ok) {
            // If response is not JSON but status is OK, still consider it successful
            return { message: 'Logout successful' };
        } else {
            throw new Error('Server returned an invalid response format');
        }
    })
    .then(data => {
        console.log('Logout successful:', data);
        completeLogout();
    })
    .catch(error => {
        console.error('Logout error:', error);
        // Try GET method as fallback
        fetch('/api/users/logout', {
            method: 'GET',
            credentials: 'include', // Important: include credentials (cookies) with request
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        })
        .then(() => {
            console.log('Logout successful via GET fallback');
            completeLogout();
        })
        .catch(fallbackError => {
            console.error('Fallback logout also failed:', fallbackError);
            // Still complete logout on client side even if server request fails
            completeLogout();
        });
    });
}

// Complete logout process
function completeLogout() {
    // Show login form
    showLoginForm();
    
    // Clear any form data
    if (loginForm) {
        loginForm.reset();
    }
    
    // Redirect to home page
    window.location.href = '/';
}

// Show login form
function showLoginForm() {
    if (loginContainer && mainContent) {
        loginContainer.style.display = 'block';
        mainContent.style.display = 'none';
    }
}

// Hide login form
function hideLoginForm() {
    if (loginContainer && mainContent) {
        loginContainer.style.display = 'none';
        mainContent.style.display = 'block';
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

// Add global fetch interceptor for unauthorized responses
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Ensure credentials are included in all requests
    const newOptions = {
        ...options,
        credentials: 'include'
    };
    
    return originalFetch(url, newOptions)
        .then(response => {
            if (response.status === 401) {
                console.log('Received 401 response from:', url);
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            return response;
        });
};
