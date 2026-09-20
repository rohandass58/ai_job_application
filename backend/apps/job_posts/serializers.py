# apps/job_posts/serializers.py

from rest_framework import serializers
from .models import JobPost
from core.validators import validate_image_file



class JobPostSerializer(serializers.ModelSerializer):
    screenshot = serializers.ImageField(validators=[validate_image_file])

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