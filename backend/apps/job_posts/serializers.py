# apps/job_posts/serializers.py

from rest_framework import serializers
from .models import JobPost


class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = (
            "id",
            "screenshot",
            "company",
            "role",
            "skills",
            "hr_email",
            "location",
            "raw_text",
            "is_parsed",
            "parse_error",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "company",
            "role",
            "skills",
            "hr_email",
            "location",
            "raw_text",
            "is_parsed",
            "parse_error",
            "created_at",
            "updated_at",
        )