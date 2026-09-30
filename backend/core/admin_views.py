from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from apps.applications.models import Application
from apps.accounts.models import User
from apps.resumes.models import Resume
from apps.job_posts.models import JobPost
from core.models import EmailCredential


@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Key metrics
    total_users = User.objects.count()
    active_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    active_users_month = User.objects.filter(date_joined__gte=month_ago).count()
    
    total_apps = Application.objects.count()
    sent_apps = Application.objects.filter(status='sent').count()
    failed_apps = Application.objects.filter(status='failed').count()
    draft_apps = Application.objects.filter(status__in=['draft', 'ready']).count()
    
    apps_this_week = Application.objects.filter(created_at__gte=week_ago).count()
    apps_this_month = Application.objects.filter(created_at__gte=month_ago).count()
    
    # Recent activity
    recent_applications = Application.objects.select_related('user', 'job_post').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Status breakdown
    status_breakdown = list(Application.objects.values('status').annotate(count=Count('id')))
    
    # Weekly chart data (last 7 days)
    weekly_labels = []
    weekly_data = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = Application.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count()
        weekly_labels.append(day.strftime('%a'))
        weekly_data.append(count)
    
    # Users with Gmail configured
    users_with_gmail = User.objects.filter(email_credential__isnull=False).distinct().count()
    verified_gmail = User.objects.filter(email_credential__is_verified=True).distinct().count()
    users_with_resume = User.objects.filter(resumes__isnull=False).distinct().count()
    
    context = {
        'total_users': total_users,
        'active_users_week': active_users_week,
        'active_users_month': active_users_month,
        'total_apps': total_apps,
        'sent_apps': sent_apps,
        'failed_apps': failed_apps,
        'draft_apps': draft_apps,
        'apps_this_week': apps_this_week,
        'apps_this_month': apps_this_month,
        'recent_applications': recent_applications,
        'recent_users': recent_users,
        'status_breakdown': status_breakdown,
        'weekly_labels': weekly_labels,
        'weekly_data': weekly_data,
        'users_with_gmail': users_with_gmail,
        'verified_gmail': verified_gmail,
        'users_with_resume': users_with_resume,
        'success_rate': round((sent_apps / total_apps * 100) if total_apps else 0, 1),
        'gmail_adoption_rate': round((users_with_gmail / total_users * 100) if total_users else 0, 1),
    }
    return render(request, 'admin/dashboard.html', context)