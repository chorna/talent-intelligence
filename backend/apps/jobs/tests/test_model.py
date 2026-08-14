from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.candidates.models import Candidate
from apps.jobs.choices import (
    ApplicationStatus,
    EmploymentType,
    JobStatus,
    WorkMode,
)
from apps.jobs.models import (
    Application,
    Job,
)
from apps.locations.models import City, Country
from apps.users.models import User


class JobModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
        )

        self.country = Country.objects.create(
            name="Peru",
            code="PE",
        )

        self.city = City.objects.create(
            country=self.country,
            name="Lima",
        )

    def test_create_job(self):
        job = Job.objects.create(
            title="Senior Backend Engineer",
            description="Python and Django position.",
            city=self.city,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            created_by=self.user,
        )

        self.assertEqual(
            job.title,
            "Senior Backend Engineer",
        )
        self.assertEqual(
            job.status,
            JobStatus.DRAFT,
        )
        self.assertEqual(
            job.city,
            self.city,
        )
        self.assertEqual(
            job.created_by,
            self.user,
        )

    def test_remote_job_can_have_no_city(self):
        job = Job(
            title="Remote Backend Engineer",
            description="Fully remote position.",
            city=None,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            created_by=self.user,
        )

        job.full_clean()

        self.assertIsNone(job.city)

    def test_remote_job_cannot_have_city(self):
        job = Job(
            title="Remote Backend Engineer",
            description="Fully remote position.",
            city=self.city,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_hybrid_job_requires_city(self):
        job = Job(
            title="Hybrid Backend Engineer",
            description="Hybrid position.",
            city=None,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_on_site_job_requires_city(self):
        job = Job(
            title="Backend Engineer",
            description="On-site position.",
            city=None,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.ON_SITE,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()


class ApplicationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
        )

        self.country = Country.objects.create(
            name="Peru",
            code="PE",
        )

        self.city = City.objects.create(
            country=self.country,
            name="Lima",
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
            city=self.city,
        )

        self.job = Job.objects.create(
            title="Senior Backend Engineer",
            description="Python and Django position.",
            city=self.city,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            created_by=self.user,
        )

    def test_create_application(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertEqual(
            application.status,
            ApplicationStatus.NEW,
        )

    def test_application_candidate_job_is_unique(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        with self.assertRaises(Exception):
            Application.objects.create(
                candidate=self.candidate,
                job=self.job,
            )
