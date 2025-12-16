from django.contrib import admin
from .models import AIConversation

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'patient', 'get_query_preview', 'tokens_used', 'response_time', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['query', 'response', 'user__username', 'patient__full_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def get_query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    get_query_preview.short_description = 'Query'
    
    fieldsets = (
        ('Conversa', {
            'fields': ('user', 'patient', 'query', 'response')
        }),
        ('Métricas', {
            'fields': ('tokens_used', 'response_time', 'context'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )