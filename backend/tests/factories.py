# tests/factories.py
import factory
from faker import Faker
from django.contrib.auth import get_user_model
from apps.resumes.models import Resume
from apps.job_posts.models import JobPost
from apps.applications.models import Application
from core.models import EmailCredential

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("testpass123")
        self.save()


class ResumeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resume

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Resume {n}")
    file = factory.django.FileField(filename="resume.pdf")
    extracted_text = factory.LazyAttribute(lambda _: fake.text(3000))
    is_primary = True


class JobPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobPost

    user = factory.SubFactory(UserFactory)
    company = factory.LazyAttribute(lambda _: fake.company())
    role = factory.LazyAttribute(lambda _: fake.job())
    skills = factory.LazyAttribute(lambda _: [fake.word() for _ in range(5)])
    hr_email = factory.LazyAttribute(lambda _: f"hr@{fake.domain_name()}")
    location = factory.LazyAttribute(lambda _: fake.city())
    is_parsed = True
    raw_text = factory.LazyAttribute(lambda _: fake.text(2000))


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    user = factory.SubFactory(UserFactory)
    job_post = factory.SubFactory(JobPostFactory)
    resume = factory.SubFactory(ResumeFactory)
    to_email = factory.LazyAttribute(lambda o: o.job_post.hr_email)
    subject = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))
    body = factory.LazyAttribute(lambda _: fake.text(500))
    status = "draft"


class EmailCredentialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailCredential

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda o: o.user.email)
    encrypted_password = factory.LazyAttribute(lambda _: fake.password())
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    is_verified = True