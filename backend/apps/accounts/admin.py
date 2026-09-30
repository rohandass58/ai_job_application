from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from core.models import EmailCredential


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'application_count', 'has_gmail']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'
    
    def has_gmail(self, obj):
        return hasattr(obj, 'email_credential') and obj.email_credential.is_verified
    has_gmail.boolean = True
    has_gmail.short_description = 'Gmail ✅'


@admin.register(EmailCredential)
class EmailCredentialAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'smtp_host', 'smtp_port', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at', 'smtp_host']
    search_fields = ['user__username', 'user__email', 'email']
    readonly_fields = ['encrypted_password', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # Users create their own via API
