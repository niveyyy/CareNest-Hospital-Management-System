# CareNest – Hospital Management System

CareNest is a Hospital Management System developed using Python and Django. It helps manage hospital activities through separate dashboards for Admin, Doctor, and Patient users.

It includes patient registration, doctor management, appointment booking, medical records, billing, and password reset features.

## Current application modules

### Administrator
- Register and sign in to the administration area.
- Review doctor and patient registration requests.
- Approve, reject, view, and manage doctor and patient records.
- Manage appointments and their approval status.
- View dashboard counts for approved and pending doctors, patients, and appointments.
- Record discharge details and generate patient bills.

### Doctor
- Submit a doctor registration request and wait for administrator approval.
- View assigned patients and manage appointment requests.
- Define weekly availability by day and time range.
- Approve, reject, and mark appointments as completed.
- Create diagnosis and prescription records for assigned patients.
- View discharged patient records.

### Patient
- Register even when a doctor has not yet been assigned; the administrator can assign one later.
- Sign in after administrator approval.
- View assigned doctor information when available.
- Request appointments only within a doctor's published availability.
- Track pending, approved, rejected, and completed appointment statuses.
- View diagnosis, prescriptions, medical notes, and discharge bills.
- Request a password reset using the registered email address.

## Technology stack
- Python
- Django
- SQLite (local development database)
- HTML, CSS, JavaScript, Bootstrap
- Django Widget Tweaks
- xhtml2pdf (PDF billing)

## Project layout
```text
CareNest/
├── hospital/             # Models, forms, views, migrations
├── hospitalmanagement/   # Django project configuration
├── templates/hospital/   # HTML templates
├── static/               # CSS, SVG assets, profile images
├── manage.py
├── requirement.txt
├── .env.example
└── README.md
```

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirement.txt
   ```
5. Copy `.env.example` to `.env` and set a unique `SECRET_KEY`. Keep `.env` private.
6. Apply migrations and start the server:
   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```
7. Visit `http://127.0.0.1:8000/`.

## Run automated tests

Patient registration, approval, appointment scheduling, appointment status updates, medical-record access, and secure logout have regression tests. Run them from the folder containing `manage.py`:

```powershell
python manage.py test hospital
```

## Configuration and safety
- `.env` and local SQLite databases are intentionally excluded from version control.
- The fallback secret key is only for local development. Set a unique secret key before sharing or deploying the application.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` for deployment.
- Password-reset emails are printed to the terminal during local development. For real email delivery, configure `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env` with an app password; never commit those credentials.
- This is an educational project, not a production-ready hospital information system. It needs a security review, privacy safeguards, automated tests, backups, and deployment hardening before real patient data is used.

## Developer
**Nivetha**  
B.Tech Information Technology (2023–2027)  
Nandha College of Technology  
GitHub: `niveyyy`
