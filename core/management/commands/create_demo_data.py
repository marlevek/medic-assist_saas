from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from patients.models import Patient
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Cria dados de demonstração'

    def handle(self, *args, **kwargs):
        # Criar médico demo
        doctor, created = User.objects.get_or_create(
            username='demo_doctor',
            defaults={
                'email': 'doctor@medai.com',
                'first_name': 'Dr. Demo',
                'is_staff': True
            }
        )
        if created:
            doctor.set_password('demo123')
            doctor.save()
            self.stdout.write(self.style.SUCCESS('Médico demo criado'))

        # Criar pacientes demo
        patients_data = [
            {
                'full_name': 'João Silva',
                'cpf': '123.456.789-00',
                'birth_date': datetime(1980, 5, 15).date(),
                'gender': 'M',
                'phone': '(41) 99999-0001',
                'email': 'joao@email.com',
                'address': 'Rua das Flores, 123',
                'blood_type': 'O+',
                'chronic_conditions': 'Hipertensão'
            },
            {
                'full_name': 'Maria Santos',
                'cpf': '987.654.321-00',
                'birth_date': datetime(1995, 8, 20).date(),
                'gender': 'F',
                'phone': '(41) 99999-0002',
                'email': 'maria@email.com',
                'address': 'Av. Principal, 456',
                'blood_type': 'A+',
                'allergies': 'Dipirona'
            }
        ]

        for data in patients_data:
            Patient.objects.get_or_create(
                cpf=data['cpf'],
                defaults={**data, 'doctor': doctor}
            )

        self.stdout.write(self.style.SUCCESS('Dados demo criados com sucesso!'))