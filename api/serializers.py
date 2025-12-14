# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, MedicalRecord, Appointment, Prescription, AIConversation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    total_appointments = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'full_name', 'cpf', 'birth_date', 'age', 'gender',
            'phone', 'email', 'address', 'blood_type', 'allergies',
            'chronic_conditions', 'created_at', 'updated_at',
            'total_appointments'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return (today - obj.birth_date).days // 365
    
    def get_total_appointments(self, obj):
        return obj.appointments.count()


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            'id', 'medication_name', 'dosage', 'frequency',
            'duration', 'instructions', 'ai_interaction_check',
            'created_at'
        ]


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    bmi = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'complaint', 'history', 'physical_exam', 'diagnosis',
            'treatment_plan', 'weight', 'height', 'bmi',
            'blood_pressure_sys', 'blood_pressure_dia',
            'heart_rate', 'temperature', 'ai_suggestions',
            'ai_risk_score', 'prescriptions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['doctor', 'created_at', 'updated_at']
    
    def get_bmi(self, obj):
        if obj.weight and obj.height and obj.height > 0:
            bmi = float(obj.weight) / (float(obj.height) ** 2)
            return round(bmi, 2)
        return None


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone',
            'doctor', 'doctor_name', 'date_time', 'duration_minutes',
            'status', 'appointment_type', 'notes', 'ai_suggested',
            'priority_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['doctor', 'created_at', 'updated_at']
    
    def validate_date_time(self, value):
        """Valida se a data/hora é futura"""
        from datetime import datetime
        if value < datetime.now():
            raise serializers.ValidationError(
                "Não é possível agendar consultas no passado"
            )
        return value


class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = [
            'id', 'patient', 'query', 'response', 'context',
            'tokens_used', 'response_time', 'created_at'
        ]
        read_only_fields = ['created_at']