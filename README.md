# **Project Documentation**

## **Table of Contents**

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Build and Run the Application](#3-build-and-run-the-application)
- [Application Components](#application-components)
  - [1. Bullhorn API Integration](#1-bullhorn-api-integration)
  - [2. Website Form Data Import](#2-website-form-data-import)
  - [3. Data Cross-Referencing](#3-data-cross-referencing)
  - [4. Dashboard](#4-dashboard)
  - [5. Reporting](#5-reporting)
  - [6. Scheduling and Background Tasks](#6-scheduling-and-background-tasks)
- [Database Setup](#database-setup)
- [Email Configuration](#email-configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)
- [License](#license)

---

## **Introduction**

This application is a Dockerized Python application designed to integrate with the Bullhorn recruitment software API and your website's job application and contact forms. It synchronizes data between Bullhorn and a local SQL database, cross-references applicants with placements, generates reports, displays a dashboard, and sends monthly email reports.

**Key Features:**

- **Bullhorn API Integration:** Sync candidates, contacts, vacancies, and placements data.
- **Website Data Import:** Import job applications and contact form submissions.
- **Data Cross-Referencing:** Identify candidates who applied through the website and were placed.
- **Dashboard:** Visualize data through a web interface.
- **Reporting:** Generate and email monthly reports with financial summaries.
- **Dockerized Deployment:** Use Docker and Docker Compose for easy setup and deployment.
- **Scheduling:** Utilize Celery and Redis for background tasks and scheduling.

---

## **Prerequisites**

Before setting up the application, ensure you have the following installed on your system:

- **Docker** (version 19.03 or higher)
- **Docker Compose** (version 1.25.0 or higher)
- **Git** (optional, for cloning the repository)

---

## **Project Structure**

The application has the following directory structure:

```
your_project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── utils.py
│   ├── tasks.py
│   ├── templates/
│   │   └── dashboard.html
│   └── static/
│
├── data/          # For persistent database storage
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

---

## **Installation**

### **1. Clone the Repository**

Open your terminal and navigate to the directory where you want to set up the project. Clone the repository:

```bash
git clone https://github.com/your_username/your_project.git
cd your_project
```

> **Note:** Replace `https://github.com/your_username/your_project.git` with the actual repository URL.

### **2. Configure Environment Variables**

Create a `.env` file in the root directory of your project to store environment-specific settings and sensitive information.

```bash
touch .env
```

Add the following content to the `.env` file:

```env
# Bullhorn API credentials
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USERNAME=your_bullhorn_username
PASSWORD=your_bullhorn_password

# Database credentials
DATABASE_URL=postgresql://your_db_user:your_db_password@db/your_db_name

# Email server settings
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password

# Security Key
SECRET_KEY=your_secret_key
```

**Replace the placeholder values with your actual credentials:**

- **Bullhorn API Credentials:** Obtain these from your Bullhorn account.
- **Database Credentials:** Ensure they match the settings in `docker-compose.yml`.
- **Email Server Settings:** Use your email provider's SMTP settings.
- **Secret Key:** Generate a random secret key for Flask sessions.

> **Important:** The `.env` file contains sensitive information. Do not commit this file to version control.

### **3. Build and Run the Application**

Use Docker Compose to build and start the application:

```bash
docker-compose up --build
```

This command performs the following:

- Builds the Docker images defined in `docker-compose.yml`.
- Starts the services:
  - **web:** The Flask application.
  - **db:** PostgreSQL database.
  - **redis:** Redis server for Celery.
  - **celery_worker:** Celery worker for background tasks.
  - **celery_beat:** Celery Beat for scheduling tasks.

---

## **Application Components**

### **1. Bullhorn API Integration**

The application connects to the Bullhorn API to retrieve data on candidates, contacts, vacancies, and placements.

- **Authentication:** Uses OAuth 2.0 to authenticate with Bullhorn.
- **Data Retrieval:** Fetches data and stores it in the local PostgreSQL database.
- **Periodic Updates:** Schedules regular updates to keep data in sync.

### **2. Website Form Data Import**

Imports job application and contact form submissions from your website:

- **Job Applications:** Stored as applicants in the database.
- **Contact Forms:** Stored and cross-referenced with vacancies.

**Data Sources:**

- **API Endpoint:** If your website provides an API.
- **Database Connection:** Directly connect to your website's database.
- **CSV/JSON Files:** Import data from exported files.

### **3. Data Cross-Referencing**

Cross-references imported applicants and contacts with Bullhorn data:

- **Applicants and Placements:**
  - Flags candidates who applied through your website and were placed.
  - Ensures the application was made no more than 9 months before the placement.
- **Contacts and Vacancies:**
  - Identifies clients who found you through the website.
  - Matches the company field in contact forms with vacancies.

### **4. Dashboard**

Provides a web-based dashboard to visualize data:

- **URL:** Access the dashboard at `http://localhost:5000`.
- **Features:**
  - List of applicants who were placed.
  - Individual placement values.
  - Total placement value per month.
  - Clients who contacted via the website leading to vacancies.
- **Templates:** Uses Flask templates in the `app/templates` directory.

### **5. Reporting**

Generates and sends monthly reports via email:

- **Content:**
  - Summary of placements and financials for the past month.
  - Detailed information on applicants and placements.
- **Scheduling:**
  - Automated to run on the 1st of every month.
  - Utilizes Celery Beat for scheduling.

### **6. Scheduling and Background Tasks**

Uses Celery and Redis for asynchronous tasks and scheduling:

- **Celery Worker:** Handles background tasks like data updates and email sending.
- **Celery Beat:** Schedules periodic tasks.
- **Tasks Defined In:** `app/tasks.py`.

**Scheduled Tasks:**

- **Data Updates:** Every hour.
- **Monthly Reports:** On the 1st of every month.

---

## **Database Setup**

The application uses PostgreSQL as the database:

- **Service Name:** `db` (as defined in `docker-compose.yml`).
- **Credentials:** Defined in both `.env` and `docker-compose.yml`.

**Database Initialization:**

Before running the application, ensure the database tables are created:

1. **Run Database Migrations:**

   - Install Flask-Migrate (already included in `requirements.txt`):

     ```bash
     docker-compose exec web flask db init
     docker-compose exec web flask db migrate
     docker-compose exec web flask db upgrade
     ```

2. **Alternative Method:**

   - Modify `app/__init__.py` to create tables on startup (not recommended for production):

     ```python
     with app.app_context():
         db.create_all()
     ```

---

## **Email Configuration**

The application sends emails using SMTP:

- **SMTP Settings:** Configured in the `.env` file.
- **Email Functionality:**
  - Sends monthly reports.
  - Can be extended to send alerts or notifications.

**Supported Email Providers:**

- **Gmail:** Requires app passwords and enabling less secure apps.
- **SendGrid, Mailgun, etc.:** Recommended for reliability and scalability.

**Email Sending Implementation:**

- **Uses:** `smtplib` or a third-party library.
- **Defined In:** `app/utils.py` or `app/tasks.py`.

---

## **Security Considerations**

- **Environment Variables:**
  - Store sensitive information in the `.env` file.
  - Do not commit the `.env` file to version control.
- **Database Security:**
  - Use strong passwords for database access.
  - Ensure the database is not exposed outside the Docker network.
- **API Credentials:**
  - Protect Bullhorn API credentials.
  - Rotate credentials periodically.
- **Email Credentials:**
  - Secure email account credentials.
  - Consider using an email API with tokens instead of raw passwords.
- **Secret Key:**
  - Set `SECRET_KEY` in the `.env` file for Flask sessions.
  - Use a secure, randomly generated string.

---

## **Troubleshooting**

### **Common Issues and Solutions**

1. **Docker Container Fails to Start:**

   - **Check Logs:**

     ```bash
     docker-compose logs web
     ```

   - **Possible Causes:**
     - Missing environment variables.
     - Port conflicts.
     - Dependency services not running.

2. **Database Connection Errors:**

   - **Solution:**
     - Verify database credentials in `.env` and `docker-compose.yml`.
     - Ensure the `db` service is running.

3. **Bullhorn API Authentication Fails:**

   - **Solution:**
     - Check Bullhorn API credentials.
     - Ensure network connectivity.
     - Handle token expiration and refresh logic.

4. **Emails Not Sending:**

   - **Solution:**
     - Verify SMTP settings.
     - Check email server logs.
     - Ensure less secure app access is enabled if using Gmail.

5. **Scheduled Tasks Not Running:**

   - **Solution:**
     - Ensure `celery_worker` and `celery_beat` services are running.
     - Check Celery logs:

       ```bash
       docker-compose logs celery_worker
       docker-compose logs celery_beat
       ```

6. **Data Not Updating:**

   - **Solution:**
     - Verify that the data update task is scheduled and running.
     - Manually trigger the task for testing.

     ```bash
     docker-compose exec web flask shell
     >>> from app.tasks import update_data_task
     >>> update_data_task.delay()
     ```

7. **Web Application Unresponsive:**

   - **Solution:**
     - Check the `web` service logs.
     - Ensure all migrations are applied.
     - Verify that the Flask app is running without errors.

---

## **Additional Notes**

### **Extending the Application**

- **Additional Features:**
  - Implement user authentication for the dashboard.
  - Add more detailed analytics and visualizations.
  - Integrate with other third-party services.

- **Scaling:**
  - Use orchestration tools like Kubernetes for large deployments.
  - Consider cloud-based solutions for hosting.

### **Development Tips**

- **Use a Virtual Environment:**
  - While Docker handles dependencies, you can set up a virtual environment for local development.

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

- **Testing:**
  - Write unit tests for critical functions.
  - Use testing frameworks like `pytest`.

- **Code Formatting:**
  - Follow PEP 8 style guidelines.
  - Use linters like `flake8`.

### **Logging and Monitoring**

- **Logging:**
  - Implement logging within the application using Python's `logging` module.
  - Configure log levels and handlers as needed.

- **Monitoring:**
  - Set up monitoring tools to track application performance.
  - Use services like Prometheus and Grafana for metrics.

### **Updating Dependencies**

- **Regularly Update Packages:**
  - Keep dependencies up to date to receive security patches.
  - Update `requirements.txt` as needed.

---

## **License**

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software as per the license terms.

---

## **Conclusion**

This documentation provides a comprehensive guide to setting up and running the application. By following the steps outlined, you should be able to integrate with Bullhorn, import and process data, and visualize results through the dashboard and reports.

If you encounter any issues or have suggestions for improvements, feel free to reach out or contribute to the project.

---

**Thank you for using this application!**
