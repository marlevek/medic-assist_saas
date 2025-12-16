from django.contrib import admin
from .models import Patient, MedicalRecord, Prescription

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'cpf', 'birth_date', 'gender', 'phone', 'doctor', 'created_at']
    list_filter = ['gender', 'doctor', 'created_at']
    search_fields = ['full_name', 'cpf', 'email', 'phone']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Médico Responsável', {
            'fields': ('doctor',)
        }),
        ('Informações Pessoais', {
            'fields': ('full_name', 'cpf', 'birth_date', 'gender', 'phone', 'email')
        }),
        ('Endereço', {
            'fields': (('street', 'number'), ('complement', 'neighborhood'), 
                      ('city', 'state', 'zipcode'))
        }),
        ('Informações Médicas', {
            'fields': ('blood_type', 'allergies', 'chronic_conditions')
        }),
        ('Sistema', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'complaint', 'diagnosis', 'created_at']
    list_filter = ['doctor', 'created_at']
    search_fields = ['patient__full_name', 'complaint', 'diagnosis']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Paciente', {
            'fields': ('patient', 'doctor')
        }),
        ('Consulta', {
            'fields': ('complaint', 'history', 'physical_exam', 'diagnosis', 'treatment_plan')
        }),
        ('Sinais Vitais', {
            'fields': ('weight', 'height', 'blood_pressure_sys', 'blood_pressure_dia', 
                      'heart_rate', 'temperature'),
            'classes': ('collapse',)
        }),
        ('IA Insights', {
            'fields': ('ai_suggestions', 'ai_risk_score'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medication_name', 'get_patient_name', 'dosage', 'frequency', 'created_at']
    list_filter = ['created_at']
    search_fields = ['medication_name', 'medical_record__patient__full_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def get_patient_name(self, obj):
        return obj.medical_record.patient.full_name
    get_patient_name.short_description = 'Paciente'