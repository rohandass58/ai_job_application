# apps/applications/serializers.py

from rest_framework import serializers
from .models import Application
from apps.job_posts.serializers import JobPostSerializer
from apps.resumes.serializers import ResumeSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    job_post = JobPostSerializer(read_only=True)
    resume = ResumeSerializer(read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "job_post",
            "resume",
            "subject",
            "body",
            "to_email",
            "status",
            "error_message",
            "sent_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "error_message",
            "sent_at",
            "created_at",
            "updated_at",
        )


class ApplicationCreateSerializer(serializers.Serializer):
    job_post_id = serializers.IntegerField()
    resume_id = serializers.IntegerField(required=False, allow_null=True)


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """Used when student edits the email before sending"""

    class Meta:
        model = Application
        fields = ("subject", "body", "to_email")