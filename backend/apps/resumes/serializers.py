from rest_framework import serializers
from core.validators import validate_resume_file
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_resume_file])
    has_text = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ("id", "title", "file", "is_primary", "has_text", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def get_has_text(self, obj) -> bool:
        return bool(obj.extracted_text)