from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/<int:user_id>', views.patient_dashboard_view, name='patient-dashboard'),
    path('appointment/<int:user_id>', views.patient_appointment_view, name='patient-appointment'),
    path('book-appointment/<int:user_id>', views.patient_book_appointment_view, name='patient-book-appointment'),
    path('view-appointment/<int:user_id>', views.patient_view_appointment_view, name='patient-view-appointment'),
    path('view-doctor/<int:user_id>', views.patient_view_doctor_view, name='patient-view-doctor'),
    path('searchdoctor/<int:user_id>', views.search_doctor_view, name='searchdoctor'),
    path('discharge/<int:user_id>', views.patient_discharge_view, name='patient-discharge'),
]

