from django import forms
from django.contrib.auth.models import User
from hospital import models


class PatientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class PatientForm(forms.ModelForm):
    assignedDoctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.all().filter(status=True),
        empty_label="Select Doctor (Name and Department)",
        to_field_name="user_id",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = models.Patient
        fields = ['address', 'mobile', 'status', 'symptoms', 'profile_pic', 'assignedDoctorId']


class AppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True), empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId = forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True), empty_label="Patient Name and Symptoms", to_field_name="user_id")

    class Meta:
        model = models.Appointment
        fields = ['description', 'status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True), empty_label="Doctor Name and Department", to_field_name="user_id")

    class Meta:
        model = models.Appointment
        fields = ['description', 'status']

