from apps.candidates.models import Candidate
from apps.clients.models import Client
from apps.jobs.choices import (
    EmploymentType,
    JobStatus,
    WorkMode,
)
from apps.jobs.models.candidate_submission import CandidateSubmission
from apps.jobs.models.job import Job
from apps.locations.models import City, Country
from apps.organizations.models import Organization
from apps.users.models import User


class JobsTestMixin:
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
            organization=self.organization,
        )

        self.peru = Country.objects.create(
            name="Peru",
            code="PE",
        )

        self.lima = City.objects.create(
            country=self.peru,
            name="Lima",
        )

        self.client_obj = Client.objects.create(
            organization=self.organization,
            name="SONY",
        )

        self.job = Job.objects.create(
            title="Senior Backend Engineer",
            description="Python and Django backend engineer.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            client=self.client_obj,
            created_by=self.recruiter,
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
            city=self.lima,
        )

        self.other_organization = Organization.objects.create(
            name="Other Company",
        )

        self.other_recruiter = User.objects.create_user(
            email="other-recruiter@example.com",
            password="testpassword123",
            organization=self.other_organization,
        )

        self.other_job = Job.objects.create(
            title="Other Backend Engineer",
            description="Other company position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.other_organization,
            client=Client.objects.create(
                organization=self.other_organization,
                name="Other Client",
            ),
            created_by=self.other_recruiter,
        )

    def create_submission(self):
        return CandidateSubmission.objects.create(
            job=self.job,
            candidate=self.candidate,
            client=self.job.client,
            submitted_by=self.recruiter,
        )
