from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from hospital import models
from .forms import PatientAppointmentForm


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_dashboard_view(request, user_id):
    # Security check: ensure user can only access their own dashboard
    if request.user.id != user_id:
        return redirect('unified_login')
    
    patient = models.Patient.objects.get(user_id=request.user.id)
    
    # Handle case where patient doesn't have an assigned doctor
    doctor = None
    doctorName = "Not Assigned"
    doctorMobile = "N/A"
    doctorAddress = "N/A"
    doctorDepartment = "General"
    
    if patient.assignedDoctorId:
        try:
            doctor = models.Doctor.objects.get(user_id=patient.assignedDoctorId)
            doctorName = doctor.get_name
            doctorMobile = doctor.mobile
            doctorAddress = doctor.address
            doctorDepartment = doctor.department
        except models.Doctor.DoesNotExist:
            # Doctor was deleted or doesn't exist
            doctorName = "Doctor Not Found"
            doctorMobile = "N/A"
            doctorAddress = "N/A"
            doctorDepartment = "General"
    
    # Get other patients for community section (excluding current patient)
    other_patients = models.Patient.objects.filter(status=True).exclude(user_id=request.user.id)[:5]
    
    # Add doctor information to other patients
    for p in other_patients:
        if p.assignedDoctorId:
            try:
                p_doctor = models.Doctor.objects.get(user_id=p.assignedDoctorId)
                p.doctor_name = p_doctor.get_name
                p.doctor_department = p_doctor.department
            except models.Doctor.DoesNotExist:
                p.doctor_name = "Not Assigned"
                p.doctor_department = "General"
        else:
            p.doctor_name = "Not Assigned"
            p.doctor_department = "General"
    
    # Get patient's appointments
    my_appointments = models.Appointment.objects.filter(patientId=request.user.id).order_by('-appointmentDate')[:5]
    
    # Add doctor profile pics to appointments
    for appointment in my_appointments:
        try:
            app_doctor = models.Doctor.objects.get(user_id=appointment.doctorId)
            appointment.doctor_profile_pic = app_doctor.profile_pic
        except models.Doctor.DoesNotExist:
            appointment.doctor_profile_pic = None
    
    mydict = {
        'patient': patient,
        'doctorName': doctorName,
        'doctorMobile': doctorMobile,
        'doctorAddress': doctorAddress,
        'symptoms': patient.symptoms,
        'doctorDepartment': doctorDepartment,
        'admitDate': patient.admitDate,
        'other_patients': other_patients,
        'my_appointments': my_appointments,
    }
    return render(request, 'hospital/patient_dashboard.html', context=mydict)


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_appointment_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient_appointment.html', {'patient': patient})


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_book_appointment_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    appointmentForm = PatientAppointmentForm()
    patient = models.Patient.objects.get(user_id=request.user.id)
    message = None
    mydict = {'appointmentForm': appointmentForm, 'patient': patient, 'message': message}
    if request.method == 'POST':
        appointmentForm = PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            doctor = models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.POST.get('doctorId')
            appointment.patientId = request.user.id
            appointment.doctorName = models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName = request.user.first_name
            appointment.status = False
            appointment.save()
        return redirect('patient-view-appointment', user_id=request.user.id)
    return render(request, 'hospital/patient_book_appointment.html', context=mydict)


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_view_doctor_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    doctors = models.Doctor.objects.all().filter(status=True)
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient_view_doctor.html', {'patient': patient, 'doctors': doctors})


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def search_doctor_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    patient = models.Patient.objects.get(user_id=request.user.id)
    query = request.GET['query']
    doctors = models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query) | Q(user__first_name__icontains=query))
    return render(request, 'hospital/patient_view_doctor.html', {'patient': patient, 'doctors': doctors})


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_view_appointment_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request, 'hospital/patient_view_appointment.html', {'appointments': appointments, 'patient': patient})


@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_discharge_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    patient = models.Patient.objects.get(user_id=request.user.id)
    dischargeDetails = models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict = None
    if dischargeDetails:
        patientDict = {
            'is_discharged': True,
            'patient': patient,
            'patientId': patient.id,
            'patientName': patient.get_name,
            'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
            'address': patient.address,
            'mobile': patient.mobile,
            'symptoms': patient.symptoms,
            'admitDate': patient.admitDate,
            'releaseDate': dischargeDetails[0].releaseDate,
            'daySpent': dischargeDetails[0].daySpent,
            'medicineCost': dischargeDetails[0].medicineCost,
            'roomCharge': dischargeDetails[0].roomCharge,
            'doctorFee': dischargeDetails[0].doctorFee,
            'OtherCharge': dischargeDetails[0].OtherCharge,
            'total': dischargeDetails[0].total,
        }
    else:
        patientDict = {
            'is_discharged': False,
            'patient': patient,
            'patientId': request.user.id,
        }
    return render(request, 'hospital/patient_discharge.html', context=patientDict)

