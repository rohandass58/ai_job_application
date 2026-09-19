# apps/job_posts/urls.py

from django.urls import path
from .views import JobPostUploadView, JobPostListView, JobPostDetailView

urlpatterns = [
    path("upload/", JobPostUploadView.as_view(), name="job-upload"),
    path("", JobPostListView.as_view(), name="job-list"),
    path("<int:pk>/", JobPostDetailView.as_view(), name="job-detail"),
]