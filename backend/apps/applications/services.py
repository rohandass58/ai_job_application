# apps/applications/services.py

from django.utils import timezone
from core.ai.factory import get_llm_provider
from core.email.factory import get_email_sender
from core.exceptions import ValidationError, AIProviderError, EmailSendError
from apps.job_posts.models import JobPost
from apps.resumes.models import Resume
from .models import Application
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)
class ApplicationService:

    @staticmethod
    def create_application(user, job_post_id: int, resume_id: int | None = None) -> Application:
        try:
            job_post = JobPost.objects.get(id=job_post_id, user=user)
        except JobPost.DoesNotExist:
            raise ValidationError("Job post not found")

        resume = None
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=user)
            except Resume.DoesNotExist:
                raise ValidationError("Resume not found")
        else:
            # fallback to primary resume
            resume = Resume.objects.filter(user=user, is_primary=True).first()

        application = Application.objects.create(
            user=user,
            job_post=job_post,
            resume=resume,
            to_email=job_post.hr_email or "",
            status="draft",
        )
        return application

    @staticmethod
    def generate_email_draft(application: Application) -> Application:
        """
        Uses Groq to generate subject + body
        """
        student_profile = {
            "name": application.user.get_full_name() or application.user.username,
            "email": application.user.email,
            "first_name": application.user.first_name,
        }

        jd = {
            "company": application.job_post.company,
            "role": application.job_post.role,
            "skills": application.job_post.skills,
        }

        resume_summary = ""
        if application.resume and application.resume.extracted_text:
            resume_summary = application.resume.extracted_text[:5000]

        try:
            provider = get_llm_provider("groq")
            result = provider.generate_email(jd, student_profile, resume_summary)

            application.subject = result["subject"]
            application.body = result["body"]
            application.status = "ready"
            application.save()
            return application

        except Exception as e:
            application.status = "failed"
            application.error_message = str(e)
            application.save()
            raise AIProviderError(f"Failed to generate email: {str(e)}")

    @staticmethod
    def send_application(application: Application) -> Application:
        if application.status not in ["ready", "draft", "failed"]:
            raise ValidationError("This application was already sent")

        if not application.to_email:
            raise ValidationError("No recipient email found")

        if not application.subject or not application.body:
            raise ValidationError("Subject or body is empty")

        try:
            sender = get_email_sender(user=application.user)
            from_name = application.user.get_full_name() or application.user.username

            sender.send(
                to_email=application.to_email,
                subject=application.subject,
                body=application.body,
                from_name=from_name,
                reply_to=application.user.email,
                attachments=ApplicationService._resume_attachments(application),
            )

            application.status = "sent"
            application.sent_at = timezone.now()
            application.error_message = ""
            application.save()
            return application

        except Exception as e:
            application.status = "failed"
            application.error_message = str(e)
            application.save()
            raise EmailSendError(f"Failed to send email: {str(e)}")

    @staticmethod
    def _resume_attachments(application: Application) -> list:
        """
        Attach the chosen resume PDF. If the file is missing on disk we still
        send the email (without attachment) instead of failing the whole send.
        """
        resume = application.resume
        if not resume or not resume.file:
            return []

        try:
            resume.file.open("rb")
            content = resume.file.read()
        except Exception:
            logger.warning("Resume file unreadable for application id=%s", application.id)
            return []
        finally:
            try:
                resume.file.close()
            except Exception:
                pass

        name = f"{application.user.get_full_name() or application.user.username} - Resume.pdf"
        return [{"filename": name, "content": content, "mimetype": "application/pdf"}]