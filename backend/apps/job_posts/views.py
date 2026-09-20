# apps/job_posts/views.py

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.parsers import MultiPartParser, FormParser

from core.views import BaseAPIView
from core.exceptions import ValidationError
from core.throttles import AIRateThrottle
from core.validators import validate_image_file
from .models import JobPost
from .serializers import JobPostSerializer
from .services import JobPostService


class JobPostUploadView(BaseAPIView):
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [AIRateThrottle]

    def post(self, request):
        if "screenshot" not in request.FILES:
            raise ValidationError(message="Screenshot is required")

        screenshot = request.FILES["screenshot"]
        try:
            validate_image_file(screenshot)
        except DjangoValidationError as e:
            raise ValidationError(message=e.messages[0])

        job_post = JobPostService.create_and_parse(
            user=request.user,
            screenshot=screenshot,
        )

        return self.success_response(
            data=JobPostSerializer(job_post).data,
            message="Job post parsed successfully",
            status_code=201,
        )


class JobPostListView(BaseAPIView):
    def get(self, request):
        jobs = JobPost.objects.filter(user=request.user)
        serializer = JobPostSerializer(jobs, many=True)
        return self.success_response(data=serializer.data)


class JobPostDetailView(BaseAPIView):
    def get(self, request, pk):
        try:
            job = JobPost.objects.get(pk=pk, user=request.user)
        except JobPost.DoesNotExist:
            raise ValidationError(message="Job post not found", status_code=404)

        return self.success_response(data=JobPostSerializer(job).data)