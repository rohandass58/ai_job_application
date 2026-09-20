# apps/applications/views.py

from core.views import BaseAPIView
from core.exceptions import ValidationError
from .models import Application
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationUpdateSerializer,
)
from .services import ApplicationService


class ApplicationCreateView(BaseAPIView):
    def post(self, request):
        serializer = ApplicationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(message="Invalid data", errors=serializer.errors)

        application = ApplicationService.create_application(
            user=request.user,
            job_post_id=serializer.validated_data["job_post_id"],
            resume_id=serializer.validated_data.get("resume_id"),
        )

        # Automatically generate the email draft
        application = ApplicationService.generate_email_draft(application)

        return self.success_response(
            data=ApplicationSerializer(application).data,
            message="Application created and email draft generated",
            status_code=201,
        )


class ApplicationListView(BaseAPIView):
    def get(self, request):
        apps = Application.objects.filter(user=request.user).select_related("job_post", "resume")
        serializer = ApplicationSerializer(apps, many=True)
        return self.success_response(data=serializer.data)


class ApplicationDetailView(BaseAPIView):
    def get(self, request, pk):
        try:
            app = Application.objects.get(pk=pk, user=request.user)
        except Application.DoesNotExist:
            raise ValidationError(message="Application not found", status_code=404)

        return self.success_response(data=ApplicationSerializer(app).data)

    def patch(self, request, pk):
        """Student can edit subject / body / to_email before sending"""
        try:
            app = Application.objects.get(pk=pk, user=request.user)
        except Application.DoesNotExist:
            raise ValidationError(message="Application not found", status_code=404)

        if app.status == "sent":
            raise ValidationError(message="Sent applications cannot be edited")

        serializer = ApplicationUpdateSerializer(app, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(message="Invalid data", errors=serializer.errors)

        serializer.save()
        app.status = "ready"
        app.save(update_fields=["status", "updated_at"])

        return self.success_response(
            data=ApplicationSerializer(app).data,
            message="Application updated"
        )


class ApplicationSendView(BaseAPIView):
    def post(self, request, pk):
        try:
            app = Application.objects.get(pk=pk, user=request.user)
        except Application.DoesNotExist:
            raise ValidationError(message="Application not found", status_code=404)

        app = ApplicationService.send_application(app)

        return self.success_response(
            data=ApplicationSerializer(app).data,
            message="Email sent successfully"
        )