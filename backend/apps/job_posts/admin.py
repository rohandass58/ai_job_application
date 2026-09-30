from django.contrib import admin
from .models import JobPost


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'company', 'role', 'hr_email', 'is_parsed', 'created_at']
    list_filter = ['is_parsed', 'created_at']
    search_fields = ['user__username', 'user__email', 'company', 'role', 'hr_email']
    readonly_fields = ['raw_text', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
