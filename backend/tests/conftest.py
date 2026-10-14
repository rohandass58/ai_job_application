# tests/conftest.py
import os
import sys

import django
import pytest
from django.conf import settings

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

# Configure pytest-django
pytest_plugins = ["pytest_django"]

def pytest_configure(config):
    config.addinivalue_line("markers", "django_db: mark test as needing database")


@pytest.fixture(scope="session")
def django_db_setup():
    """Ensure database is set up for tests."""
    pass


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# Register factory fixtures
@pytest.fixture
def user_factory():
    from tests.factories import UserFactory
    return UserFactory


@pytest.fixture
def resume_factory():
    from tests.factories import ResumeFactory
    return ResumeFactory


@pytest.fixture
def job_post_factory():
    from tests.factories import JobPostFactory
    return JobPostFactory


@pytest.fixture
def application_factory():
    from tests.factories import ApplicationFactory
    return ApplicationFactory


@pytest.fixture
def email_credential_factory():
    from tests.factories import EmailCredentialFactory
    return EmailCredentialFactory
