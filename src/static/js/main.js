// Main JavaScript file for connecting frontend to backend
// This will handle API calls and interactive features

// Global variables
let currentView = 'dashboard';
let jobData = [];
let quoteData = [];
let clientData = [];
let staffData = [];
let paymentData = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    if (checkAuthStatus()) {
        // Set up navigation event listeners
        setupNavigation();
        
        // Load initial view (dashboard)
        loadDashboard();
    } else {
        console.log('Authentication required before loading dashboard');
    }
});

// Authentication functions
// Note: Real authentication is now handled by auth.js
// This function is kept for compatibility but doesn't do authentication checks
function checkAuthStatus() {
    // Authentication is now handled by auth.js
    console.log('Authentication check delegated to auth.js');
    
    // We'll check if we're already in the login form state
    const loginContainer = document.getElementById('login-container');
    const mainContent = document.getElementById('main-content');
    
    // If login container is visible, don't proceed with loading dashboard
    if (loginContainer && mainContent) {
        if (loginContainer.style.display !== 'none') {
            console.log('Login required - dashboard loading paused');
            return false;
        }
    }
    
    return true;
}

function setupNavigation() {
    // Add event listeners to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const view = this.getAttribute('data-view') || 'dashboard';
            navigateTo(view);
        });
    });
}

function navigateTo(view) {
    // Update current view
    currentView = view;
    
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current nav link
    const activeLink = document.querySelector(`.nav-link[data-view="${view}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Load the appropriate view
    switch(view) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'quotes':
            loadQuotes();
            break;
        case 'jobs':
            loadJobs();
            break;
        case 'clients':
            loadClients();
            break;
        case 'staff':
            loadStaff();
            break;
        case 'payments':
            loadPayments();
            break;
        case 'reports':
            loadReports();
            break;
        default:
            loadDashboard();
    }
}

// Dashboard functions
function loadDashboard() {
    console.log('Loading dashboard');
    
    // Fetch dashboard summary data
    fetchDashboardSummary();
    
    // Fetch weekly calendar data
    fetchWeeklyCalendar();
    
    // Fetch cashflow forecast
    fetchCashflowForecast();
    
    // Fetch income history
    fetchIncomeHistory();
    
    // Fetch current workshop jobs
    fetchCurrentJobs();
}

function fetchDashboardSummary() {
    // API call to get dashboard summary
    fetch('/api/reports/dashboard-summary')
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Dashboard summary API not implemented yet, using mock data');
                    return {
                        active_jobs: 12,
                        pending_quotes: 8,
                        upcoming_payment_total: 24500,
                        clients_needing_updates: 5
                    };
                }
                throw new Error('Failed to fetch dashboard summary');
            }
            return response.json();
        })
        .then(data => updateDashboardSummary(data))
        .catch(error => {
            console.error('Error fetching dashboard summary:', error);
            // Fallback to mock data on error
            const summaryData = {
                active_jobs: 12,
                pending_quotes: 8,
                upcoming_payment_total: 24500,
                clients_needing_updates: 5
            };
            updateDashboardSummary(summaryData);
        });
}

function updateDashboardSummary(data) {
    // Update dashboard summary cards
    document.getElementById('active-jobs-count').textContent = data.active_jobs;
    document.getElementById('pending-quotes-count').textContent = data.pending_quotes;
    document.getElementById('upcoming-payments-amount').textContent = `£${data.upcoming_payment_total}`;
    document.getElementById('clients-updates-count').textContent = data.clients_needing_updates;
}

function fetchWeeklyCalendar() {
    // API call to get weekly calendar data
    fetch('/api/jobs/calendar/weekly')
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Weekly calendar API not implemented yet, using mock data');
                    return [
                        {
                            job_id: 1,
                            job_name: 'Hampstead Kitchen',
                            client_name: 'John Smith',
                            date: '2025-05-19',
                            stage: 'Build',
                            team: ['James Wilson', 'Robert Johnson']
                        },
                        {
                            job_id: 2,
                            job_name: 'Chelsea Wardrobe',
                            client_name: 'Emma Johnson',
                            date: '2025-05-19',
                            stage: 'Spray',
                            team: []
                        }
                    ];
                }
                throw new Error('Failed to fetch weekly calendar');
            }
            return response.json();
        })
        .then(data => updateWeeklyCalendar(data))
        .catch(error => {
            console.error('Error fetching weekly calendar:', error);
            // Fallback to mock data on error
            const calendarData = [
                {
                    job_id: 1,
                    job_name: 'Hampstead Kitchen',
                    client_name: 'John Smith',
                    date: '2025-05-19',
                    stage: 'Build',
                    team: ['James Wilson', 'Robert Johnson']
                },
                {
                    job_id: 2,
                    job_name: 'Chelsea Wardrobe',
                    client_name: 'Emma Johnson',
                    date: '2025-05-19',
                    stage: 'Spray',
                    team: []
                }
            ];
            updateWeeklyCalendar(calendarData);
        });
}

function updateWeeklyCalendar(data) {
    // Group events by date
    const eventsByDate = {};
    data.forEach(event => {
        if (!eventsByDate[event.date]) {
            eventsByDate[event.date] = [];
        }
        eventsByDate[event.date].push(event);
    });
    
    // Update calendar UI
    // This would populate the calendar grid with events
    console.log('Calendar data loaded', eventsByDate);
}

function fetchCashflowForecast() {
    // API call to get cashflow forecast
    fetch('/api/reports/cashflow-forecast')
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Cashflow forecast API not implemented yet, using mock data');
                    return [
                        {
                            month: 'May 2025',
                            total: 32500,
                            deposit: 16250,
                            build: 9750,
                            fit: 4875,
                            completion: 1625
                        },
                        {
                            month: 'June 2025',
                            total: 45000,
                            deposit: 22500,
                            build: 13500,
                            fit: 6750,
                            completion: 2250
                        }
                    ];
                }
                throw new Error('Failed to fetch cashflow forecast');
            }
            return response.json();
        })
        .then(data => updateCashflowForecast(data))
        .catch(error => {
            console.error('Error fetching cashflow forecast:', error);
            // Fallback to mock data on error
            const forecastData = [
                {
                    month: 'May 2025',
                    total: 32500,
                    deposit: 16250,
                    build: 9750,
                    fit: 4875,
                    completion: 1625
                },
                {
                    month: 'June 2025',
                    total: 45000,
                    deposit: 22500,
                    build: 13500,
                    fit: 6750,
                    completion: 2250
                }
            ];
            updateCashflowForecast(forecastData);
        });
}

function updateCashflowForecast(data) {
    // Update cashflow chart
    const labels = data.map(month => month.month);
    const values = data.map(month => month.total);
    
    // This would update the Chart.js chart
    if (window.cashflowChart) {
        window.cashflowChart.data.labels = labels;
        window.cashflowChart.data.datasets[0].data = values;
        window.cashflowChart.update();
    }
    
    // Update current month breakdown
    const currentMonth = data[0];
    document.getElementById('current-month-total').textContent = `£${currentMonth.total}`;
    
    // Update progress bars
    document.getElementById('deposit-progress').style.width = `${currentMonth.deposit / currentMonth.total * 100}%`;
    document.getElementById('deposit-progress').textContent = `Deposits: £${currentMonth.deposit}`;
    
    document.getElementById('build-progress').style.width = `${currentMonth.build / currentMonth.total * 100}%`;
    document.getElementById('build-progress').textContent = `Build: £${currentMonth.build}`;
    
    document.getElementById('fit-progress').style.width = `${currentMonth.fit / currentMonth.total * 100}%`;
    document.getElementById('fit-progress').textContent = `Fit: £${currentMonth.fit}`;
    
    document.getElementById('completion-progress').style.width = `${currentMonth.completion / currentMonth.total * 100}%`;
    document.getElementById('completion-progress').textContent = `Completion: £${currentMonth.completion}`;
}

function fetchIncomeHistory() {
    // API call to get income history
    fetch('/api/reports/income-history')
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Income history API not implemented yet, using mock data');
                    return {
                        months: [
                            {
                                month: 'February 2025',
                                total: 28000,
                                deposit: 14000,
                                build: 7000,
                                fit: 5600,
                                completion: 1400
                            },
                            {
                                month: 'March 2025',
                                total: 32000,
                                deposit: 16000,
                                build: 8000,
                                fit: 6400,
                                completion: 1600
                            },
                            {
                                month: 'April 2025',
                                total: 27500,
                                deposit: 13750,
                                build: 6875,
                                fit: 5500,
                                completion: 1375
                            }
                        ],
                        total_income: 87500,
                        percentages: {
                            deposit: 45,
                            build: 25,
                            fit: 20,
                            completion: 10
                        }
                    };
                }
                throw new Error('Failed to fetch income history');
            }
            return response.json();
        })
        .then(data => updateIncomeHistory(data))
        .catch(error => {
            console.error('Error fetching income history:', error);
            // Fallback to mock data on error
            const historyData = {
                months: [
                    {
                        month: 'February 2025',
                        total: 28000,
                        deposit: 14000,
                        build: 7000,
                        fit: 5600,
                        completion: 1400
                    },
                    {
                        month: 'March 2025',
                        total: 32000,
                        deposit: 16000,
                        build: 8000,
                        fit: 6400,
                        completion: 1600
                    },
                    {
                        month: 'April 2025',
                        total: 27500,
                        deposit: 13750,
                        build: 6875,
                        fit: 5500,
                        completion: 1375
                    }
                ],
                total_income: 87500,
                percentages: {
                    deposit: 45,
                    build: 25,
                    fit: 20,
                    completion: 10
                }
            };
            updateIncomeHistory(historyData);
        });
}

function updateIncomeHistory(data) {
    // Update income history chart
    const labels = ['Deposits', 'Build', 'Fit', 'Completion'];
    const values = [
        data.percentages.deposit,
        data.percentages.build,
        data.percentages.fit,
        data.percentages.completion
    ];
    
    // This would update the Chart.js chart
    if (window.incomeChart) {
        window.incomeChart.data.labels = labels;
        window.incomeChart.data.datasets[0].data = values;
        window.incomeChart.update();
    }
    
    // Update total
    document.getElementById('income-history-total').textContent = `£${data.total_income}`;
    
    // Update percentages
    document.getElementById('deposit-percentage').textContent = `Deposits: ${data.percentages.deposit}%`;
    document.getElementById('build-percentage').textContent = `Build: ${data.percentages.build}%`;
    document.getElementById('fit-percentage').textContent = `Fit: ${data.percentages.fit}%`;
    document.getElementById('completion-percentage').textContent = `Completion: ${data.percentages.completion}%`;
}

function fetchCurrentJobs() {
    // API call to get current jobs
    fetch('/api/jobs/current')
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Current jobs API not implemented yet, using mock data');
                    return [
                        {
                            id: 1,
                       
(Content truncated due to size limit. Use line ranges to read in chunks)
