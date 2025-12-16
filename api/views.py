# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from datetime import datetime, timedelta
from patients.models import Patient, MedicalRecord
from appointments.models import Appointment
from .serializers import PatientSerializer, MedicalRecordSerializer, AppointmentSerializer
from ai_assistant.services import MedicalAIAssistant, PredictiveAnalytics
import pandas as pd


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Patient.objects.filter(doctor=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)
    
    @action(detail=True, methods=['get'])
    def health_summary(self, request, pk=None):
        """Retorna resumo de saúde com análise de IA"""
        patient = self.get_object()
        
        # Coletar dados
        records = patient.records.all()[:10]
        vitals_history = [
            {
                'weight': r.weight,
                'height': r.height,
                'blood_pressure_sys': r.blood_pressure_sys,
                'blood_pressure_dia': r.blood_pressure_dia,
            }
            for r in records if r.weight
        ]
        
        # Calcular score de risco
        from datetime import date
        age = (date.today() - patient.birth_date).days // 365
        
        patient_data = {
            'age': age,
            'gender': patient.gender,
            'chronic_conditions': patient.chronic_conditions,
            'allergies': patient.allergies
        }
        
        risk_analysis = PredictiveAnalytics.calculate_health_risk_score(
            patient_data, 
            vitals_history
        )
        
        # Gerar resumo com IA
        ai = MedicalAIAssistant()
        records_data = [
            {
                'date': r.created_at.strftime('%Y-%m-%d'),
                'complaint': r.complaint,
                'diagnosis': r.diagnosis
            }
            for r in records
        ]
        summary = ai.generate_medical_summary(records_data)
        
        return Response({
            'patient': PatientSerializer(patient).data,
            'risk_analysis': risk_analysis,
            'ai_summary': summary,
            'total_consultations': records.count(),
            'last_visit': records.first().created_at if records.exists() else None
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas gerais de pacientes"""
        patients = self.get_queryset()
        
        return Response({
            'total_patients': patients.count(),
            'active_patients': patients.filter(is_active=True).count(),
            'gender_distribution': {
                'male': patients.filter(gender='M').count(),
                'female': patients.filter(gender='F').count(),
                'other': patients.filter(gender='O').count(),
            },
            'age_groups': self._get_age_distribution(patients),
            'patients_with_chronic': patients.exclude(chronic_conditions='').count()
        })
    
    def _get_age_distribution(self, patients):
        from datetime import date
        today = date.today()
        
        distribution = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}
        
        for p in patients:
            age = (today - p.birth_date).days // 365
            if age <= 18:
                distribution['0-18'] += 1
            elif age <= 35:
                distribution['19-35'] += 1
            elif age <= 50:
                distribution['36-50'] += 1
            elif age <= 65:
                distribution['51-65'] += 1
            else:
                distribution['65+'] += 1
        
        return distribution


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MedicalRecord.objects.filter(doctor=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)
    
    @action(detail=False, methods=['post'])
    def ai_assist(self, request):
        """Assistência de IA para diagnóstico"""
        symptoms = request.data.get('symptoms')
        patient_id = request.data.get('patient_id')
        
        if not symptoms or not patient_id:
            return Response(
                {'error': 'Sintomas e ID do paciente são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient = Patient.objects.get(id=patient_id, doctor=request.user)
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Paciente não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Preparar dados do paciente
        from datetime import date
        age = (date.today() - patient.birth_date).days // 365
        
        patient_data = {
            'age': age,
            'gender': patient.get_gender_display(),
            'chronic_conditions': patient.chronic_conditions,
            'allergies': patient.allergies
        }
        
        # Obter sugestões da IA
        ai = MedicalAIAssistant()
        suggestions = ai.get_differential_diagnosis(symptoms, patient_data)
        
        return Response(suggestions)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Consultas de hoje"""
        today = datetime.now().date()
        appointments = self.get_queryset().filter(
            date_time__date=today
        ).order_by('date_time')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Próximas consultas (próximos 7 dias)"""
        now = datetime.now()
        week_later = now + timedelta(days=7)
        
        appointments = self.get_queryset().filter(
            date_time__gte=now,
            date_time__lte=week_later,
            status__in=['scheduled', 'confirmed']
        ).order_by('date_time')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def predict_no_show(self, request, pk=None):
        """Prediz probabilidade de não comparecimento"""
        appointment = self.get_object()
        
        # Calcular dias até a consulta
        days_until = (appointment.date_time.date() - datetime.now().date()).days
        
        # Buscar histórico de não comparecimentos
        previous_no_shows = Appointment.objects.filter(
            patient=appointment.patient,
            status='no_show'
        ).count()
        
        appointment_data = {
            'days_until': days_until,
            'previous_no_shows': previous_no_shows,
            'hour': appointment.date_time.hour,
            'is_first': appointment.patient.appointments.count() == 1
        }
        
        probability = PredictiveAnalytics.predict_appointment_no_show(appointment_data)
        
        return Response({
            'appointment_id': appointment.id,
            'patient': appointment.patient.full_name,
            'no_show_probability': round(probability * 100, 2),
            'risk_level': 'Alto' if probability > 0.5 else 'Médio' if probability > 0.3 else 'Baixo',
            'recommendation': 'Enviar lembrete' if probability > 0.3 else 'Acompanhamento normal'
        })
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Analytics de consultas"""
        appointments = self.get_queryset()
        
        # Últimos 30 dias
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent = appointments.filter(date_time__gte=thirty_days_ago)
        
        return Response({
            'total_appointments': appointments.count(),
            'last_30_days': recent.count(),
            'by_status': {
                'completed': recent.filter(status='completed').count(),
                'scheduled': recent.filter(status='scheduled').count(),
                'cancelled': recent.filter(status='cancelled').count(),
                'no_show': recent.filter(status='no_show').count(),
            },
            'no_show_rate': self._calculate_no_show_rate(recent),
            'busiest_hours': self._get_busiest_hours(recent),
            'average_duration': recent.aggregate(avg=models.Avg('duration_minutes'))['avg']
        })
    
    def _calculate_no_show_rate(self, appointments):
        total = appointments.exclude(status='scheduled').count()
        if total == 0:
            return 0
        no_shows = appointments.filter(status='no_show').count()
        return round((no_shows / total) * 100, 2)
    
    def _get_busiest_hours(self, appointments):
        from django.db.models.functions import ExtractHour
        
        hours = appointments.annotate(
            hour=ExtractHour('date_time')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return list(hours)


class DashboardView(viewsets.ViewSet):
    """Dashboard principal com métricas e insights"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Visão geral do dashboard"""
        user = request.user
        
        # Pacientes
        total_patients = Patient.objects.filter(doctor=user, is_active=True).count()
        
        # Consultas
        today = datetime.now().date()
        appointments_today = Appointment.objects.filter(
            doctor=user,
            date_time__date=today
        ).count()
        
        # Consultas pendentes
        pending_appointments = Appointment.objects.filter(
            doctor=user,
            date_time__gte=datetime.now(),
            status='scheduled'
        ).count()
        
        # Últimos registros médicos
        recent_records = MedicalRecord.objects.filter(
            doctor=user
        ).order_by('-created_at')[:5]
        
        return Response({
            'total_patients': total_patients,
            'appointments_today': appointments_today,
            'pending_appointments': pending_appointments,
            'recent_consultations': MedicalRecordSerializer(recent_records, many=True).data,
            'timestamp': datetime.now().isoformat()
        })