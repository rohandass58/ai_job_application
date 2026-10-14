# tests/test_ai_providers.py
import pytest
import re
from unittest.mock import Mock, patch
from core.ai.groq import GroqProvider
from core.exceptions import AIProviderError


def make_mock_response(company, role):
    """Create a mock response with the given company and role."""
    return {
        "subject": f"Application for {role} at {company}",
        "body": f"Dear Hiring Manager,\n\nI am applying for the {role} position at {company}. My experience with Python and backend development aligns well with your requirements.\n\nI would love a 15-min call to discuss."
    }


@pytest.fixture
def mock_groq_success():
    """Mock successful Groq response that matches input."""
    with patch('core.ai.groq.Groq') as mock_client:
        def side_effect(*args, **kwargs):
            # Extract company and role from the user prompt in messages
            messages = kwargs.get('messages', [])
            user_content = ""
            for msg in messages:
                if msg.get('role') == 'user':
                    user_content = msg.get('content', '')
                    break
            
            # Try to extract company and role from the prompt
            company_match = re.search(r'Company:\s*(\w+)', user_content)
            role_match = re.search(r'Role:\s*([\w\s]+)', user_content)
            
            company = company_match.group(1) if company_match else "TestCompany"
            role = role_match.group(1).strip() if role_match else "TestRole"
            
            response_data = {
                "subject": f"Application for {role} at {company}",
                "body": f"Dear Hiring Manager,\n\nI am applying for the {role} position at {company}. My experience with Python and backend development aligns well with your requirements.\n\nI would love a 15-min call to discuss."
            }
            
            mock_completion = Mock()
            mock_completion.choices = [Mock(message=Mock(content=str(response_data).replace("'", '"')))]
            return mock_completion
        
        mock_client.return_value.chat.completions.create.side_effect = side_effect
        yield mock_client


@pytest.fixture
def mock_groq_empty_then_success():
    """Mock Groq that fails JSON mode then succeeds in plain mode."""
    with patch('core.ai.groq.Groq') as mock_client:
        mock_client.return_value.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content=""))]),  # JSON mode - empty
            Mock(choices=[Mock(message=Mock(content='{"subject": "Test Subject", "body": "Test body with concrete details."}'))]),  # Plain mode
        ]
        yield mock_client


class TestGroqProvider:
    """Test GroqProvider email generation."""

    def test_generates_valid_email_structure(self, mock_groq_success):
        """GroqProvider should return valid subject and body."""
        provider = GroqProvider()
        result = provider.generate_email(
            jd={"company": "Google", "role": "ML Engineer", "skills": ["Python", "PyTorch"]},
            student_profile={"name": "Rahul", "email": "rahul@test.com"},
            resume_summary="ML project with 94% accuracy using PyTorch. Django internship."
        )

        assert "subject" in result
        assert "body" in result
        assert isinstance(result["subject"], str)
        assert isinstance(result["body"], str)
        assert len(result["subject"]) > 5
        assert len(result["body"]) > 50

    def test_email_contains_company_and_role(self, mock_groq_success):
        """Generated email should mention company and role."""
        provider = GroqProvider()
        result = provider.generate_email(
            jd={"company": "Microsoft", "role": "Backend Engineer", "skills": ["Python", "Azure"]},
            student_profile={"name": "Test User", "email": "test@test.com"},
            resume_summary="Python backend experience."
        )

        assert "Microsoft" in result["subject"] or "Microsoft" in result["body"]
        assert "Backend Engineer" in result["subject"] or "Backend Engineer" in result["body"]

    def test_handles_json_mode_failure_then_plain_mode(self, mock_groq_empty_then_success):
        """Should retry in plain mode when JSON mode returns empty."""
        provider = GroqProvider()
        result = provider.generate_email(
            jd={"company": "Test", "role": "Dev", "skills": ["Python"]},
            student_profile={"name": "Test"},
            resume_summary="Python experience."
        )

        assert "subject" in result
        assert "body" in result

    def test_raises_on_empty_response(self):
        """Should raise AIProviderError when both modes return empty."""
        with patch('core.ai.groq.Groq') as mock_client:
            mock_client.return_value.chat.completions.create.return_value.choices = [
                Mock(message=Mock(content=""))
            ]

            provider = GroqProvider()
            with pytest.raises(AIProviderError, match="empty response"):
                provider.generate_email(
                    jd={"company": "Test", "role": "Dev", "skills": ["Python"]},
                    student_profile={"name": "Test"},
                    resume_summary="Experience."
                )

    def test_raises_on_invalid_json(self):
        """Should raise AIProviderError on invalid JSON."""
        with patch('core.ai.groq.Groq') as mock_client:
            mock_client.return_value.chat.completions.create.return_value.choices = [
                Mock(message=Mock(content="not valid json at all"))
            ]

            provider = GroqProvider()
            with pytest.raises(AIProviderError, match="invalid JSON"):
                provider.generate_email(
                    jd={"company": "Test", "role": "Dev", "skills": ["Python"]},
                    student_profile={"name": "Test"},
                    resume_summary="Experience."
                )

    def test_extract_jd_raises_not_implemented(self):
        """Groq extract_jd should raise NotImplementedError."""
        provider = GroqProvider()
        with pytest.raises(AIProviderError, match="Groq does not support image vision"):
            provider.extract_jd(b"fake image bytes")
