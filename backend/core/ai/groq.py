# backend/core/ai/groq.py

import json
import re
from typing import Any, Dict, Optional

from django.conf import settings
from groq import Groq

from core.exceptions import AIProviderError
from .base import LLMProvider


class GroqProvider(LLMProvider):
    """
    Groq implementation – used mainly for fast email generation.
    """

    def __init__(self):
        api_key = getattr(settings, "GROQ_API_KEY", None)
        if not api_key:
            raise AIProviderError("GROQ_API_KEY is not set in settings")

        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"

    def extract_jd(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        raise AIProviderError(
            "Groq does not support image vision well. Use GeminiProvider for extraction."
        )

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
Write a cold email for a student applying to a job.

Job Details:
- Company: {company}
- Role: {role}
- Required Skills: {skills}

Student Details:
- Name: {student_name}
- Email: {student_email}
- College: {college}
- Experience / Summary: {experience or resume_summary or "Fresher with strong fundamentals"}

Requirements:
1. Subject line should be short and professional.
2. Body should be 120-180 words max.
3. Mention 1-2 relevant skills from the job.
4. End with a clear call-to-action (ask for a short call or interview).
5. Do not use placeholders like [Name]. Use real values.
6. Return ONLY valid JSON in this exact format:
{{
  "subject": "the subject line",
  "body": "the full email body"
}}
"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.6,
                max_tokens=600,
            )

            text = completion.choices[0].message.content.strip()

            # Clean markdown if present
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"^```\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            data = json.loads(text)

            return {
                "subject": data.get("subject", f"Application for {role} at {company}"),
                "body": data.get("body", ""),
            }

        except json.JSONDecodeError as e:
            raise AIProviderError(f"Groq returned invalid JSON: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"Groq generate_email failed: {str(e)}")