# 🚀 HR Comply360 – Statutory Compliance Suite

> A centralized HR compliance management platform that helps organizations automate statutory compliance tracking, document management, deadline monitoring, and reminder notifications.



---

# 📌 Overview

Managing statutory compliance manually can be time-consuming and prone to missed deadlines. **HR Comply360** is a full-stack web application designed to streamline compliance management by centralizing statutory records, automating reminders, and providing real-time visibility into compliance status.

The system enables HR teams to:

* Track statutory compliance deadlines
* Automate reminder notifications
* Manage compliance documents
* Import compliance records from Excel/CSV
* Monitor compliance health through dashboards
* Receive email and in-app notifications

---

# ✨ Key Features

### 📋 Compliance Management

* Create, update, delete and view compliance records
* Track due dates and compliance status
* Priority management (High, Medium, Low)
* Search, filter and pagination

### 📊 Interactive Dashboard

* Total compliance overview
* Compliance completion rate
* Status distribution
* Monthly trends
* Category analytics
* Pie, Bar and Doughnut charts

### 📅 Calendar View

* Interactive compliance calendar
* Upcoming deadline tracking
* Color-coded status indicators
* Daily compliance details

### 📂 Document Management

* Upload compliance documents
* Download files
* File tracking
* Document association with compliance records

### 📥 Excel / CSV Import

* Bulk upload compliance records
* Automatic validation
* Status detection
* Batch processing
* Import logging

### 🔔 Automated Reminder System

* Configurable reminder schedule
* Email notifications
* In-app notifications
* Duplicate reminder prevention
* Reminder history

### 🔐 Secure Authentication

* JWT Authentication
* Password hashing
* Protected APIs
* Session management

### ☁ Deployment Ready

* Render deployment
* GitHub Actions Scheduler
* Gmail SMTP integration
* Production configuration

---

# 🏗️ System Architecture

```text
                                   HR Comply360
                    Statutory Compliance Management System

┌─────────────────────────────────────────────────────────────────────────────┐
│                               Client Layer                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  React.js • Bootstrap • Chart.js • React Calendar • Axios • React Router   │
│                                                                             │
│  Dashboard │ Compliance │ Calendar │ Documents │ Analytics │ Notifications  │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ HTTPS / REST API (JWT Authentication)
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Backend Layer                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Flask REST API                                │
│                                                                             │
│  ┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐    │
│  │ Auth API   │ │ Compliance   │ │ Documents    │ │ Notifications API  │    │
│  └────────────┘ └──────────────┘ └──────────────┘ └────────────────────┘    │
│                                                                             │
│             Business Services & Validation Layer                            │
│                                                                             │
│  • JWT Authentication                                                       │
│  • Excel/CSV Processing                                                     │
│  • Reminder Scheduler                                                       │
│  • Email Service                                                            │
│  • File Upload Management                                                   │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ SQLAlchemy ORM
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Database Layer                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                     SQLite (Development)                                    │
│              PostgreSQL / MySQL (Production)                               │
│                                                                             │
│  Users │ Compliance │ Documents │ Notifications │ Email Logs │ Import Logs │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                ┌───────────────┴────────────────┐
                │                                │
                ▼                                ▼
┌────────────────────────────┐     ┌───────────────────────────────────────┐
│ External Services          │     │ Automation & Deployment               │
├────────────────────────────┤     ├───────────────────────────────────────┤
│ • Gmail SMTP               │     │ • GitHub Actions Scheduler            │
│ • Email Notifications      │     │ • Daily Reminder Trigger (9:00 AM)    │
│ • HTML Email Templates     │     │ • Render Deployment                   │
└────────────────────────────┘     └───────────────────────────────────────┘
```

---

## Architecture Flow

```text
User
   │
   ▼
React Frontend
   │
   ▼
Axios HTTP Requests
   │
   ▼
Flask REST API
   │
   ├── JWT Authentication
   ├── Compliance Management
   ├── Document Management
   ├── Notification Service
   └── Excel Import Service
   │
   ▼
SQLAlchemy ORM
   │
   ▼
Database
   │
   ├── Users
   ├── Compliance Records
   ├── Notifications
   ├── Documents
   ├── Email Logs
   └── Import Logs
   │
   ▼
GitHub Actions Scheduler
   │
   ▼
Reminder Service
   │
   ├── Gmail SMTP Emails
   └── In-App Notifications
```

### Architecture Highlights

* **Presentation Layer:** React-based responsive user interface for HR operations.
* **API Layer:** Flask REST APIs handling authentication, compliance, uploads, and notifications.
* **Business Layer:** Validation, reminder scheduling, email processing, and Excel parsing.
* **Data Layer:** SQLAlchemy ORM with SQLite for development and PostgreSQL/MySQL for production.
* **Automation Layer:** GitHub Actions triggers scheduled reminder jobs every day at **9:00 AM IST**.
* **Notification Layer:** Sends automated email reminders via Gmail SMTP and stores in-app notifications.


---

# 🛠 Technology Stack

## Frontend

| Technology      | Purpose             |
| --------------- | ------------------- |
| React 18        | User Interface      |
| React Router v6 | Routing             |
| Bootstrap 5     | Responsive UI       |
| Axios           | API Communication   |
| Chart.js        | Dashboard Analytics |
| React Calendar  | Calendar View       |
| React Toastify  | Notifications       |

---

## Backend

| Technology         | Purpose               |
| ------------------ | --------------------- |
| Flask              | REST API              |
| Flask SQLAlchemy   | ORM                   |
| Flask JWT Extended | Authentication        |
| Flask Mail         | Email Service         |
| Flask CORS         | Cross-Origin Requests |
| APScheduler        | Background Scheduling |
| Gunicorn           | Production Server     |

---

## Database

* SQLite (Development)
* PostgreSQL / MySQL (Production)

---

## Deployment

* Render
* GitHub Actions
* Gmail SMTP

---

# 📂 Project Structure

```
HR-Comply360
│
├── backend
│   ├── models
│   ├── routes
│   ├── services
│   ├── utils
│   ├── instance
│   ├── app.py
│   └── requirements.txt
│
├── frontend
│   ├── public
│   ├── src
│   │   ├── components
│   │   ├── pages
│   │   ├── services
│   │   └── App.js
│   └── package.json
│
├── .github
│   └── workflows
│
└── README.md
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Dhanyaa-shree/HR-Comply360-Statutory-Compliance-Suite.git

cd HR-Comply360-Statutory-Compliance-Suite
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file inside the backend folder.

```env
SECRET_KEY=your-secret-key

JWT_SECRET_KEY=your-jwt-secret

DEBUG=True

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True

MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

UPLOAD_FOLDER=uploads

GITHUB_ACTIONS_API_KEY=your-api-key
```

---

## Initialize Database

```bash
python seed.py
```

or

```bash
python import_now.py
```

---

## Frontend Setup

```bash
cd ../frontend

npm install
```

Create `.env`

```
REACT_APP_API_URL=http://localhost:5000/api
```

---

## Run Backend

```bash
cd backend

python app.py
```

---

## Run Frontend

```bash
cd frontend

npm start
```

---

#

---

# 🔄 Workflow

### Authentication

```
User
   ↓
Login
   ↓
JWT Authentication
   ↓
Protected Routes
```

---

### Compliance Management

```
Create Compliance
        ↓
Store Database
        ↓
Calculate Reminder Dates
        ↓
Dashboard Update
```

---

### Reminder System

```
GitHub Actions
        ↓
Daily Scheduler
        ↓
Check Due Records
        ↓
Send Email
        ↓
Create Notification
        ↓
Store Logs
```

---

### Excel Import

```
Upload File
      ↓
Validate
      ↓
Parse
      ↓
Transform
      ↓
Database
```

---

# 📊 Database Design

## Users

* id
* name
* email
* password_hash
* created_at

---

## Compliance

* authority
* compliance_name
* category
* valid_date
* priority
* status
* reminder dates
* reminder sent flags

---

## Notifications

* title
* message
* type
* is_read
* created_at

---

## Documents

* compliance_id
* filename
* filepath
* uploaded_at

---

# 🔌 REST API

| Method | Endpoint                      | Description       |
| ------ | ----------------------------- | ----------------- |
| POST   | `/api/auth/login`             | Login             |
| GET    | `/api/compliance`             | List Compliance   |
| POST   | `/api/compliance`             | Create Compliance |
| PUT    | `/api/compliance/:id`         | Update Compliance |
| DELETE | `/api/compliance/:id`         | Delete Compliance |
| GET    | `/api/compliance/stats`       | Dashboard Stats   |
| POST   | `/api/upload/excel`           | Import Excel      |
| GET    | `/api/notifications`          | Notifications     |
| PUT    | `/api/notifications/:id/read` | Mark Read         |
| POST   | `/api/documents/upload`       | Upload Document   |
| GET    | `/api/documents/:id`          | Download Document |
| POST   | `/api/check-reminders`        | Trigger Reminder  |

---

# 🔒 Security

* JWT Authentication
* Password Hashing
* Environment Variables
* SQLAlchemy ORM Protection
* Secure File Upload
* CORS Configuration
* API Key Protected Endpoints

---

# 📈 Highlights

* Full Stack HR Management Application
* Automated Statutory Compliance Tracking
* Email & In-App Notification System
* Interactive Dashboard Analytics
* Calendar-Based Deadline Tracking
* Excel Bulk Import
* Document Repository
* Production Ready Deployment
* CI/CD using GitHub Actions

---

# 🚀 Deployment

## Backend

Render Web Service

```
Build Command

cd backend && pip install -r requirements.txt
```

```
Start Command

cd backend && gunicorn app:app
```

---

## Frontend

Render Static Site

```
Build Command

cd frontend && npm install && npm run build
```

```
Publish Directory

frontend/build
```

---

# 🎯 Future Enhancements

* Role-Based Access Control (RBAC)
* Multi-Tenant Architecture
* Mobile Application
* AI-Based Compliance Risk Prediction
* Advanced Reports & Exports
* WebSocket Real-Time Notifications
* Third-Party HRMS Integration

---

# 🤝 Contributing

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 👩‍💻 Author

**Dhanyaa Shree**

📧 **Email:** [dhanyaashreet010@gmail.com](mailto:dhanyaashreet010@gmail.com)

🐙 **GitHub:** https://github.com/Dhanyaa-shree


---

# ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.

Your support motivates future improvements and open-source contributions.

---

**Built with ❤️ using React, Flask, SQLAlchemy, Bootstrap and Chart.js**
