from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_primary', 'file_size_kb', 'text_length', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['user__username', 'user__email', 'title']
    readonly_fields = ['extracted_text', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def file_size_kb(self, obj):
        if obj.file:
            return f"{obj.file.size / 1024:.1f} KB"
        return "-"
    file_size_kb.short_description = 'Size'
    
    def text_length(self, obj):
        return f"{len(obj.extracted_text or '')} chars"
    text_length.short_description = 'Extracted Text'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
