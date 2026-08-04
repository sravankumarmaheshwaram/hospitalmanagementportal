from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from hospital import models


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request, user_id):
    # Security check: ensure user can only access their own dashboard
    if request.user.id != user_id:
        return redirect('unified_login')
    patientcount = models.Patient.objects.all().filter(status=True, assignedDoctorId=request.user.id).count()
    appointmentcount = models.Appointment.objects.all().filter(status=True, doctorId=request.user.id).count()
    patientdischarged = models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    appointments = models.Appointment.objects.all().filter(status=True, doctorId=request.user.id).order_by('-id')
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(status=True, user_id__in=patientid).order_by('-id')
    appointments = zip(appointments, patients)
    mydict = {
        'patientcount': patientcount,
        'appointmentcount': appointmentcount,
        'patientdischarged': patientdischarged,
        'appointments': appointments,
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor_dashboard.html', context=mydict)


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_patient_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    mydict = {
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor_patient.html', context=mydict)


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    patients = models.Patient.objects.all().filter(status=True, assignedDoctorId=request.user.id)
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_view_patient.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def search_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    query = request.GET['query']
    patients = models.Patient.objects.all().filter(status=True, assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query) | Q(user__first_name__icontains=query))
    return render(request, 'hospital/doctor_view_patient.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    dischargedpatients = models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_view_discharge_patient.html', {'dischargedpatients': dischargedpatients, 'doctor': doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_appointment_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_appointment.html', {'doctor': doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(status=True, doctorId=request.user.id)
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_view_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request, user_id):
    # Security check: ensure user can only access their own data
    if request.user.id != user_id:
        return redirect('unified_login')
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(status=True, doctorId=request.user.id)
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def delete_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(status=True, doctorId=request.user.id)
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})
from django.shortcuts import render

# Create your views here.
