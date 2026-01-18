from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'language', 'status', 'runtime', 'memory', 'created_at')
    list_filter = ('status', 'language', 'problem__difficulty', 'created_at')
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('created_at', 'updated_at', 'judge0_token')
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('user', 'problem', 'language', 'code')
        }),
        ('Results', {
            'fields': ('status', 'runtime', 'memory', 'error_message', 
                       'passed_test_cases', 'total_test_cases', 'failed_test_case')
        }),
        ('Metadata', {
            'fields': ('judge0_token', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
