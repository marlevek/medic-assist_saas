# ai_assistant/services.py
import anthropic
from django.conf import settings
import json
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# ai_assistant/services.py
from django.conf import settings
import json
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import time
import random

class MedicalAIAssistant:
    """Assistente de IA médica - Versão com Mock para desenvolvimento"""
    
    def __init__(self):
        # Verifica se tem API key real ou usa mock
        self.use_mock = not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == 'sk-ant-fake-key-for-development'
        
        if not self.use_mock:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.model = "claude-sonnet-4-20250514"
            except:
                self.use_mock = True
    
    def get_differential_diagnosis(self, symptoms, patient_data):
        """Gera diagnóstico diferencial baseado em sintomas"""
        
        if self.use_mock:
            return self._mock_differential_diagnosis(symptoms, patient_data)
        
        prompt = f"""Você é um assistente médico especializado. Analise os seguintes dados:

Sintomas/Queixa: {symptoms}

Dados do Paciente:
- Idade: {patient_data.get('age')} anos
- Sexo: {patient_data.get('gender')}
- Condições crônicas: {patient_data.get('chronic_conditions', 'Nenhuma')}
- Alergias: {patient_data.get('allergies', 'Nenhuma')}

Forneça:
1. Top 5 diagnósticos diferenciais mais prováveis (com probabilidade estimada)
2. Exames complementares sugeridos
3. Red flags (sinais de alerta)
4. Orientações gerais de conduta

Responda em formato JSON estruturado."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text
            
            return json.loads(json_str)
        
        except Exception as e:
            return {
                "error": str(e),
                "fallback": "Não foi possível gerar sugestões no momento"
            }
    
    def _mock_differential_diagnosis(self, symptoms, patient_data):
        """Mock para desenvolvimento sem API"""
        time.sleep(0.5)  # Simula latência da API
        
        # Análise básica dos sintomas para mock inteligente
        symptoms_lower = symptoms.lower()
        
        # Base de conhecimento mock
        diagnoses_db = {
            'dor de cabeça': {
                'diagnoses': [
                    {'name': 'Cefaleia Tensional', 'probability': 45},
                    {'name': 'Enxaqueca', 'probability': 30},
                    {'name': 'Cefaleia em Salvas', 'probability': 15},
                    {'name': 'Hipertensão Arterial', 'probability': 7},
                    {'name': 'Tumor Cerebral (raro)', 'probability': 3}
                ],
                'exams': ['Aferição de PA', 'TC de crânio (se sinais de alerta)', 'Hemograma'],
                'red_flags': ['Cefaleia súbita intensa', 'Alteração de consciência', 'Sinais neurológicos focais'],
                'conduct': 'Analgésicos simples, orientações posturais, acompanhamento'
            },
            'febre': {
                'diagnoses': [
                    {'name': 'Infecção Viral (Gripe/Resfriado)', 'probability': 50},
                    {'name': 'Infecção Bacteriana', 'probability': 25},
                    {'name': 'COVID-19', 'probability': 15},
                    {'name': 'Dengue', 'probability': 7},
                    {'name': 'Infecção Urinária', 'probability': 3}
                ],
                'exams': ['Hemograma completo', 'PCR/VHS', 'Teste para COVID-19', 'Urina tipo 1'],
                'red_flags': ['Febre >39°C persistente', 'Dispneia', 'Alteração de consciência', 'Petéquias'],
                'conduct': 'Antitérmicos, hidratação, repouso, antibiótico se indicado'
            },
            'dor torácica': {
                'diagnoses': [
                    {'name': 'Dor Musculoesquelética', 'probability': 35},
                    {'name': 'Refluxo Gastroesofágico', 'probability': 25},
                    {'name': 'Angina Estável', 'probability': 20},
                    {'name': 'Infarto Agudo do Miocárdio', 'probability': 15},
                    {'name': 'Embolia Pulmonar', 'probability': 5}
                ],
                'exams': ['ECG urgente', 'Troponina', 'RX de tórax', 'D-dímero se indicado'],
                'red_flags': ['Dor em aperto irradiando', 'Sudorese', 'Dispneia', 'Síncope'],
                'conduct': '⚠️ ATENÇÃO: Considerar atendimento de emergência. ECG imediato'
            },
            'tosse': {
                'diagnoses': [
                    {'name': 'Infecção Viral das Vias Aéreas', 'probability': 45},
                    {'name': 'Bronquite Aguda', 'probability': 25},
                    {'name': 'Pneumonia', 'probability': 15},
                    {'name': 'Asma/DPOC exacerbado', 'probability': 10},
                    {'name': 'Tuberculose', 'probability': 5}
                ],
                'exams': ['RX de tórax', 'Ausculta pulmonar', 'Oximetria', 'Espirometria se indicado'],
                'red_flags': ['Dispneia importante', 'Hemoptise', 'Febre alta persistente', 'Perda de peso'],
                'conduct': 'Avaliar necessidade de antibiótico, broncodilatador se indicado'
            }
        }
        
        # Encontra melhor match
        best_match = None
        for key in diagnoses_db.keys():
            if key in symptoms_lower:
                best_match = diagnoses_db[key]
                break
        
        # Se não encontrou match específico, usa genérico
        if not best_match:
            best_match = {
                'diagnoses': [
                    {'name': 'Diagnóstico diferencial requer avaliação clínica', 'probability': 40},
                    {'name': 'Condição benigna autolimitada', 'probability': 30},
                    {'name': 'Necessário exames complementares', 'probability': 20},
                    {'name': 'Encaminhar para especialista', 'probability': 10}
                ],
                'exams': ['Hemograma', 'Exames de rotina conforme idade', 'Exames específicos conforme queixa'],
                'red_flags': ['Sintomas graves ou progressivos', 'Alteração de sinais vitais', 'Sintomas sistêmicos'],
                'conduct': 'Avaliação clínica detalhada necessária'
            }
        
        # Adiciona contexto do paciente
        age_context = ""
        if patient_data.get('age', 0) > 60:
            age_context = " Considerar comorbidades relacionadas à idade."
        elif patient_data.get('age', 0) < 18:
            age_context = " Considerar diagnósticos pediátricos."
        
        return {
            'differential_diagnoses': best_match['diagnoses'],
            'recommended_exams': best_match['exams'],
            'red_flags': best_match['red_flags'],
            'general_conduct': best_match['conduct'] + age_context,
            'confidence_score': random.randint(75, 95),
            'mock_mode': True,
            'note': '⚠️ Usando modo MOCK - Ative API real para diagnósticos precisos'
        }
    
    def analyze_prescription_interactions(self, medications):
        """Analisa interações medicamentosas"""
        
        if self.use_mock:
            return self._mock_prescription_interactions(medications)
        
        prompt = f"""Analise as seguintes medicações para possíveis interações:

{json.dumps(medications, indent=2)}

Forneça:
1. Interações medicamentosas graves (se houver)
2. Interações moderadas
3. Precauções especiais
4. Sugestões de ajuste

Responda em JSON."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text
            
            return json.loads(json_str)
        
        except Exception as e:
            return {"error": str(e)}
    
    def _mock_prescription_interactions(self, medications):
        """Mock para análise de interações"""
        time.sleep(0.3)
        
        # Base de interações conhecidas
        known_interactions = {
            ('varfarina', 'aspirina'): {
                'severity': 'grave',
                'description': 'Risco aumentado de sangramento'
            },
            ('captopril', 'espironolactona'): {
                'severity': 'moderada',
                'description': 'Risco de hipercalemia'
            },
            ('sinvastatina', 'amiodarona'): {
                'severity': 'moderada',
                'description': 'Risco de miopatia/rabdomiólise'
            }
        }
        
        interactions_found = []
        
        # Simula verificação de interações
        med_names = [m.get('name', '').lower() if isinstance(m, dict) else str(m).lower() 
                     for m in medications]
        
        for i, med1 in enumerate(med_names):
            for med2 in med_names[i+1:]:
                # Verifica interações conhecidas
                key = tuple(sorted([med1, med2]))
                if key in known_interactions:
                    interactions_found.append({
                        'medications': [med1, med2],
                        'severity': known_interactions[key]['severity'],
                        'description': known_interactions[key]['description']
                    })
        
        return {
            'severe_interactions': [i for i in interactions_found if i['severity'] == 'grave'],
            'moderate_interactions': [i for i in interactions_found if i['severity'] == 'moderada'],
            'precautions': [
                'Monitorar função renal regularmente',
                'Avaliar sinais de sangramento',
                'Acompanhar efeitos adversos'
            ],
            'suggestions': [
                'Considerar ajuste de dose conforme função renal',
                'Monitorar níveis séricos quando aplicável'
            ],
            'total_interactions': len(interactions_found),
            'mock_mode': True
        }
    
    def generate_medical_summary(self, medical_records):
        """Gera resumo da história clínica do paciente"""
        
        if self.use_mock:
            return self._mock_medical_summary(medical_records)
        
        records_text = "\n\n".join([
            f"Data: {r.get('date')}\n"
            f"Queixa: {r.get('complaint')}\n"
            f"Diagnóstico: {r.get('diagnosis')}"
            for r in medical_records[-5:]
        ])
        
        prompt = f"""Gere um resumo executivo da história clínica deste paciente:

{records_text}

Inclua:
1. Padrões identificados
2. Evolução do quadro
3. Pontos de atenção
4. Recomendações de follow-up"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            return f"Erro ao gerar resumo: {str(e)}"
    
    def _mock_medical_summary(self, medical_records):
        """Mock para resumo médico"""
        time.sleep(0.4)
        
        if not medical_records or len(medical_records) == 0:
            return """📋 RESUMO CLÍNICO (Mock)

Paciente sem histórico de consultas anteriores registradas no sistema.

RECOMENDAÇÕES:
- Realizar anamnese completa
- Solicitar exames de rotina conforme idade
- Estabelecer plano de acompanhamento

⚠️ Modo MOCK ativo - Ative API real para análises precisas"""
        
        num_records = len(medical_records)
        
        # Análise básica dos registros
        complaints = [r.get('complaint', '') for r in medical_records if r.get('complaint')]
        diagnoses = [r.get('diagnosis', '') for r in medical_records if r.get('diagnosis')]
        
        summary = f"""📋 RESUMO CLÍNICO (Mock)

HISTÓRICO: {num_records} consulta(s) registrada(s)

PADRÕES IDENTIFICADOS:
- Queixas principais: {', '.join(complaints[:3]) if complaints else 'Não especificadas'}
- Diagnósticos prévios: {', '.join(diagnoses[:3]) if diagnoses else 'Não especificados'}

EVOLUÇÃO DO QUADRO:
O paciente apresenta acompanhamento {"regular" if num_records > 3 else "inicial"} no sistema.
{"Histórico sugere necessidade de seguimento contínuo." if num_records > 2 else "Estabelecer baseline para futuras comparações."}

PONTOS DE ATENÇÃO:
- Avaliar adesão ao tratamento prescrito
- Monitorar evolução dos sintomas
- Considerar necessidade de exames complementares

RECOMENDAÇÕES DE FOLLOW-UP:
- Retorno em {"30 dias" if num_records < 3 else "60-90 dias"}
- Monitoramento de sinais vitais
- Reavaliação terapêutica se necessário

---
⚠️ Modo MOCK ativo - Ative API real da Anthropic para análises detalhadas e precisas
Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        return summary


class PredictiveAnalytics:
    """Ciência de dados e modelos preditivos"""
    
    @staticmethod
    def calculate_health_risk_score(patient_data, vitals_history):
        """
        Calcula score de risco de saúde (0-100)
        Baseado em sinais vitais e histórico
        """
        
        risk_factors = {
            'age': 0,
            'chronic_conditions': 0,
            'vitals': 0,
            'adherence': 0
        }
        
        # Idade
        age = patient_data.get('age', 0)
        if age > 65:
            risk_factors['age'] = 25
        elif age > 50:
            risk_factors['age'] = 15
        elif age > 40:
            risk_factors['age'] = 5
        
        # Condições crônicas
        chronic = patient_data.get('chronic_conditions', '').lower()
        high_risk_conditions = ['diabetes', 'hipertensão', 'cardiopatia', 'câncer']
        risk_factors['chronic_conditions'] = sum(15 for c in high_risk_conditions if c in chronic)
        
        # Análise de sinais vitais
        if vitals_history:
            latest_vitals = vitals_history[-1]
            
            # Pressão arterial
            bp_sys = latest_vitals.get('blood_pressure_sys', 120)
            if bp_sys > 140 or bp_sys < 90:
                risk_factors['vitals'] += 20
            
            # IMC
            weight = latest_vitals.get('weight', 70)
            height = latest_vitals.get('height', 1.70)
            if height > 0:
                bmi = weight / (height ** 2)
                if bmi > 30 or bmi < 18.5:
                    risk_factors['vitals'] += 15
        
        # Total score (normalizado para 0-100)
        total_score = min(100, sum(risk_factors.values()))
        
        return {
            'total_score': total_score,
            'risk_level': 'Baixo' if total_score < 30 else 'Médio' if total_score < 60 else 'Alto',
            'factors': risk_factors,
            'recommendations': PredictiveAnalytics._get_recommendations(risk_factors)
        }
    
    @staticmethod
    def _get_recommendations(risk_factors):
        """Gera recomendações baseadas nos fatores de risco"""
        recommendations = []
        
        if risk_factors['age'] > 0:
            recommendations.append("Realizar check-up geriátrico anual")
        
        if risk_factors['chronic_conditions'] > 20:
            recommendations.append("Consultas de acompanhamento a cada 3 meses")
        
        if risk_factors['vitals'] > 15:
            recommendations.append("Monitoramento frequente de sinais vitais")
        
        return recommendations
    
    @staticmethod
    def predict_appointment_no_show(appointment_data):
        """
        Prediz probabilidade de não comparecimento
        Modelo simplificado - em produção, treinar com dados reais
        """
        
        features = {
            'days_until_appointment': appointment_data.get('days_until', 0),
            'previous_no_shows': appointment_data.get('previous_no_shows', 0),
            'appointment_hour': appointment_data.get('hour', 14),
            'is_first_appointment': appointment_data.get('is_first', False)
        }
        
        # Score simplificado
        probability = 0.1  # Base 10%
        
        if features['days_until_appointment'] > 30:
            probability += 0.2
        
        if features['previous_no_shows'] > 0:
            probability += 0.3
        
        if features['appointment_hour'] < 8 or features['appointment_hour'] > 17:
            probability += 0.15
        
        if features['is_first_appointment']:
            probability += 0.1
        
        return min(1.0, probability)
    
    @staticmethod
    def analyze_patient_trends(medical_records_df):
        """Analisa tendências nos dados do paciente"""
        
        if len(medical_records_df) < 3:
            return {"message": "Dados insuficientes para análise de tendências"}
        
        trends = {}
        
        # Análise de peso
        if 'weight' in medical_records_df.columns:
            weight_trend = np.polyfit(
                range(len(medical_records_df)), 
                medical_records_df['weight'].fillna(method='ffill'), 
                1
            )[0]
            trends['weight'] = {
                'direction': 'aumentando' if weight_trend > 0 else 'diminuindo',
                'rate': abs(weight_trend),
                'concern': abs(weight_trend) > 0.5  # Mais de 0.5kg por consulta
            }
        
        # Análise de pressão arterial
        if 'blood_pressure_sys' in medical_records_df.columns:
            bp_mean = medical_records_df['blood_pressure_sys'].mean()
            bp_std = medical_records_df['blood_pressure_sys'].std()
            
            trends['blood_pressure'] = {
                'mean': bp_mean,
                'variability': bp_std,
                'concern': bp_mean > 140 or bp_std > 20
            }
        
        return trends


class SmartScheduling:
    """Sistema inteligente de agendamento"""
    
    @staticmethod
    def suggest_optimal_appointment_time(doctor_id, patient_priority, existing_appointments):
        """Sugere melhor horário para consulta baseado em padrões"""
        
        # Análise de horários disponíveis
        # Lógica simplificada - expandir com ML
        
        morning_slots = [8, 9, 10, 11]
        afternoon_slots = [14, 15, 16, 17]
        
        if patient_priority == 'high':
            preferred_slots = morning_slots
        else:
            preferred_slots = afternoon_slots
        
        return {
            'suggested_times': preferred_slots,
            'reason': 'Baseado em prioridade e disponibilidade',
            'alternatives': morning_slots + afternoon_slots
        }