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
    // Check if we're in a post-logout state
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('logout')) {
        console.log('Detected logout parameter, showing login form');
        showLoginForm();
        return;
    }
    
    // Force login form to show on initial page load if not authenticated in session
    if (!sessionStorage.getItem('authenticated')) {
        console.log('No authenticated session found, showing login form');
        showLoginForm();
        return;
    }
    
    // Make a request to a protected endpoint
    fetch('/api/users/health')
        .then(response => {
            if (response.status === 401) {
                // User is not authenticated, show login form
                console.log('Received 401 from health check, showing login form');
                sessionStorage.removeItem('authenticated');
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            
            // Check if response is JSON before parsing
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                console.error('Health check response is not JSON:', contentType);
                sessionStorage.removeItem('authenticated');
                showLoginForm();
                return Promise.reject('Invalid response format');
            }
        })
        .then(data => {
            // User is authenticated, hide login form and show main content
            console.log('Health check successful, user is authenticated');
            sessionStorage.setItem('authenticated', 'true');
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
                sessionStorage.removeItem('authenticated');
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
        console.log('Login successful');
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
    
    // Try POST first, then GET if POST fails
    fetch('/api/users/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
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
        console.log('Logout successful');
        completeLogout();
    })
    .catch(error => {
        console.error('Logout error:', error);
        // Try GET method as fallback
        fetch('/api/users/logout', { method: 'GET' })
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
    // Clear authentication state
    sessionStorage.removeItem('authenticated');
    
    // Show login form
    showLoginForm();
    
    // Reload page with logout parameter to ensure fresh state
    window.location.href = '/?logout=true';
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
                sessionStorage.removeItem('authenticated');
                showLoginForm();
                return Promise.reject('Unauthorized');
            }
            return response;
        });
};
