# patients/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients')
    full_name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Endereço completo
    street = models.CharField(max_length=255, verbose_name="Rua/Avenida")
    number = models.CharField(max_length=10, verbose_name="Número")
    complement = models.CharField(max_length=100, blank=True, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=100, verbose_name="Bairro")
    city = models.CharField(max_length=100, verbose_name="Cidade")
    state = models.CharField(max_length=2, verbose_name="Estado (UF)")
    zipcode = models.CharField(max_length=10, verbose_name="CEP")
    
    # Medical info
    blood_type = models.CharField(max_length=3, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doctor', 'full_name']),
            models.Index(fields=['cpf']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.cpf}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Consulta
    complaint = models.TextField(help_text="Queixa principal")
    history = models.TextField(help_text="História da doença atual")
    physical_exam = models.TextField(help_text="Exame físico")
    diagnosis = models.TextField(help_text="Hipótese diagnóstica")
    treatment_plan = models.TextField(help_text="Plano terapêutico")
    
    # Sinais vitais
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    blood_pressure_sys = models.IntegerField(null=True, blank=True)
    blood_pressure_dia = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    # IA Insights
    ai_suggestions = models.JSONField(default=dict, blank=True)
    ai_risk_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prontuário {self.patient.full_name} - {self.created_at.date()}"


class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    
    ai_interaction_check = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medication_name} - {self.medical_record.patient.full_name}"