# Studio Wiseman Scheduler

A comprehensive scheduling system for bespoke cabinetry manufacturing businesses. This application helps manage the entire workflow from quotes to completed jobs, with features for workshop scheduling, staff management, client communication, and financial forecasting.

## Features

- **Quote Management**: Create and track quotes with extras, convert to jobs
- **Workshop Job Scheduling**: Gantt chart view and weekly calendar for job scheduling
- **Staff Management**: Track staff availability and assign to jobs
- **Client Management**: Track client information and communication
- **Financial Forecasting**: Track payments and forecast cashflow
- **Reporting**: Business intelligence dashboards and KPIs

## Deployment Instructions for Railway

### Prerequisites

1. A GitHub account
2. A Railway account (sign up at https://railway.app/)

### Step 1: Fork this Repository

1. Click the "Fork" button at the top right of this GitHub repository
2. This will create a copy of the repository in your GitHub account

### Step 2: Set Up Railway

1. Go to https://railway.app/ and log in
2. Click "New Project" on your dashboard
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if prompted
5. Select the forked "studio-wiseman-scheduler" repository
6. Railway will automatically detect the configuration and start the deployment

### Step 3: Add a Database

1. In your Railway project, click "New Service"
2. Select "Database" and then "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database

### Step 4: Connect the Database

1. Click on your web service (the one deployed from GitHub)
2. Go to the "Variables" tab
3. Railway should automatically add the `DATABASE_URL` variable
4. Add a new variable:
   - `SECRET_KEY`: Create a random string (e.g., "studio-wiseman-secret-key-12345")

### Step 5: Deploy

1. Railway will automatically deploy your application
2. Once deployment is complete, click on the web service
3. Go to the "Settings" tab
4. Find the "Domains" section to see your application URL

### Step 6: Initial Login

1. Navigate to your application URL
2. Log in with the default credentials:
   - Username: admin
   - Password: admin123
3. For security, change your password after first login

## Local Development

If you want to run the application locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `DATABASE_URL`: Your database connection string
   - `SECRET_KEY`: A random string for security
4. Run the application: `python -m src.main`

## User Guide

See the [User Guide](USER_GUIDE.md) for detailed instructions on using the system.

## Support

If you encounter any issues or have questions, please open an issue in this repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
