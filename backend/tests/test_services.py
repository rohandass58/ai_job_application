# tests/test_services.py
import pytest
from unittest.mock import Mock, patch
from core.exceptions import ValidationError
from apps.applications.services import ApplicationService
from apps.applications.models import Application
from apps.job_posts.models import JobPost
from apps.resumes.models import Resume
from core.exceptions import EmailSendError


@pytest.mark.django_db
class TestApplicationService:
    """Test ApplicationService business logic."""

    def test_create_application_with_valid_data(self, user_factory, job_post_factory, resume_factory):
        """Should create application with valid user, job, and resume."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)

        assert app.user == user
        assert app.job_post == job
        assert app.resume == resume
        assert app.status == "draft"
        assert app.to_email == job.hr_email

    def test_create_application_without_resume_uses_primary(self, user_factory, job_post_factory, resume_factory):
        """Should use primary resume when resume_id not provided."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume_factory(user=user, is_primary=False)
        primary_resume = resume_factory(user=user, is_primary=True)

        app = ApplicationService.create_application(user, job.id)

        assert app.resume == primary_resume

    def test_create_application_invalid_job_raises(self, user_factory, resume_factory):
        """Should raise ValidationError for non-existent job."""
        user = user_factory()
        resume = resume_factory(user=user)

        with pytest.raises(ValidationError, match="Job post not found"):
            ApplicationService.create_application(user, 99999, resume.id)

    def test_create_application_invalid_resume_raises(self, user_factory, job_post_factory):
        """Should raise ValidationError for non-existent resume."""
        user = user_factory()
        job = job_post_factory(user=user)

        with pytest.raises(ValidationError, match="Resume not found"):
            ApplicationService.create_application(user, job.id, 99999)

    def test_generate_email_draft_updates_status(self, user_factory, job_post_factory, resume_factory):
        """generate_email_draft should update status to 'ready'."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        assert app.status == "draft"

        with patch('apps.applications.services.get_llm_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate_email.return_value = {
                "subject": "Test Subject",
                "body": "Test body with enough content to pass validation."
            }
            mock_get_provider.return_value = mock_provider

            app = ApplicationService.generate_email_draft(app)

        assert app.status == "ready"
        assert app.subject == "Test Subject"
        assert app.body == "Test body with enough content to pass validation."

    def test_generate_email_draft_failed_sets_failed_status(self, user_factory, job_post_factory, resume_factory):
        """Should set status to 'failed' on AI error."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)

        with patch('apps.applications.services.get_llm_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate_email.side_effect = Exception("AI service down")
            mock_get_provider.return_value = mock_provider

            with pytest.raises(Exception):
                ApplicationService.generate_email_draft(app)

        app.refresh_from_db()
        assert app.status == "failed"
        assert "AI service down" in app.error_message

    @patch('apps.applications.services.get_email_sender')
    def test_send_application_success(self, mock_get_sender, user_factory, job_post_factory, resume_factory):
        """Should send email and update status to 'sent'."""
        user = user_factory()
        job = job_post_factory(user=user, hr_email="hr@test.com")
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        app.subject = "Test Subject"
        app.body = "Test body content"
        app.status = "ready"
        app.save()

        mock_sender = Mock()
        mock_sender.send.return_value = True
        mock_get_sender.return_value = mock_sender

        app = ApplicationService.send_application(app)

        assert app.status == "sent"
        assert app.sent_at is not None
        assert app.error_message == ""
        mock_sender.send.assert_called_once()

    @patch('apps.applications.services.get_email_sender')
    def test_send_application_failure_updates_status(self, mock_get_sender, user_factory, job_post_factory, resume_factory):
        """Should set status to 'failed' on send error."""
        user = user_factory()
        job = job_post_factory(user=user, hr_email="hr@test.com")
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        app.subject = "Test Subject"
        app.body = "Test body content"
        app.status = "ready"
        app.save()

        mock_sender = Mock()
        mock_sender.send.side_effect = Exception("SMTP auth failed")
        mock_get_sender.return_value = mock_sender

        with pytest.raises(EmailSendError):
            ApplicationService.send_application(app)

        app.refresh_from_db()
        assert app.status == "failed"
        assert "SMTP auth failed" in app.error_message

    def test_send_application_invalid_status_raises(self, user_factory, job_post_factory, resume_factory):
        """Should raise ValidationError for already sent application."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        app.status = "sent"
        app.save()

        with pytest.raises(ValidationError, match="already sent"):
            ApplicationService.send_application(app)

    def test_send_application_missing_email_raises(self, user_factory, job_post_factory, resume_factory):
        """Should raise ValidationError when no recipient email."""
        user = user_factory()
        job = job_post_factory(user=user, hr_email="")
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        app.subject = "Test"
        app.body = "Body"
        app.status = "ready"
        app.save()

        with pytest.raises(ValidationError, match="No recipient email"):
            ApplicationService.send_application(app)

    def test_send_application_missing_subject_or_body_raises(self, user_factory, job_post_factory, resume_factory):
        """Should raise ValidationError when subject or body empty."""
        user = user_factory()
        job = job_post_factory(user=user, hr_email="hr@test.com")
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        app.subject = ""
        app.body = "Body only"
        app.status = "ready"
        app.save()

        with pytest.raises(ValidationError, match="Subject or body is empty"):
            ApplicationService.send_application(app)

    def test_resume_attachments_returns_pdf(self, user_factory, job_post_factory, resume_factory):
        """_resume_attachments should return PDF attachment dict."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        attachments = ApplicationService._resume_attachments(app)

        assert len(attachments) == 1
        assert attachments[0]["mimetype"] == "application/pdf"
        assert "Resume.pdf" in attachments[0]["filename"]
        assert isinstance(attachments[0]["content"], bytes)

    def test_resume_attachments_missing_file_returns_empty(self, user_factory, job_post_factory, resume_factory):
        """_resume_attachments should return empty list if file missing."""
        user = user_factory()
        job = job_post_factory(user=user)
        resume = resume_factory(user=user)
        # Delete the file
        resume.file.delete(save=True)

        app = ApplicationService.create_application(user, job.id, resume.id)
        attachments = ApplicationService._resume_attachments(app)

        assert attachments == []

    def test_send_application_retry_from_failed(self, user_factory, job_post_factory, resume_factory):
        """Should allow retry from failed status."""
        user = user_factory()
        job = job_post_factory(user=user, hr_email="hr@test.com")
        resume = resume_factory(user=user)

        app = ApplicationService.create_application(user, job.id, resume.id)
        app.subject = "Test"
        app.body = "Body"
        app.status = "failed"
        app.error_message = "Previous error"
        app.save()

        with patch('apps.applications.services.get_email_sender') as mock_get_sender:
            mock_sender = Mock()
            mock_sender.send.return_value = True
            mock_get_sender.return_value = mock_sender

            app = ApplicationService.send_application(app)

            assert app.status == "sent"
            assert app.error_message == ""
