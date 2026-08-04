from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/<int:user_id>', views.doctor_dashboard_view, name='doctor-dashboard'),
    path('search/<int:user_id>', views.search_view, name='search'),
    path('patient/<int:user_id>', views.doctor_patient_view, name='doctor-patient'),
    path('view-patient/<int:user_id>', views.doctor_view_patient_view, name='doctor-view-patient'),
    path('view-discharge-patient/<int:user_id>', views.doctor_view_discharge_patient_view, name='doctor-view-discharge-patient'),
    path('appointment/<int:user_id>', views.doctor_appointment_view, name='doctor-appointment'),
    path('view-appointment/<int:user_id>', views.doctor_view_appointment_view, name='doctor-view-appointment'),
    path('delete-appointment/<int:user_id>', views.doctor_delete_appointment_view, name='doctor-delete-appointment'),
    path('delete-appointment/<int:pk>', views.delete_appointment_view, name='delete-appointment'),
]

