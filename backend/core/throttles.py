# backend/core/throttles.py

from rest_framework.throttling import UserRateThrottle


class AIRateThrottle(UserRateThrottle):
    """Applied to endpoints that call Gemini/Groq (costly + quota-limited)."""
    scope = "ai"