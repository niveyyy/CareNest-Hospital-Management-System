from django import forms
from django.contrib.auth.models import User
from . import models



#for admin signup
class AdminSigupForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model=User
        fields=['first_name','last_name','email','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }


#for student related form
class DoctorUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model=User
        fields=['first_name','last_name','email','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class DoctorForm(forms.ModelForm):
    class Meta:
        model=models.Doctor
        fields=['address','mobile','department','status','profile_pic']



#for teacher related form
class PatientUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model=User
        fields=['first_name','last_name','email','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class PatientForm(forms.ModelForm):
    # Only approved doctors can be selected by a patient.
    # The selected doctor's User ID is stored in Patient.assignedDoctorId.
    assignedDoctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.filter(status=True).select_related('user'),
        empty_label='Select an approved doctor',
        to_field_name='user_id',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = models.Patient
        # Account approval is controlled by the admin, never by the signup form.
        fields = ['address', 'mobile', 'symptoms', 'profile_pic']



class AppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.filter(status=True).select_related('user'),
        empty_label='Choose an approved doctor', to_field_name='user_id',
    )
    scheduled_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    scheduled_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = models.Appointment
        fields = ['description', 'scheduled_date', 'scheduled_time']

    def clean_scheduled_date(self):
        value = self.cleaned_data['scheduled_date']
        from django.utils import timezone
        if value < timezone.localdate():
            raise forms.ValidationError('Please choose today or a future date.')
        return value

    def clean(self):
        cleaned = super().clean()
        scheduled_date = cleaned.get('scheduled_date')
        scheduled_time = cleaned.get('scheduled_time')
        from django.utils import timezone
        if scheduled_date == timezone.localdate() and scheduled_time:
            current_time = timezone.localtime().time().replace(second=0, microsecond=0)
            if scheduled_time <= current_time:
                self.add_error('scheduled_time', 'Please choose a future time.')
        return cleaned


class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = models.DoctorAvailability
        fields = ['weekday', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get('start_time'), cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('End time must be later than start time.')
        return cleaned


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = models.MedicalRecord
        fields = ['patient', 'diagnosis', 'prescription', 'notes']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'placeholder': 'Diagnosis'}),
            'prescription': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Prescription and dosage'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes (optional)'}),
        }


#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


