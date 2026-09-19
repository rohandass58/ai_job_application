# backend/core/ai/gemini.py

import json
import re
from typing import Any, Dict, Optional

from django.conf import settings
from google import genai
from google.genai import types

from core.exceptions import AIProviderError
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Gemini implementation using the official google-genai SDK.
    Used primarily for screenshot → structured JD extraction.
    """

    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise AIProviderError("GEMINI_API_KEY is not set in settings")

        self.client = genai.Client(api_key=api_key)
        # Fast + cheap vision model
        self.model_name = "gemini-2.5-flash"

    def extract_jd(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        prompt = """
You are an expert job description parser.

Analyze the attached screenshot of a job posting and extract the following information.

Return ONLY a valid JSON object with these exact keys:
{
  "company": "string or empty",
  "role": "string or empty",
  "skills": ["skill1", "skill2"],
  "hr_email": "email or null",
  "location": "string or empty",
  "raw_text": "full readable text from the image"
}

Rules:
- If a field is not found, use empty string "" or null for hr_email.
- skills must be a list of strings.
- Do not add any extra text, markdown, or explanation. Only pure JSON.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    prompt,
                ],
            )

            text = response.text.strip()

            # Clean possible markdown code blocks
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"^```\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            data = json.loads(text)

            # Ensure required structure
            return {
                "company": data.get("company", "") or "",
                "role": data.get("role", "") or "",
                "skills": data.get("skills", []) or [],
                "hr_email": data.get("hr_email"),
                "location": data.get("location", "") or "",
                "raw_text": data.get("raw_text", "") or "",
            }

        except json.JSONDecodeError as e:
            raise AIProviderError(f"Gemini returned invalid JSON: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"Gemini extract_jd failed: {str(e)}")

    def generate_email(
        self,
        jd: Dict[str, Any],
        student_profile: Dict[str, Any],
        resume_summary: Optional[str] = None
    ) -> Dict[str, str]:
        # We prefer Groq for email generation, so this is optional
        raise AIProviderError("Use GroqProvider for email generation")