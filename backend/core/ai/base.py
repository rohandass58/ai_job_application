# backend/core/ai/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMProvider(ABC):
    """
    Abstract interface for all LLM providers (Gemini, Groq, etc.).
    Any new provider must implement these two methods.
    """

    @abstractmethod
    def extract_jd(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Extract structured job data from a screenshot.

        Returns a dictionary with at least these keys:
        {
            "company": str,
            "role": str,
            "skills": list[str],
            "hr_email": Optional[str],
            "location": Optional[str],
            "raw_text": str
        }
        """
        pass

    @abstractmethod
    def generate_email(
        self,
        jd: Dict[str, Any],
        student_profile: Dict[str, Any],
        resume_summary: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a professional cold email.

        Returns:
        {
            "subject": str,
            "body": str
        }
        """
        pass