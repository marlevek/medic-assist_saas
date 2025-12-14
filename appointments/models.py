from django.db import models
from patients.models import User, Patient, MedicalRecord


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Agendado'),
        ('confirmed', 'Confirmado'),
        ('completed', 'Realizado'),
        ('cancelled', 'Cancelado'),
        ('no_show', 'Não compareceu'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    
    date_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    appointment_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    
    # IA scheduling optimization
    ai_suggested = models.BooleanField(default=False)
    priority_score = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_time']
        indexes = [
            models.Index(fields=['doctor', 'date_time']),
            models.Index(fields=['patient', 'date_time']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.date_time}"

