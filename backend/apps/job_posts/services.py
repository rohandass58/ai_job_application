# apps/job_posts/services.py

from core.ai.factory import get_llm_provider
from core.exceptions import ParsingError, AIProviderError
from .models import JobPost


class JobPostService:

    @staticmethod
    def create_and_parse(user, screenshot) -> JobPost:
        """
        1. Save the screenshot
        2. Call Gemini to extract JD
        3. Update the JobPost with extracted data
        """
        job_post = JobPost.objects.create(
            user=user,
            screenshot=screenshot
        )

        try:
            # Read image bytes
            image_bytes = job_post.screenshot.read()
            mime_type = job_post.screenshot.file.content_type or "image/jpeg"

            # Get LLM provider (Gemini by default)
            provider = get_llm_provider("gemini")
            extracted = provider.extract_jd(image_bytes, mime_type)

            # Update the job post
            job_post.company = extracted.get("company", "")
            job_post.role = extracted.get("role", "")
            job_post.skills = extracted.get("skills", [])
            job_post.hr_email = extracted.get("hr_email")
            job_post.location = extracted.get("location", "")
            job_post.raw_text = extracted.get("raw_text", "")
            job_post.is_parsed = True
            job_post.save()

            return job_post

        except Exception as e:
            job_post.parse_error = str(e)
            job_post.save(update_fields=["parse_error"])
            raise ParsingError(f"Failed to parse job screenshot: {str(e)}")