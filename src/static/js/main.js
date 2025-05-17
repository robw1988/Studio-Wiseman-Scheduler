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
    checkAuthStatus();
    
    // Set up navigation event listeners
    setupNavigation();
    
    // Load initial view (dashboard)
    loadDashboard();
});

// Authentication functions
function checkAuthStatus() {
    // This would check if user is logged in
    // For prototype, we'll assume user is logged in
    console.log('User authenticated');
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
    // This would make an API call to get dashboard summary
    // For prototype, we'll use mock data
    const summaryData = {
        active_jobs: 12,
        pending_quotes: 8,
        upcoming_payment_total: 24500,
        clients_needing_updates: 5
    };
    
    updateDashboardSummary(summaryData);
}

function updateDashboardSummary(data) {
    // Update dashboard summary cards
    document.getElementById('active-jobs-count').textContent = data.active_jobs;
    document.getElementById('pending-quotes-count').textContent = data.pending_quotes;
    document.getElementById('upcoming-payments-amount').textContent = `£${data.upcoming_payment_total}`;
    document.getElementById('clients-updates-count').textContent = data.clients_needing_updates;
}

function fetchWeeklyCalendar() {
    // This would make an API call to get weekly calendar data
    // For prototype, we'll use mock data
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
        },
        // More calendar events would be here
    ];
    
    updateWeeklyCalendar(calendarData);
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
    // This would make an API call to get cashflow forecast
    // For prototype, we'll use mock data
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
        },
        // More months would be here
    ];
    
    updateCashflowForecast(forecastData);
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
    // This would make an API call to get income history
    // For prototype, we'll use mock data
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
    // This would make an API call to get current jobs
    // For prototype, we'll use mock data
    const jobsData = [
        {
            id: 1,
            name: 'Hampstead Kitchen',
            client_name: 'John Smith',
            stage: 'Build',
            build_start_date: '2025-05-19',
            fitting_date: '2025-05-26',
            status: 'On Track'
        },
        {
            id: 2,
            name: 'Chelsea Wardrobe',
            client_name: 'Emma Johnson',
            stage: 'Spray',
            build_start_date: '2025-05-12',
            fitting_date: '2025-05-22',
            status: 'Delayed'
        },
        // More jobs would be here
    ];
    
    updateCurrentJobs(jobsData);
}

function updateCurrentJobs(data) {
    // Update current jobs table
    const tableBody = document.querySelector('#current-jobs-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    data.forEach(job => {
        const row = document.createElement('tr');
        
        // Format dates
        const buildDate = new Date(job.build_start_date).toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        const fittingDate = new Date(job.fitting_date).toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        // Set status badge class
        let statusClass = 'bg-success';
        if (job.status === 'Delayed') statusClass = 'bg-warning';
        if (job.status === 'Issue') statusClass = 'bg-danger';
        if (job.status === 'Scheduled') statusClass = 'bg-info';
        
        row.innerHTML = `
            <td>${job.name}</td>
            <td>${job.client_name}</td>
            <td>${job.stage}</td>
            <td>${buildDate}</td>
            <td>${fittingDate}</td>
            <td><span class="badge ${statusClass} status-badge">${job.status}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Workshop Jobs functions
function loadJobs() {
    console.log('Loading jobs');
    
    // Fetch job data
    fetchJobs();
    
    // Fetch job schedule for Gantt view
    fetchJobSchedule();
    
    // Fetch weekly calendar
    fetchWeeklyCalendar();
}

function fetchJobs() {
    // This would make an API call to get all jobs
    // For prototype, we'll use mock data
    jobData = [
        {
            id: 1,
            name: 'Hampstead Kitchen',
            client_name: 'John Smith',
            stage: 'Build',
            build_start_date: '2025-05-19',
            build_team: ['James Wilson', 'Robert Johnson'],
            fitting_date: '2025-05-26',
            fit_team: ['William Davis'],
            status: 'On Track'
        },
        {
            id: 2,
            name: 'Chelsea Wardrobe',
            client_name: 'Emma Johnson',
            stage: 'Spray',
            build_start_date: '2025-05-12',
            build_team: ['Daniel Smith'],
            fitting_date: '2025-05-22',
            fit_team: ['William Davis'],
            status: 'Delayed'
        },
        // More jobs would be here
    ];
    
    updateJobsTable(jobData);
}

function updateJobsTable(data) {
    // Update jobs table
    const tableBody = document.querySelector('#jobs-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    data.forEach(job => {
        const row = document.createElement('tr');
        
        // Format dates
        const buildDate = new Date(job.build_start_date).toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        const fittingDate = new Date(job.fitting_date).toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        // Set status badge class
        let statusClass = 'bg-success';
        if (job.status === 'Delayed') statusClass = 'bg-warning';
        if (job.status === 'Issue') statusClass = 'bg-danger';
        if (job.status === 'Scheduled') statusClass = 'bg-info';
        
        row.innerHTML = `
            <td>${job.name}</td>
            <td>${job.client_name}</td>
            <td>${job.stage}</td>
            <td>${buildDate}</td>
            <td>${job.build_team.join(', ')}</td>
            <td>${fittingDate}</td>
            <td>${job.fit_team.join(', ')}</td>
            <td><span class="badge ${statusClass} status-badge">${job.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-job" data-job-id="${job.id}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary advance-job" data-job-id="${job.id}">
                    <i class="bi bi-arrow-right"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to buttons
    document.querySelectorAll('.edit-job').forEach(button => {
        button.addEventListener('click', function() {
            const jobId = this.getAttribute('data-job-id');
            editJob(jobId);
        });
    });
    
    document.querySelectorAll('.advance-job').forEach(button => {
        button.addEventListener('click', function() {
            const jobId = this.getAttribute('data-job-id');
            advanceJob(jobId);
        });
    });
}

function fetchJobSchedule() {
    // This would make an API call to get job schedule data for Gantt view
    // For prototype, we'll use mock data
    const scheduleData = [
        {
            id: 1,
            name: 'Hampstead Kitchen',
            client: 'John Smith',
            stages: [
                {
                    name: 'Build',
                    start: '2025-05-19',
                    end: '2025-05-25',
                    progress: 50
                },
                {
                    name: 'Spray',
                    start: '2025-05-24',
                    end: '2025-05-29',
                    progress: 0
                },
                {
                    name: 'Fit',
                    start: '2025-05-26',
                    end: '2025-05-29',
                    progress: 0
                }
            ]
        },
        // More jobs would be here
    ];
    
    updateGanttChart(scheduleData);
}

function updateGanttChart(data) {
    // This would update the Gantt chart
    // For prototype, we'll just log the data
    console.log('Gantt data loaded', data);
    
    // In a real implementation, this would create a dynamic Gantt chart
    // with drag-and-drop functionality for rescheduling
}

function editJob(jobId) {
    // Find the job in jobData
    const job = jobData.find(j => j.id == jobId);
    if (!job) return;
    
    // This would open a modal to edit the job
    console.log('Editing job', job);
    
    // In a real implementation, this would populate a form with job data
    // and allow the user to edit and save changes
}

function advanceJob(jobId) {
    // Find the job in jobData
    const job = jobData.find(j => j.id == jobId);
    if (!job) return;
    
    // This would advance the job to the next stage
    console.log('Advancing job', job);
    
    // In a real implementation, this would make an API call to update the job stage
    // and refresh the job data
}

// Quote Management functions
function loadQuotes() {
    console.log('Loading quotes');
    
    // Fetch quote data
    fetchQuotes();
}

function fetchQuotes() {
    // This would make an API call to get all quotes
    // For prototype, we'll use mock data
    quoteData = [
        {
            id: 1,
            name: 'Hampstead Kitchen',
            client_name: 'John Smith',
            cabinetry_type: 'Kitchen',
            initial_quote_amount: 25000,
            final_quote_amount: 24000,
            status: 'Accepted-Negotiated',
            has_job: true
        },
        {
            id: 2,
            name: 'Mayfair Wardrobe',
            client_name: 'David Taylor',
            cabinetry_type: 'Wardrobe',
            initial_quote_amount: 12000,
            final_quote_amount: null,
            status: 'Sent',
            has_job: false
        },
        // More quotes would be here
    ];
    
    updateQuotesTable(quoteData);
}

function updateQuotesTable(data) {
    // Update quotes table
    const tableBody = document.querySelector('#quotes-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    data.forEach(quote => {
        const row = document.createElement('tr');
        
        // Format amounts
        const initialAmount = `£${quote.initial_quote_amount}`;
        const finalAmount = quote.final_quote_amount ? `£${quote.final_quote_amount}` : '-';
        
        // Set status badge class
        let statusClass = 'bg-info';
        if (quote.status === 'Accepted' || quote.status === 'Accepted-Negotiated') statusClass = 'bg-success';
        if (quote.status === 'Rejected') statusClass = 'bg-danger';
        if (quote.status === 'Negotiating') statusClass = 'bg-warning';
        
        row.innerHTML = `
            <td>${quote.name}</td>
            <td>${quote.client_name}</td>
            <td>${quote.cabinetry_type}</td>
            <td>${initialAmount}</td>
            <td>${finalAmount}</td>
            <td><span class="badge ${statusClass} status-badge">${quote.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-quote" data-quote-id="${quote.id}">
                    <i class="bi bi-pencil"></i>
                </button>
                ${!quote.has_job && (quote.status === 'Accepted' || quote.status === 'Accepted-Negotiated') ? 
                    `<button class="btn btn-sm btn-outline-success convert-quote" data-quote-id="${quote.id}">
                        <i class="bi bi-arrow-right-circle"></i>
                    </button>` : ''}
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to buttons
    document.querySelectorAll('.edit-quote').forEach(button => {
        button.addEventListener('click', function() {
            const quoteId = this.getAttribute('data-quote-id');
            editQuote(quoteId);
        });
    });
    
    document.querySelectorAll('.convert-quote').forEach(button => {
        button.addEventListener('click', function() {
            const quoteId = this.getAttribute('data-quote-id');
            convertQuoteToJob(quoteId);
        });
    });
}

function editQuote(quoteId) {
    // Find the quote in quoteData
    const quote = quoteData.find(q => q.id == quoteId);
    if (!quote) return;
    
    // This would open a modal to edit the quote
    console.log('Editing quote', quote);
    
    // In a real implementation, this would populate a form with quote data
    // and allow the user to edit and save changes
}

function convertQuoteToJob(quoteId) {
    // Find the quote in quoteData
    const quote = quoteData.find(q => q.id == quoteId);
    if (!quote) return;
    
    // This would convert the quote to a job
    console.log('Converting quote to job', quote);
    
    // In a real implementation, this would make an API call to convert the quote
    // and refresh the quote data
}

// Initialize the application when the script loads
console.log('Cabinetry Scheduler frontend script loaded');
