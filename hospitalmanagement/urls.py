

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hospital import views
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import RedirectView


#-------------FOR ADMIN RELATED URLS
urlpatterns = [
    path('djadmin/', admin.site.urls),
    path('',views.home_view,name='home'),


    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view,name='contactusform'),


    path('adminclick', views.adminclick_view),
    path('doctorclick', views.doctorclick_view),
    path('patientclick', views.patientclick_view),

    # Unified login and signup
    path('login', views.unified_login_view, name='unified_login'),
    path('signup', views.unified_signup_view, name='unified_signup'),
    
    # Legacy routes for backward compatibility
    path('adminsignup', views.admin_signup_view),
    path('doctorsignup', views.doctor_signup_view,name='doctorsignup'),
    path('patientsignup', views.patient_signup_view),
    
    path('adminlogin', LoginView.as_view(template_name='hospital/adminlogin.html'), name='adminlogin'),
    path('doctorlogin', LoginView.as_view(template_name='hospital/doctorlogin.html'), name='doctorlogin'),
    path('patientlogin', LoginView.as_view(template_name='hospital/patientlogin.html'), name='patientlogin'),


    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout/', views.logout_view, name='logout'),


    path('admin/', include('adminpanel.urls')),
    # Map default accounts login to our admin login to avoid 404s
    path('accounts/login/', RedirectView.as_view(url='/adminlogin', permanent=False)),
    # Legacy redirects for existing templates
    path('admin-dashboard', RedirectView.as_view(url='/admin/dashboard', permanent=False)),
    path('admin-doctor', RedirectView.as_view(url='/admin/doctor', permanent=False)),
    path('admin-view-doctor', RedirectView.as_view(url='/admin/view-doctor', permanent=False)),
    path('admin-add-doctor', RedirectView.as_view(url='/admin/add-doctor', permanent=False)),
    path('admin-approve-doctor', RedirectView.as_view(url='/admin/approve-doctor', permanent=False)),
    path('admin-view-doctor-specialisation', RedirectView.as_view(url='/admin/view-doctor-specialisation', permanent=False)),
    path('admin-patient', RedirectView.as_view(url='/admin/patient', permanent=False)),
    path('admin-view-patient', RedirectView.as_view(url='/admin/view-patient', permanent=False)),
    path('admin-add-patient', RedirectView.as_view(url='/admin/add-patient', permanent=False)),
    path('admin-approve-patient', RedirectView.as_view(url='/admin/approve-patient', permanent=False)),
    path('admin-discharge-patient', RedirectView.as_view(url='/admin/discharge-patient', permanent=False)),
    path('admin-appointment', RedirectView.as_view(url='/admin/appointment', permanent=False)),
    path('admin-view-appointment', RedirectView.as_view(url='/admin/view-appointment', permanent=False)),
    path('admin-add-appointment', RedirectView.as_view(url='/admin/add-appointment', permanent=False)),
    path('admin-approve-appointment', RedirectView.as_view(url='/admin/approve-appointment', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#---------FOR DOCTOR RELATED URLS-------------------------------------
urlpatterns +=[
    path('doctor/', include('doctors.urls')),
    # Legacy doctor routes with user ID redirects
    path('doctor-dashboard', views.legacy_doctor_dashboard_redirect),
    path('doctor-patient', views.legacy_doctor_patient_redirect),
    path('doctor-appointment', views.legacy_doctor_appointment_redirect),
]




#---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns +=[
    path('patient/', include('patients.urls')),
    # Legacy patient routes with user ID redirects
    path('patient-dashboard', views.legacy_patient_dashboard_redirect),
    path('patient-appointment', views.legacy_patient_appointment_redirect),
    path('patient-book-appointment', views.legacy_patient_book_appointment_redirect),
    path('patient-view-appointment', views.legacy_patient_view_appointment_redirect),
    path('patient-view-doctor', views.legacy_patient_view_doctor_redirect),
    path('patient-discharge', views.legacy_patient_discharge_redirect),
]


