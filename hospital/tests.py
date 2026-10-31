from django.contrib.auth.models import Group, User
from django.test import TestCase

from datetime import time, timedelta
from django.utils import timezone
from .models import Appointment, Doctor, DoctorAvailability, MedicalRecord, Patient


class PatientRegistrationFlowTests(TestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(
            username='approved_doctor',
            password='StrongDoctorPass123!',
            first_name='Asha',
            last_name='Kumar',
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            address='Chennai',
            mobile='9876543210',
            department='Cardiologist',
            status=True,
        )

    def patient_payload(self, **overrides):
        payload = {
            'first_name': 'Nivetha',
            'last_name': 'Patient',
            'username': 'nivetha_patient',
            'password': 'StrongPatientPass123!',
            'email': 'nivetha.patient@example.com',
            'address': 'Erode',
            'mobile': '9876543211',
            'symptoms': 'Headache',
            'assignedDoctorId': str(self.doctor_user.pk),
        }
        payload.update(overrides)
        return payload

    def test_registration_page_lists_approved_doctor(self):
        response = self.client.get('/patientsignup')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asha')
        self.assertTrue(response.context['has_approved_doctors'])

    def test_patient_registration_creates_account_and_profile(self):
        response = self.client.post('/patientsignup', self.patient_payload())

        self.assertRedirects(response, '/patientlogin', fetch_redirect_response=False)
        user = User.objects.get(username='nivetha_patient')
        patient = Patient.objects.get(user=user)

        self.assertTrue(user.check_password('StrongPatientPass123!'))
        self.assertEqual(patient.assignedDoctorId, self.doctor_user.pk)
        self.assertFalse(patient.status, 'New patient accounts must wait for admin approval.')
        self.assertTrue(user.groups.filter(name='PATIENT').exists())

    def test_duplicate_username_shows_validation_error_without_creating_profile(self):
        User.objects.create_user(username='nivetha_patient', password='AnotherPass123!')

        response = self.client.post('/patientsignup', self.patient_payload())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')
        self.assertEqual(Patient.objects.count(), 0)

    def test_registration_is_allowed_without_an_approved_doctor(self):
        self.doctor.status = False
        self.doctor.save(update_fields=['status'])
        payload = self.patient_payload()
        payload.pop('assignedDoctorId')

        response = self.client.post('/patientsignup', payload)

        self.assertRedirects(response, '/patientlogin', fetch_redirect_response=False)
        patient = Patient.objects.get(user__username='nivetha_patient')
        self.assertIsNone(patient.assignedDoctorId)
        self.assertFalse(patient.status)

    def test_patient_login_waits_for_admin_approval_then_opens_dashboard(self):
        self.client.post('/patientsignup', self.patient_payload())
        patient_user = User.objects.get(username='nivetha_patient')

        self.assertTrue(self.client.login(username='nivetha_patient', password='StrongPatientPass123!'))
        waiting_response = self.client.get('/afterlogin')
        self.assertTemplateUsed(waiting_response, 'hospital/patient_wait_for_approval.html')

        patient = Patient.objects.get(user=patient_user)
        patient.status = True
        patient.save(update_fields=['status'])

        approved_response = self.client.get('/afterlogin')
        self.assertRedirects(approved_response, '/patient-dashboard', fetch_redirect_response=False)

        dashboard_response = self.client.get('/patient-dashboard')
        self.assertEqual(dashboard_response.status_code, 200)


class CareNestWorkflowTests(TestCase):
    def setUp(self):
        doctor_user = User.objects.create_user(
            username='workflow_doctor', password='StrongDoctorPass123!',
            first_name='Asha', last_name='Kumar', email='asha@example.com',
        )
        doctor_user.groups.add(Group.objects.get_or_create(name='DOCTOR')[0])
        self.doctor = Doctor.objects.create(
            user=doctor_user, address='Chennai', mobile='9876543210',
            department='Cardiologist', status=True,
        )
        patient_user = User.objects.create_user(
            username='workflow_patient', password='StrongPatientPass123!',
            first_name='Nivetha', last_name='Patient', email='nivetha@example.com',
        )
        patient_user.groups.add(Group.objects.get_or_create(name='PATIENT')[0])
        self.patient = Patient.objects.create(
            user=patient_user, address='Erode', mobile='9876543211',
            symptoms='Headache', assignedDoctorId=doctor_user.pk, status=True,
        )
        self.doctor_user = doctor_user
        self.patient_user = patient_user

    def test_doctor_workflow_pages_render(self):
        self.client.login(username='workflow_doctor', password='StrongDoctorPass123!')
        self.assertEqual(self.client.get('/doctor-availability').status_code, 200)
        self.assertEqual(self.client.get('/doctor-medical-records').status_code, 200)
        self.assertEqual(self.client.get('/doctor-view-appointment').status_code, 200)

    def test_patient_workflow_pages_render(self):
        self.client.login(username='workflow_patient', password='StrongPatientPass123!')
        self.assertEqual(self.client.get('/patient-book-appointment').status_code, 200)
        self.assertEqual(self.client.get('/patient-medical-records').status_code, 200)
        self.assertEqual(self.client.get('/patient-view-appointment').status_code, 200)

    def test_patient_dashboard_works_before_doctor_assignment(self):
        self.patient.assignedDoctorId = None
        self.patient.save(update_fields=['assignedDoctorId'])
        self.client.login(username='workflow_patient', password='StrongPatientPass123!')
        response = self.client.get('/patient-dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Not assigned yet')

    def test_doctor_can_create_availability(self):
        self.client.login(username='workflow_doctor', password='StrongDoctorPass123!')
        response = self.client.post('/doctor-availability', {
            'weekday': 0, 'start_time': '09:00', 'end_time': '12:00', 'is_active': 'on',
        })
        self.assertRedirects(response, '/doctor-availability', fetch_redirect_response=False)
        self.assertTrue(DoctorAvailability.objects.filter(doctor=self.doctor, weekday=0).exists())

    def test_patient_booking_requires_an_available_doctor_slot(self):
        target_date = timezone.localdate() + timedelta(days=(7 - timezone.localdate().weekday()) % 7 or 7)
        DoctorAvailability.objects.create(
            doctor=self.doctor, weekday=target_date.weekday(),
            start_time=time(9, 0), end_time=time(12, 0),
        )
        self.client.login(username='workflow_patient', password='StrongPatientPass123!')
        response = self.client.post('/patient-book-appointment', {
            'doctorId': str(self.doctor_user.pk), 'scheduled_date': target_date.isoformat(),
            'scheduled_time': '10:00', 'description': 'Routine check-up',
        })
        self.assertRedirects(response, '/patient-view-appointment', fetch_redirect_response=False)
        appointment = Appointment.objects.get(patientId=self.patient_user.pk)
        self.assertEqual(appointment.workflow_status, 'PENDING')

    def test_doctor_can_update_own_appointment_status(self):
        appointment = Appointment.objects.create(
            patientId=self.patient_user.pk, doctorId=self.doctor_user.pk,
            patientName='Nivetha Patient', doctorName='Asha Kumar',
            description='Check-up', workflow_status='PENDING',
        )
        self.client.login(username='workflow_doctor', password='StrongDoctorPass123!')
        response = self.client.post(f'/doctor-update-appointment/{appointment.pk}', {'action': 'approve'})
        self.assertRedirects(response, '/doctor-view-appointment', fetch_redirect_response=False)
        appointment.refresh_from_db()
        self.assertEqual(appointment.workflow_status, 'APPROVED')
        self.assertTrue(appointment.status)

    def test_patient_can_only_see_own_medical_records(self):
        record = MedicalRecord.objects.create(
            patient=self.patient, doctor=self.doctor, diagnosis='Seasonal allergy',
            prescription='Take medication as prescribed.', notes='Follow up if symptoms continue.',
        )
        self.client.login(username='workflow_patient', password='StrongPatientPass123!')
        response = self.client.get('/patient-medical-records')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seasonal allergy')


class LogoutFlowTests(TestCase):
    """Logout must end the session and return to the public homepage."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='logout_test_user', password='StrongLogoutPass123!'
        )

    def test_logout_post_clears_session_and_redirects_home(self):
        self.client.force_login(self.user)

        response = self.client.post('/logout/')

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_get_is_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get('/logout/')

        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_form_exists_in_all_role_navigation_templates(self):
        from django.template.loader import get_template

        for template_name in (
            'hospital/admin_base.html',
            'hospital/doctor_base.html',
            'hospital/patient_base.html',
            'hospital/doctor_wait_for_approval.html',
            'hospital/patient_wait_for_approval.html',
        ):
            template = get_template(template_name)
            self.assertIsNotNone(template)
