from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date_time', 'status', 'appointment_type', 'duration_minutes']
    list_filter = ['status', 'doctor', 'date_time', 'appointment_type']
    search_fields = ['patient__full_name', 'notes']
    date_hierarchy = 'date_time'
    ordering = ['date_time']
    
    fieldsets = (
        ('Agendamento', {
            'fields': ('patient', 'doctor', 'date_time', 'duration_minutes', 'status')
        }),
        ('Detalhes', {
            'fields': ('appointment_type', 'notes')
        }),
        ('IA Optimization', {
            'fields': ('ai_suggested', 'priority_score'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_cancelled', 'mark_as_no_show']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} consulta(s) marcada(s) como realizadas.')
    mark_as_completed.short_description = 'Marcar como realizada'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} consulta(s) cancelada(s).')
    mark_as_cancelled.short_description = 'Cancelar consulta'
    
    def mark_as_no_show(self, request, queryset):
        updated = queryset.update(status='no_show')
        self.message_user(request, f'{updated} consulta(s) marcada(s) como não comparecimento.')
    mark_as_no_show.short_description = 'Marcar como não compareceu'

