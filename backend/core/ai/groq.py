# backend/core/ai/groq.py

import json
import logging
import re
from typing import Any, Dict, Optional

from django.conf import settings
from groq import Groq

from core.exceptions import AIProviderError
from .base import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    Groq implementation – used mainly for fast email generation.
    """

    def __init__(self):
        api_key = getattr(settings, "GROQ_API_KEY", None)
        if not api_key:
            raise AIProviderError("GROQ_API_KEY is not set in settings")

        self.client = Groq(api_key=api_key)
        self.model_name = getattr(settings, "GROQ_MODEL", "openai/gpt-oss-120b")

    def extract_jd(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        raise AIProviderError(
            "Groq does not support image vision well. Use GeminiProvider for extraction."
        )

    def _complete(self, messages, json_mode: bool) -> str:
        """One Groq call. Returns '' if JSON mode produced nothing."""
        kwargs = dict(
            model=self.model_name,
            messages=messages,
            temperature=0.6,
            max_tokens=1500,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            completion = self.client.chat.completions.create(**kwargs)
            return (completion.choices[0].message.content or "").strip()
        except Exception as e:
            # json_validate_failed with empty generation -> caller retries in plain mode
            if json_mode and "json_validate_failed" in str(e):
                logger.warning("Groq JSON mode failed, retrying plain: %s", str(e)[:200])
                return ""
            raise

    def generate_email(
        self,
        jd: Dict[str, Any],
        student_profile: Dict[str, Any],
        resume_summary: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a professional cold email.
        Returns {"subject": "...", "body": "..."}
        """

        company = jd.get("company", "the company")
        role = jd.get("role", "the role")
        skills = ", ".join(jd.get("skills", [])[:8]) or "relevant skills"

        student_name = student_profile.get("name") or student_profile.get("first_name", "Student")
        student_email = student_profile.get("email", "")
        college = student_profile.get("college", "")
        experience = student_profile.get("experience", "")

        system_prompt = """
You are an expert career coach who writes short, professional, and highly personalized cold emails for job applications.
Write in a polite, confident, and concise tone. Avoid fluff.
"""

        user_prompt = f"""
Write a cold email for a job applicant.

Job Details:
- Company: {company}
- Role: {role}
- Required Skills: {skills}

Applicant Details:
- Name: {student_name}
- Email: {student_email}
- College: {college}
- Resume text (use only facts stated here, do not invent anything): {experience or resume_summary or "Fresher with strong fundamentals"}

Requirements:
1. Subject line should be short and professional.
2. Body should be 120-180 words max.
3. From the applicant's resume, pick the 2-3 achievements or skills that best match the job's required skills, and mention them concretely (numbers if the resume has them). Do not summarise the whole resume.
4. End with a clear call-to-action (ask for a short call or interview).
5. Do not use placeholders like [Name]. Use real values.
6. Return ONLY valid JSON in this exact format:
{{
  "subject": "the subject line",
  "body": "the full email body"
}}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        text = ""
        try:
            text = self._complete(messages, json_mode=True)
            if not text:
                # JSON mode sometimes returns nothing; retry once in plain mode
                text = self._complete(messages, json_mode=False)
            if not text:
                raise AIProviderError("Groq returned an empty response")

            # Strip markdown fences, then pull out the {...} object if there is extra text
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"^```\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                text = match.group(0)

            data = json.loads(text)

            return {
                "subject": data.get("subject", f"Application for {role} at {company}"),
                "body": data.get("body", ""),
            }

        except AIProviderError:
            raise
        except json.JSONDecodeError as e:
            logger.error("Groq invalid JSON. Raw output: %r", text[:500])
            raise AIProviderError(f"Groq returned invalid JSON: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"Groq generate_email failed: {str(e)}")