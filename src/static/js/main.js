// Main JavaScript file for connecting frontend to backend
// This will handle API calls and interactive features

// Global variables
let currentView = 'dashboard';
let jobData = [];
let quoteData = [];
let clientData = [];
let staffData = [];
let paymentData = [];

// Function to initialize the dashboard - made global for auth.js to call
window.initializeDashboard = function() {
    console.log('Initializing dashboard from window.initializeDashboard...');
    
    // Set up navigation event listeners
    setupNavigation();
    
    // Load initial view (dashboard)
    loadDashboard();
};

// Initialize Chart.js objects
document.addEventListener('DOMContentLoaded', function() {
    console.log('Main.js DOMContentLoaded event fired');
    
    // Initialize cashflow chart
    const cashflowCtx = document.getElementById('cashflow-chart');
    if (cashflowCtx) {
        window.cashflowChart = new Chart(cashflowCtx, {
            type: 'bar',
            data: {
                labels: ['May 2025', 'June 2025'],
                datasets: [{
                    label: 'Projected Income',
                    data: [32500, 45000],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Initialize income chart
    const incomeCtx = document.getElementById('income-chart');
    if (incomeCtx) {
        window.incomeChart = new Chart(incomeCtx, {
            type: 'pie',
            data: {
                labels: ['Deposits', 'Build', 'Fit', 'Completion'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.7)',
                        'rgba(25, 135, 84, 0.7)',
                        'rgba(13, 202, 240, 0.7)',
                        'rgba(255, 193, 7, 0.7)'
                    ],
                    borderColor: [
                        'rgba(13, 110, 253, 1)',
                        'rgba(25, 135, 84, 1)',
                        'rgba(13, 202, 240, 1)',
                        'rgba(255, 193, 7, 1)'
                    ],
                    borderWidth: 1
                }]
            }
        });
    }
    
    // Check if user is logged in
    if (checkAuthStatus()) {
        // Initialize dashboard directly if already authenticated
        window.initializeDashboard();
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
    console.log('Setting up navigation event listeners');
    
    // Add event listeners to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const view = this.getAttribute('data-view') || 'dashboard';
            console.log('Navigation clicked:', view);
            navigateTo(view);
        });
    });
    
    console.log('Navigation setup complete with', document.querySelectorAll('.nav-link').length, 'links');
}

function navigateTo(view) {
    console.log('Navigating to view:', view);
    
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
    fetch('/api/reports/dashboard-summary', {
        credentials: 'include' // Ensure cookies are sent with request
    })
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Dashboard summary API not implemented yet, using mock data');
                    return Promise.resolve({
                        active_jobs: 12,
                        pending_quotes: 8,
                        upcoming_payment_total: 24500,
                        clients_needing_updates: 5
                    });
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
    const activeJobsCount = document.getElementById('active-jobs-count');
    if (activeJobsCount) {
        activeJobsCount.textContent = data.active_jobs;
    }
    
    const pendingQuotesCount = document.getElementById('pending-quotes-count');
    if (pendingQuotesCount) {
        pendingQuotesCount.textContent = data.pending_quotes;
    }
    
    const upcomingPaymentsAmount = document.getElementById('upcoming-payments-amount');
    if (upcomingPaymentsAmount) {
        upcomingPaymentsAmount.textContent = `£${data.upcoming_payment_total}`;
    }
    
    const clientsUpdatesCount = document.getElementById('clients-updates-count');
    if (clientsUpdatesCount) {
        clientsUpdatesCount.textContent = data.clients_needing_updates;
    }
}

function fetchWeeklyCalendar() {
    // API call to get weekly calendar data
    fetch('/api/jobs/calendar/weekly', {
        credentials: 'include' // Ensure cookies are sent with request
    })
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Weekly calendar API not implemented yet, using mock data');
                    return Promise.resolve([
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
                    ]);
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
    fetch('/api/reports/cashflow-forecast', {
        credentials: 'include' // Ensure cookies are sent with request
    })
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Cashflow forecast API not implemented yet, using mock data');
                    return Promise.resolve([
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
                    ]);
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
    const currentMonthTotal = document.getElementById('current-month-total');
    if (currentMonthTotal) {
        currentMonthTotal.textContent = `£${currentMonth.total}`;
    }
    
    // Update progress bars with null checks
    const depositProgress = document.getElementById('deposit-progress');
    if (depositProgress) {
        depositProgress.style.width = `${currentMonth.deposit / currentMonth.total * 100}%`;
        depositProgress.textContent = `Deposits: £${currentMonth.deposit}`;
    }
    
    const buildProgress = document.getElementById('build-progress');
    if (buildProgress) {
        buildProgress.style.width = `${currentMonth.build / currentMonth.total * 100}%`;
        buildProgress.textContent = `Build: £${currentMonth.build}`;
    }
    
    const fitProgress = document.getElementById('fit-progress');
    if (fitProgress) {
        fitProgress.style.width = `${currentMonth.fit / currentMonth.total * 100}%`;
        fitProgress.textContent = `Fit: £${currentMonth.fit}`;
    }
    
    const completionProgress = document.getElementById('completion-progress');
    if (completionProgress) {
        completionProgress.style.width = `${currentMonth.completion / currentMonth.total * 100}%`;
        completionProgress.textContent = `Completion: £${currentMonth.completion}`;
    }
}

function fetchIncomeHistory() {
    // API call to get income history
    fetch('/api/reports/income-history', {
        credentials: 'include' // Ensure cookies are sent with request
    })
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Income history API not implemented yet, using mock data');
                    return Promise.resolve({
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
                    });
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
    // Update income chart
    if (window.incomeChart) {
        window.incomeChart.data.datasets[0].data = [
            data.percentages.deposit,
            data.percentages.build,
            data.percentages.fit,
            data.percentages.completion
        ];
        window.incomeChart.update();
    }
    
    // Update total income
    const totalIncome = document.getElementById('total-income');
    if (totalIncome) {
        totalIncome.textContent = `£${data.total_income}`;
    }
    
    // Update monthly breakdown table
    const incomeTable = document.getElementById('income-table');
    if (incomeTable && incomeTable.querySelector('tbody')) {
        const tbody = incomeTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        data.months.forEach(month => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${month.month}</td>
                <td>£${month.total}</td>
                <td>£${month.deposit}</td>
                <td>£${month.build}</td>
                <td>£${month.fit}</td>
                <td>£${month.completion}</td>
            `;
            tbody.appendChild(row);
        });
    }
}

function fetchCurrentJobs() {
    // API call to get current jobs
    fetch('/api/jobs/current', {
        credentials: 'include' // Ensure cookies are sent with request
    })
        .then(response => {
            if (!response.ok) {
                // If API endpoint doesn't exist yet, use mock data
                if (response.status === 404) {
                    console.warn('Current jobs API not implemented yet, using mock data');
                    return Promise.resolve([
                        {
                            job_id: 1,
                            job_name: 'Hampstead Kitchen',
                            client_name: 'John Smith',
                            stage: 'Build',
                            progress: 65,
                            deadline: '2025-06-15'
                        },
                        {
                            job_id: 2,
                            job_name: 'Chelsea Wardrobe',
                            client_name: 'Emma Johnson',
                            stage: 'Spray',
                            progress: 40,
                            deadline: '2025-06-01'
                        },
                        {
                            job_id: 3,
                            job_name: 'Kensington Bathroom',
                            client_name: 'Michael Brown',
                            stage: 'Design',
                            progress: 20,
                            deadline: '2025-07-10'
                        }
                    ]);
                }
                throw new Error('Failed to fetch current jobs');
            }
            return response.json();
        })
        .then(data => updateCurrentJobs(data))
        .catch(error => {
            console.error('Error fetching current jobs:', error);
            // Fallback to mock data on error
            const jobsData = [
                {
                    job_id: 1,
                    job_name: 'Hampstead Kitchen',
                    client_name: 'John Smith',
                    stage: 'Build',
                    progress: 65,
                    deadline: '2025-06-15'
                },
                {
                    job_id: 2,
                    job_name: 'Chelsea Wardrobe',
                    client_name: 'Emma Johnson',
                    stage: 'Spray',
                    progress: 40,
                    deadline: '2025-06-01'
                },
                {
                    job_id: 3,
                    job_name: 'Kensington Bathroom',
                    client_name: 'Michael Brown',
                    stage: 'Design',
                    progress: 20,
                    deadline: '2025-07-10'
                }
            ];
            updateCurrentJobs(jobsData);
        });
}

function updateCurrentJobs(data) {
    // Update current jobs table
    const jobsTable = document.getElementById('current-jobs-table');
    if (jobsTable && jobsTable.querySelector('tbody')) {
        const tbody = jobsTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        data.forEach(job => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${job.job_name}</td>
                <td>${job.client_name}</td>
                <td>${job.stage}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: ${job.progress}%;" aria-valuenow="${job.progress}" aria-valuemin="0" aria-valuemax="100">${job.progress}%</div>
                    </div>
                </td>
                <td>${job.deadline}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary view-job-btn" data-job-id="${job.job_id}">View</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Add event listeners to view buttons
        const viewButtons = tbody.querySelectorAll('.view-job-btn');
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const jobId = this.getAttribute('data-job-id');
                viewJob(jobId);
            });
        });
    }
}

function viewJob(jobId) {
    console.log('Viewing job:', jobId);
    // This would navigate to the job details page
    // For now, just log the action
}

// Placeholder functions for other views
function loadQuotes() {
    console.log('Loading quotes view');
    // This would load the quotes view
}

function loadJobs() {
    console.log('Loading jobs view');
    // This would load the jobs view
}

function loadClients() {
    console.log('Loading clients view');
    // This would load the clients view
}

function loadStaff() {
    console.log('Loading staff view');
    // This would load the staff view
}

function loadPayments() {
    console.log('Loading payments view');
    // This would load the payments view
}

function loadReports() {
    console.log('Loading reports view');
    // This would load the reports view
}
