# JobPost Application Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Setup Instructions](#setup-instructions)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Install Python](#2-install-python)
    - [3. Create and Activate a Virtual Environment](#3-create-and-activate-a-virtual-environment)
    - [4. Install Dependencies](#4-install-dependencies)
    - [5. Configure Environment Variables](#5-configure-environment-variables)
5. [Azure Active Directory (Azure AD) Configuration](#azure-active-directory-azure-ad-configuration)
    - [a. Register the Application](#a-register-the-application)
    - [b. Configure Redirect URI](#b-configure-redirect-uri)
    - [c. Obtain Client ID, Client Secret, and Tenant ID](#c-obtain-client-id-client-secret-and-tenant-id)
    - [d. Set API Permissions](#d-set-api-permissions)
6. [Running the Application](#running-the-application)
7. [Application Structure](#application-structure)
8. [Usage](#usage)
    - [1. Accessing the Application](#1-accessing-the-application)
    - [2. Authentication Flow](#2-authentication-flow)
    - [3. Submitting a Job Post](#3-submitting-a-job-post)
    - [4. Handling Branded Ads](#4-handling-branded-ads)
9. [Email Processing](#email-processing)
    - [1. Sending Emails](#1-sending-emails)
    - [2. Receiving and Processing Emails](#2-receiving-and-processing-emails)
10. [Troubleshooting](#troubleshooting)
11. [Deployment](#deployment)
    - [1. Production Server Setup](#1-production-server-setup)
    - [2. Security Considerations](#2-security-considerations)
12. [Contributing](#contributing)
13. [License](#license)
14. [Contact](#contact)

---

## Introduction

**JobPost** is a Flask-based web application designed to streamline the job posting process for Jackson Hogg Ltd. It allows authorized users to submit job listings, generate branded advertisements, and manage ad templates efficiently. The application integrates with Azure Active Directory (Azure AD) for secure authentication and utilizes email functionalities to handle communication with the marketing team for branded ad requests.

---

## Features

- **Secure Authentication:** Utilizes Azure AD to ensure that only authorized users with `@jacksonhogg.com` email addresses can access the application.
- **Job Submission Form:** Allows users to submit job details, including job type, title, location, salary, and optional published client information.
- **Branded Ad Generation:** Users can opt to generate branded advertisements using existing templates or request new templates from the marketing team.
- **Automatic Template Management:** Processes incoming emails with new ad templates, automatically adding them to the available templates for selection.
- **Image Generation:** Uses Pillow to create customized images for job posts based on user inputs and selected templates.
- **Email Integration:** Sends confirmation emails with generated images and handles communication with the marketing team for branded ad requests.
- **Scheduled Tasks:** Employs APScheduler to periodically check for new incoming emails with ad templates.

---

## Prerequisites

Before setting up and running the JobPost application, ensure that your system meets the following requirements:

- **Operating System:** macOS, Linux, or Windows
- **Python:** Version 3.8 or higher
- **Package Manager:** `pip` (Python's package installer)
- **Azure Active Directory:** Access to Azure AD for application registration
- **Email Account:** Office 365 email account for sending and receiving emails

---

## Setup Instructions

Follow these steps to set up the JobPost application on your local machine.

### 1. Clone the Repository

First, clone the application's repository to your local machine.

```bash
git clone https://github.com/yourusername/jobpost.git
cd jobpost
```

*Replace `https://github.com/yourusername/jobpost.git` with the actual repository URL.*

### 2. Install Python

Ensure that Python 3.8 or higher is installed on your system.

**Check Python Installation:**

```bash
python3 --version
```

**Install Python (If Not Installed):**

- **macOS (Using Homebrew):**

  ```bash
  brew install python3
  ```

- **Ubuntu/Debian:**

  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```

- **Windows:**

  Download and install Python from the [official website](https://www.python.org/downloads/). Ensure that you check the box to add Python to your PATH during installation.

### 3. Create and Activate a Virtual Environment

Creating a virtual environment ensures that your project dependencies are isolated from the system-wide Python packages.

**Create Virtual Environment:**

```bash
python3 -m venv venv
```

**Activate Virtual Environment:**

- **macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

- **Windows:**

  ```cmd
  venv\Scripts\activate
  ```

*After activation, your terminal prompt should be prefixed with `(venv)`.*

### 4. Install Dependencies

With the virtual environment activated, install the required Python packages.

**Upgrade `pip`:**

```bash
pip install --upgrade pip
```

**Install Packages:**

```bash
pip install -r requirements.txt
```

*If you encounter the "externally-managed-environment" error, ensure that you are within the virtual environment and use `python -m pip` as follows:*

```bash
python -m pip install -r requirements.txt
```

---

## Azure Active Directory (Azure AD) Configuration

To enable secure authentication, the application integrates with Azure AD. Follow these steps to register your application and obtain the necessary credentials.

### a. Register the Application

1. **Sign In to Azure Portal:**

   Navigate to the [Azure Portal](https://portal.azure.com/) and sign in with your administrator credentials.

2. **Navigate to Azure Active Directory:**

   - In the left-hand navigation pane, select **"Azure Active Directory"**.

3. **App Registrations:**

   - Click on **"App registrations"** in the Azure AD menu.
   - Click **"New registration"**.

4. **Register Application:**

   - **Name:** Enter a descriptive name, e.g., `JobPostApp`.
   - **Supported Account Types:** Select **"Accounts in this organizational directory only"**.
   - **Redirect URI:** Select **"Web"** and enter `http://localhost:5858/getAToken`.
   - Click **"Register"**.

### b. Configure Redirect URI

1. **Navigate to Authentication Settings:**

   - After registration, go to the **"Authentication"** section.

2. **Add Redirect URI:**

   - Ensure that `http://localhost:5858/getAToken` is listed under **"Redirect URIs"**.
   - If not, add it and save the changes.

### c. Obtain Client ID, Client Secret, and Tenant ID

1. **Client ID:**

   - In the **"Overview"** section of your registered app, copy the **"Application (client) ID"**.

2. **Tenant ID:**

   - Also in the **"Overview"** section, copy the **"Directory (tenant) ID"**.

3. **Client Secret:**

   - Navigate to the **"Certificates & secrets"** section.
   - Under **"Client secrets"**, click **"New client secret"**.
   - **Description:** Enter a description, e.g., `JobPostAppSecret`.
   - **Expires:** Select an appropriate expiration period.
   - Click **"Add"**.
   - Copy the **"Value"** of the newly created client secret. **Note:** This value will not be shown again.

### d. Set API Permissions

1. **API Permissions:**

   - Go to the **"API permissions"** section.

2. **Add Permissions:**

   - Click **"Add a permission"**.
   - Select **"Microsoft Graph"**.
   - Choose **"Delegated permissions"**.
   - Search for and select **"User.Read"**.
   - Click **"Add permissions"**.

3. **Grant Admin Consent:**

   - If required, click **"Grant admin consent for [Your Tenant]"** to grant the necessary permissions.

---

## Configure Environment Variables

The application uses a `.env` file to manage sensitive configurations securely. Follow these steps to set up the environment variables.

### a. Locate/Create `.env` File

Ensure that a `.env` file exists in the root directory of your project. If it doesn't, create one.

```bash
cd /Users/jackroberts/Desktop/CustomApps/jobpost
nano .env
```

### b. Populate `.env` with Required Variables

Add the following variables to your `.env` file. Replace the placeholder values with your actual credentials.

```env
# Flask Configuration
SECRET_KEY=your_generated_flask_secret_key

# Azure AD Configuration
CLIENT_ID=your_application_client_id
CLIENT_SECRET=your_application_client_secret
TENANT_ID=your_actual_tenant_id

# Email Configuration
EMAIL_USERNAME=your_email@jacksonhogg.com
EMAIL_PASSWORD=your_email_password_or_app_password
MARKETING_EMAIL=marketing@jacksonhogg.com
```

**Descriptions:**

- **SECRET_KEY:**  
  A strong, random string used by Flask to secure sessions and cookies. You can generate one using Python:

  ```python
  import secrets
  secrets.token_urlsafe(32)
  ```

- **CLIENT_ID:**  
  The **Application (client) ID** obtained from Azure AD.

- **CLIENT_SECRET:**  
  The **Client Secret** generated in Azure AD.

- **TENANT_ID:**  
  The **Directory (tenant) ID** from Azure AD.

- **EMAIL_USERNAME:**  
  The email address used to send emails (e.g., `your_email@jacksonhogg.com`).

- **EMAIL_PASSWORD:**  
  The password or app-specific password for the email account.

- **MARKETING_EMAIL:**  
  The email address of the marketing team to receive ad requests (e.g., `marketing@jacksonhogg.com`).

### c. Save and Exit

If using `nano`, press `CTRL + O` to save and `CTRL + X` to exit.

### d. Secure the `.env` File

Ensure that the `.env` file is **excluded from version control** to protect sensitive information.

**Add to `.gitignore`:**

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

## Running the Application

With the virtual environment activated and dependencies installed, you can now run the Flask application.

### a. Activate the Virtual Environment (If Not Already Active)

```bash
source venv/bin/activate
```

*Your terminal prompt should display `(venv)`.*

### b. Start the Flask Application

```bash
python app.py
```

**Expected Output:**

```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5858
 * Running on http://192.168.5.4:5858
Press CTRL+C to quit
```

### c. Access the Application

Open your web browser and navigate to:

```
http://localhost:5858/
```

or

```
http://127.0.0.1:5858/
```

---

## Application Structure

Here's an overview of the application's directory structure:

```
jobpost/
├── app.py
├── requirements.txt
├── .env
├── templates/
│   └── index.html
├── static/
│   ├── fonts/
│   │   └── PTSans-Regular.ttf
│   └── BrandedAds/
│       ├── Existing_Template1.jpg
│       ├── Existing_Template2.jpg
│       └── ... (other templates)
└── venv/ (virtual environment directory, excluded from version control)
```

**Descriptions:**

- **app.py:**  
  The main Flask application file containing all route definitions and business logic.

- **requirements.txt:**  
  Lists all Python dependencies required by the application.

- **.env:**  
  Stores environment variables securely (excluded from version control).

- **templates/index.html:**  
  The HTML template for the job submission form.

- **static/fonts/PTSans-Regular.ttf:**  
  The TrueType font used for image generation.

- **static/BrandedAds/:**  
  Directory containing existing branded ad templates in `.jpg` format.

- **venv/:**  
  The virtual environment directory containing isolated Python packages (excluded from version control).

---

## Usage

### 1. Accessing the Application

Navigate to `http://localhost:5858/` in your web browser. If you're accessing it from another device on the same network, use `http://<your-ip-address>:5858/`.

### 2. Authentication Flow

1. **Login:**

   - Upon accessing the application, you'll be redirected to the Azure AD login page.
   - Log in using an `@jacksonhogg.com` email account.

2. **Authorization:**

   - After successful authentication, Azure AD redirects you back to the application.

3. **Access Form:**

   - Authenticated users are directed to the job submission form at `/form`.

### 3. Submitting a Job Post

1. **Fill Out the Form:**

   - **Your Email:** Automatically pre-filled with your authenticated email address.
   - **Job Type:** Select either "Permanent" or "Temporary".
   - **Job Title:** Enter the title of the job.
   - **Job Location:** Specify the location of the job.
   - **Job Salary:** Provide the salary details.
   - **Published Client (Optional):** If applicable, enter the client name.

2. **Branded Ad Option:**

   - **Do you want a branded ad?**  
     Choose "Yes" or "No".
     
   - **If "Yes":**
     - **Select a Branded Ad Template:**  
       Choose from existing templates or select "New Brand" to request a new template.

3. **Submit:**

   - Click the **"Submit"** button to process the form.

### 4. Handling Branded Ads

- **Using Existing Templates:**

  - If you select an existing template, the application generates an image based on your job details and the chosen template.
  - An email with the generated image is sent to the specified email address.

- **Requesting a New Template:**

  - Selecting "New Brand" sends an email to the marketing team with your job details.
  - The marketing team designs a new branded ad template and sends it as an attachment.
  - The application periodically checks for incoming emails from the marketing team and adds new templates automatically.

---

## Email Processing

The application handles sending and receiving emails to manage job postings and branded ad templates.

### 1. Sending Emails

- **Job Post Confirmation:**

  - After submitting a job post, the application sends an email to the specified address with the generated image attached.
  - If a branded ad is requested, the email includes a link to pre-fill the form for any necessary edits.

- **Branded Ad Requests:**

  - Selecting "New Brand" sends an email to the marketing team with the job details.
  - The marketing team is expected to reply with the new ad template attached.

### 2. Receiving and Processing Emails

- **Automatic Email Checking:**

  - The application uses **APScheduler** to schedule a task that runs every 5 minutes.
  - This task checks the inbox for new, unseen emails from the marketing team containing `.jpg` attachments.

- **Processing New Templates:**

  - When a new ad template is received, the application saves it in the `static/BrandedAds/` directory.
  - Filenames use underscores instead of spaces for consistency (e.g., `Brand_Name.jpg`).
  - The new template becomes available in the job submission form's dropdown menu with spaces in the display name (e.g., `Brand Name`).

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **Port 5000 is Already in Use**

- **Issue:**  
  Flask defaults to running on port 5000, which may be in use by another application.

- **Solution:**  
  Change the port number in `app.py` to an available port (e.g., 5858).

  ```python
  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5858)
  ```

#### 2. **Invalid Azure AD Tenant ID**

- **Issue:**  
  Authentication fails with an error indicating an invalid Tenant ID.

- **Solution:**  
  - Ensure that the `TENANT_ID` in your `.env` file is correct.
  - Verify the Tenant ID via the Azure Portal.
  - Confirm that the app registration has the correct permissions and credentials.

#### 3. **"externally-managed-environment" Error**

- **Issue:**  
  Encountered when attempting to install packages, indicating conflicts with system-managed Python environments.

- **Solution:**  
  - **Use a Virtual Environment:** Ensure you're working within a virtual environment.
  - **Recreate the Virtual Environment:** If the virtual environment is broken, delete and recreate it.
  - **Use `python -m pip`:** Install packages using `python -m pip` instead of `pip` directly.

#### 4. **Cannot Import `url_quote` from `werkzeug.urls`**

- **Issue:**  
  Compatibility issues between Flask and Werkzeug versions.

- **Solution:**  
  - **Upgrade Flask:** Ensure Flask is updated to the latest version compatible with your Werkzeug version.
  - **Pin Werkzeug Version:** Set Werkzeug to a version below 3.0.0 in `requirements.txt`.

#### 5. **Application Crashes on `/login` Route**

- **Issue:**  
  Errors occur when accessing the login route due to misconfigurations.

- **Solution:**  
  - **Verify `.env` Variables:** Ensure all necessary environment variables are correctly set.
  - **Check Azure AD Configuration:** Confirm that the app registration is correctly configured in Azure AD.

---

## Deployment

For production deployment, consider using a production-grade WSGI server and ensuring the application is secured properly.

### 1. Production Server Setup

- **Use a WSGI Server:**  
  Deploy the Flask application using a WSGI server like **Gunicorn** or **uWSGI**.

  **Example with Gunicorn:**

  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5858 app:app
  ```

  - **`-w 4`:** Number of worker processes.
  - **`-b 0.0.0.0:5858`:** Bind to all interfaces on port 5858.

- **Reverse Proxy:**  
  Set up a reverse proxy using **Nginx** or **Apache** to handle incoming requests, SSL termination, and load balancing.

### 2. Security Considerations

- **Enable HTTPS:**  
  Ensure that all communications are encrypted using SSL/TLS.

- **Secure Environment Variables:**  
  Use secure methods to manage environment variables in production, such as secret managers or environment variables set on the server.

- **Regular Updates:**  
  Keep all dependencies updated to the latest secure versions.

- **Firewall Configuration:**  
  Restrict access to necessary ports and services only.

---

## Contributing

Contributions are welcome! Follow these steps to contribute to the JobPost application.

### 1. Fork the Repository

- Click the **"Fork"** button on the repository's GitHub page to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/yourusername/jobpost.git
cd jobpost
```

### 3. Create a New Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes and Commit

```bash
# Make your changes in the codebase

git add .
git commit -m "Add your descriptive commit message"
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

- Navigate to your forked repository on GitHub.
- Click **"Compare & pull request"**.
- Provide a descriptive title and detailed description of your changes.
- Submit the pull request.

### 7. Address Feedback

- Collaborate with the maintainers to refine your contributions based on feedback.

---

## License

This project is licensed under the [MIT License](LICENSE).


---

## Appendix

### Additional Resources

- **Flask Documentation:**  
  [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)

- **MSAL for Python Documentation:**  
  [https://github.com/AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python)

- **Pillow Documentation:**  
  [https://pillow.readthedocs.io/](https://pillow.readthedocs.io/)

- **APScheduler Documentation:**  
  [https://apscheduler.readthedocs.io/](https://apscheduler.readthedocs.io/)

- **Python-dotenv Documentation:**  
  [https://saurabh-kumar.com/python-dotenv/](https://saurabh-kumar.com/python-dotenv/)

- **GitHub Guides:**  
  [https://guides.github.com/](https://guides.github.com/)

---

*This documentation provides a comprehensive guide to setting up, configuring, running, and maintaining the JobPost Flask application. Ensure that all sensitive information, such as client secrets and email passwords, are kept secure and not exposed in version control systems.*
