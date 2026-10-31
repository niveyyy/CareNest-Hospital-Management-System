# CareNest update – October 2026

- Patient registration now works even when no doctor has been assigned yet; an administrator can assign a doctor later.
- Registration forms collect an email address for account recovery and appointment notifications.
- Added doctor weekly availability management.
- Added date/time-based appointment requests with availability and duplicate-time validation.
- Added Pending, Approved, Rejected, and Completed appointment states.
- Added doctor-side appointment actions and patient-side status tracking.
- Added doctor-created medical records and patient-only medical-record viewing.
- Added password reset pages and local console email delivery when SMTP credentials are not configured.
- Added safe fallback avatars for accounts without profile pictures.
- Added regression tests for registration, appointments, availability, dashboards, and medical records.

This remains an educational project and is not approved for storing real patient data without a formal security and privacy review.


## Logout reliability fix
- Changed logout to a POST-only Django logout action with CSRF protection.
- Standardized the logout URL as `/logout/` and redirected successful logout to the public homepage.
- Updated Admin, Doctor, Patient, and approval-waiting screens.
- Added regression tests for session clearing, redirect behaviour, and GET rejection.
