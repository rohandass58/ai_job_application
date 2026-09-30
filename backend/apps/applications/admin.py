from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'job_post', 'status', 'to_email', 'sent_at', 'created_at']
    list_filter = ['status', 'created_at', 'sent_at']
    search_fields = ['user__username', 'user__email', 'job_post__company', 'job_post__role', 'to_email', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'error_message']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Info', {'fields': ('user', 'job_post', 'resume', 'status')}),
        ('Email', {'fields': ('to_email', 'subject', 'body')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'sent_at')}),
        ('Error', {'fields': ('error_message',)}),
    )
    
    actions = ['mark_as_sent', 'mark_as_failed', 'mark_as_draft']
    
    @admin.action(description='Mark selected as sent')
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} application(s) marked as sent.')
    
    @admin.action(description='Mark selected as failed')
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} application(s) marked as failed.')
    
    @admin.action(description='Mark selected as draft (retry)')
    def mark_as_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} application(s) marked as draft for retry.')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'job_post', 'resume')
