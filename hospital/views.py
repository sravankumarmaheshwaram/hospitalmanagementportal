from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from .models import ContactusForm
from django.contrib.auth import logout, login, authenticate



# Create your views here.
def home_view(request):
    return render(request,'hospital/index.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# Custom redirect views for legacy URLs
@login_required(login_url='unified_login')
def legacy_patient_dashboard_redirect(request):
    return redirect('patient-dashboard', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_patient_appointment_redirect(request):
    return redirect('patient-appointment', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_patient_book_appointment_redirect(request):
    return redirect('patient-book-appointment', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_patient_view_appointment_redirect(request):
    return redirect('patient-view-appointment', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_patient_view_doctor_redirect(request):
    return redirect('patient-view-doctor', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_patient_discharge_redirect(request):
    return redirect('patient-discharge', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_doctor_dashboard_redirect(request):
    return redirect('doctor-dashboard', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_doctor_patient_redirect(request):
    return redirect('doctor-patient', user_id=request.user.id)

@login_required(login_url='unified_login')
def legacy_doctor_appointment_redirect(request):
    return redirect('doctor-appointment', user_id=request.user.id)

# Unified Login View
def unified_login_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    
    if request.method == 'POST':
        form = forms.UnifiedLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user has the correct role
                user_groups = [group.name for group in user.groups.all()]
                
                if role == 'admin' and (user.is_superuser or user.is_staff or user.groups.filter(name='ADMIN').exists()):
                    login(request, user)
                    return redirect('afterlogin')
                elif role == 'doctor' and user.groups.filter(name='DOCTOR').exists():
                    login(request, user)
                    return redirect('afterlogin')
                elif role == 'patient' and user.groups.filter(name='PATIENT').exists():
                    login(request, user)
                    return redirect('afterlogin')
                else:
                    available_roles = []
                    if user.is_superuser or user.is_staff or user.groups.filter(name='ADMIN').exists():
                        available_roles.append('admin')
                    if user.groups.filter(name='DOCTOR').exists():
                        available_roles.append('doctor')
                    if user.groups.filter(name='PATIENT').exists():
                        available_roles.append('patient')
                    
                    if available_roles:
                        messages.error(request, f'You are not registered as a {role}. You are registered as: {", ".join(available_roles)}')
                    else:
                        messages.error(request, 'Your account is not assigned to any role. Please contact admin.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = forms.UnifiedLoginForm()
    
    return render(request, 'hospital/unified_login.html', {'form': form})

# Unified Signup View
def unified_signup_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    
    if request.method == 'POST':
        form = forms.UnifiedSignupForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                role = form.cleaned_data['role']
                
                # Check if user already exists
                try:
                    existing_user = User.objects.get(username=username)
                    
                    # Check if user already has this role
                    if role == 'doctor':
                        if existing_user.groups.filter(name='DOCTOR').exists():
                            messages.error(request, 'This user is already registered as a doctor.')
                            return render(request, 'hospital/unified_signup.html', {'form': form})
                        
                        # Check if doctor profile already exists
                        if models.Doctor.objects.filter(user=existing_user).exists():
                            messages.error(request, 'This user already has a doctor profile.')
                            return render(request, 'hospital/unified_signup.html', {'form': form})
                            
                    elif role == 'patient':
                        if existing_user.groups.filter(name='PATIENT').exists():
                            messages.error(request, 'This user is already registered as a patient.')
                            return render(request, 'hospital/unified_signup.html', {'form': form})
                        
                        # Check if patient profile already exists
                        if models.Patient.objects.filter(user=existing_user).exists():
                            messages.error(request, 'This user already has a patient profile.')
                            return render(request, 'hospital/unified_signup.html', {'form': form})
                    
                    # Use existing user
                    user = existing_user
                    
                except User.DoesNotExist:
                    # Create new user
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                
                # Add role-specific profile and group
                if role == 'doctor':
                    # Create doctor profile with basic details
                    doctor = models.Doctor()
                    doctor.user = user
                    doctor.address = form.cleaned_data['address']
                    doctor.mobile = form.cleaned_data['mobile']
                    doctor.department = 'Cardiologist'  # Default department
                    if form.cleaned_data.get('profile_pic'):
                        doctor.profile_pic = form.cleaned_data['profile_pic']
                    doctor.status = False  # Requires admin approval
                    doctor.save()
                    
                    # Add to doctor group
                    doctor_group, created = Group.objects.get_or_create(name='DOCTOR')
                    doctor_group.user_set.add(user)
                    
                    messages.success(request, 'Doctor registration submitted successfully. Awaiting admin approval.')
                    return redirect('unified_login')
                    
                elif role == 'patient':
                    # Create patient profile with basic details
                    patient = models.Patient()
                    patient.user = user
                    patient.address = form.cleaned_data['address']
                    patient.mobile = form.cleaned_data['mobile']
                    patient.symptoms = 'General consultation'  # Default symptoms
                    if form.cleaned_data.get('profile_pic'):
                        patient.profile_pic = form.cleaned_data['profile_pic']
                    patient.assignedDoctorId = None  # Will be assigned by admin
                    patient.status = False  # Requires admin approval
                    patient.save()
                    
                    # Add to patient group
                    patient_group, created = Group.objects.get_or_create(name='PATIENT')
                    patient_group.user_set.add(user)
                    
                    messages.success(request, 'Patient registration submitted successfully. Awaiting admin approval.')
                    return redirect('unified_login')
                else:
                    messages.error(request, 'Invalid role selected.')
                    
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = forms.UnifiedSignupForm()
    
    return render(request, 'hospital/unified_signup.html', {'form': form})


#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')




def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                
                # Check if user already exists
                try:
                    existing_user = User.objects.get(username=username)
                    
                    # Check if user already has admin role
                    if existing_user.is_superuser or existing_user.is_staff or existing_user.groups.filter(name='ADMIN').exists():
                        messages.error(request, 'This user is already registered as an admin.')
                        return render(request, 'hospital/adminsignup.html', {'form': form})
                    
                    # Use existing user and make them admin
                    user = existing_user
                    user.is_staff = True
                    user.save()
                    
                except User.DoesNotExist:
                    # Create new user
                    user = form.save()
                    user.set_password(user.password)
                    user.is_staff = True
                    user.save()
                
                # Add to admin group
                my_admin_group = Group.objects.get_or_create(name='ADMIN')
                my_admin_group[0].user_set.add(user)
                
                messages.success(request, 'Admin registration successful.')
                return HttpResponseRedirect('adminlogin')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.info(request,'enter valid details')
    else:
        form=forms.AdminSigupForm()
    return render(request,'hospital/adminsignup.html',{'form':form})




def doctor_signup_view(request):

    from doctors.forms import DoctorUserForm, DoctorForm
    userForm=DoctorUserForm()
    doctorForm=DoctorForm()

    mydict={'userForm':userForm,'doctorForm':doctorForm}

    if request.method=='POST':
        userForm=DoctorUserForm(request.POST)
        doctorForm=DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            try:
                username = userForm.cleaned_data['username']
                
                # Check if user already exists
                try:
                    existing_user = User.objects.get(username=username)
                    
                    # Check if user already has doctor role
                    if existing_user.groups.filter(name='DOCTOR').exists() or models.Doctor.objects.filter(user=existing_user).exists():
                        messages.error(request, 'This user is already registered as a doctor.')
                        mydict={'userForm':userForm,'doctorForm':doctorForm}
                        return render(request,'hospital/doctorsignup.html',context=mydict)
                    
                    # Use existing user
                    user = existing_user
                    
                except User.DoesNotExist:
                    # Create new user
                    user=userForm.save()
                    user.set_password(user.password)
                    user.save()
                
                # Create doctor profile
                doctor=doctorForm.save(commit=False)
                doctor.user=user
                doctor.save()
                my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
                my_doctor_group[0].user_set.add(user)
                messages.success(request,'Registration submitted. Awaiting admin approval.')
                return redirect('doctorlogin')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                mydict={'userForm':userForm,'doctorForm':doctorForm}
                return render(request,'hospital/doctorsignup.html',context=mydict)
        else:
            messages.error(request,'Please correct the errors below and resubmit.')
            mydict={'userForm':userForm,'doctorForm':doctorForm}
            return render(request,'hospital/doctorsignup.html',context=mydict)
    return render(request,'hospital/doctorsignup.html',context=mydict)


def patient_signup_view(request):
    from patients.forms import PatientUserForm, PatientForm
    userForm=PatientUserForm()
    patientForm=PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=PatientUserForm(request.POST)
        patientForm=PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            try:
                username = userForm.cleaned_data['username']
                
                # Check if user already exists
                try:
                    existing_user = User.objects.get(username=username)
                    
                    # Check if user already has patient role
                    if existing_user.groups.filter(name='PATIENT').exists() or models.Patient.objects.filter(user=existing_user).exists():
                        messages.error(request, 'This user is already registered as a patient.')
                        mydict={'userForm':userForm,'patientForm':patientForm}
                        return render(request,'hospital/patientsignup.html',context=mydict)
                    
                    # Use existing user
                    user = existing_user
                    
                except User.DoesNotExist:
                    # Create new user
                    user=userForm.save()
                    user.set_password(user.password)
                    user.save()
                
                # Create patient profile
                patient=patientForm.save(commit=False)
                patient.user=user
                patient.assignedDoctorId=request.POST.get('assignedDoctorId') or None
                patient.save()
                my_patient_group = Group.objects.get_or_create(name='PATIENT')
                my_patient_group[0].user_set.add(user)
                messages.success(request,'Registration submitted. Awaiting admin approval.')
                return redirect('patientlogin')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                mydict={'userForm':userForm,'patientForm':patientForm}
                return render(request,'hospital/patientsignup.html',context=mydict)
        else:
            messages.error(request,'Please correct the errors below and resubmit.')
            mydict={'userForm':userForm,'patientForm':patientForm}
            return render(request,'hospital/patientsignup.html',context=mydict)
    return render(request,'hospital/patientsignup.html',context=mydict)






#-----------for checking user is doctor , patient or admin(by sumit)
def is_admin(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
        

    elif is_doctor(request.user):
        accountapproval=models.Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard', user_id=request.user.id)
        else:
            return render(request,'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval=models.Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard', user_id=request.user.id)
        else:
            return render(request,'hospital/patient_wait_for_approval.html')
    # Handle authenticated users without a role to avoid redirect loops
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin-dashboard')
    logout(request)
    return redirect('home')
    
    
    








#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
# moved to adminpanel.views


# this view for sidebar click on admin page
@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)




@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_discharge_patient.html',{'patients':patients})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admitDate) #2 days, 0:00:00
    assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
    d=days.days # only how many day that is 2
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'hospital/patient_final_bill.html',context=patientDict)
    return render(request,'hospital/patient_generate_bill.html',context=patientDict)



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='unified_login')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)



@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)





@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='unified_login')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name,
    'doctorMobile':doctor.mobile,
    'doctorAddress':doctor.address,
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'hospital/patient_dashboard.html',context=mydict)



@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request,'hospital/patient_book_appointment.html',context=mydict)



def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})



def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='unified_login')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)


#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    
    if request.method == 'POST':
        # Handle the new form fields from our modern contact form
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        name = f"{first_name} {last_name}".strip() or request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        feedback = message or request.POST.get('feedback', '')

        ContactusForm.objects.create(
            name=name,
            email=email,
            feedback=feedback
        )
        
        messages.success(request, 'Your message has been sent successfully!')

        return render(request, 'hospital/contactussuccess.html')
        
    
    return render(request,'hospital/contactus.html')

    
       
            


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------




