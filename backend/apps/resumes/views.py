# apps/resumes/views.py

from rest_framework.parsers import MultiPartParser, FormParser
from core.views import BaseAPIView
from core.exceptions import ValidationError
from .models import Resume
from .serializers import ResumeSerializer


class ResumeUploadView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResumeSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                message="Resume upload failed",
                errors=serializer.errors
            )

        # If this is set as primary, unset previous primary resumes
        if serializer.validated_data.get("is_primary", True):
            Resume.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

        resume = serializer.save(user=request.user)
        return self.success_response(
            data=ResumeSerializer(resume).data,
            message="Resume uploaded successfully",
            status_code=201
        )


class ResumeListView(BaseAPIView):
    def get(self, request):
        resumes = Resume.objects.filter(user=request.user)
        serializer = ResumeSerializer(resumes, many=True)
        return self.success_response(data=serializer.data)