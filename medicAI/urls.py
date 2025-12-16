from django.contrib import admin
from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from api.views import (
    PatientViewSet, MedicalRecordViewSet, 
    AppointmentViewSet, DashboardView
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'records', MedicalRecordViewSet, basename='record')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'dashboard', DashboardView, basename='dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]