from django.db import models
from patients.models import User, Patient, MedicalRecord



class AIConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    
    query = models.TextField()
    response = models.TextField()
    context = models.JSONField(default=dict)
    
    tokens_used = models.IntegerField(default=0)
    response_time = models.FloatField(help_text="Tempo de resposta em segundos")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversa {self.user.username} - {self.created_at}"


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
