from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.jobs.choices import (
    ApplicationStatus,
    EmploymentType,
    JobStatus,
    WorkMode,
)
from apps.jobs.models import Application, Job
from apps.locations.models import City, Country
from apps.organizations.models import Organization

User = get_user_model()


class JobViewSetTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.other_organization = Organization.objects.create(
            name="Other Company",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
            organization=self.organization,
        )

        self.second_recruiter = User.objects.create_user(
            email="recruiter2@example.com",
            password="testpassword123",
            organization=self.organization,
        )

        self.other_recruiter = User.objects.create_user(
            email="other-recruiter@example.com",
            password="testpassword123",
            organization=self.other_organization,
        )

        self.unassigned_user = User.objects.create_user(
            email="unassigned@example.com",
            password="testpassword123",
        )

        self.url = "/api/jobs/"

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        self.peru = Country.objects.create(
            name="Peru",
            code="PE",
        )

        self.colombia = Country.objects.create(
            name="Colombia",
            code="CO",
        )

        self.lima = City.objects.create(
            country=self.peru,
            name="Lima",
        )

        self.bogota = City.objects.create(
            country=self.colombia,
            name="Bogota",
        )

        self.job = Job.objects.create(
            title="Senior Backend Engineer",
            description="Python Django backend engineer.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        self.other_job = Job.objects.create(
            title="Other Backend Engineer",
            description="Other company position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            organization=self.other_organization,
            created_by=self.other_recruiter,
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
            city=self.lima,
        )

    def test_list_jobs(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_retrieve_job(self):
        response = self.client.get(
            f"{self.url}{self.job.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            str(self.job.id),
        )

    def test_create_job(self):
        data = {
            "title": "Python Developer",
            "description": "Backend developer.",
            "city": str(self.lima.id),
            "employment_type": EmploymentType.FULL_TIME,
            "work_mode": WorkMode.HYBRID,
            "status": JobStatus.OPEN,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        job = Job.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            job.created_by,
            self.recruiter,
        )

    def test_create_remote_job_without_city(self):
        data = {
            "title": "Remote Python Developer",
            "description": "Fully remote.",
            "city": None,
            "employment_type": EmploymentType.FULL_TIME,
            "work_mode": WorkMode.REMOTE,
            "status": JobStatus.OPEN,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        job = Job.objects.get(
            id=response.data["id"],
        )

        self.assertIsNone(job.city)

    def test_remote_job_with_city_is_rejected(self):
        data = {
            "title": "Remote Python Developer",
            "description": "Fully remote.",
            "city": str(self.lima.id),
            "employment_type": EmploymentType.FULL_TIME,
            "work_mode": WorkMode.REMOTE,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "city",
            response.data,
        )

    def test_hybrid_job_without_city_is_rejected(self):
        data = {
            "title": "Hybrid Python Developer",
            "description": "Hybrid position.",
            "city": None,
            "employment_type": EmploymentType.FULL_TIME,
            "work_mode": WorkMode.HYBRID,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_filter_jobs_by_status(self):
        Job.objects.create(
            title="Draft Job",
            description="Draft position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.DRAFT,
            created_by=self.recruiter,
        )

        response = self.client.get(
            f"{self.url}?status=open",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_jobs_by_work_mode(self):
        Job.objects.create(
            title="Remote Job",
            description="Remote position.",
            city=None,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            status=JobStatus.OPEN,
            created_by=self.recruiter,
            organization=self.organization,
        )

        response = self.client.get(
            f"{self.url}?work_mode=remote",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_jobs_by_city(self):
        response = self.client.get(
            f"{self.url}?city=Lima",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_jobs_by_country(self):
        response = self.client.get(
            f"{self.url}?country=PE",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_search_jobs(self):
        response = self.client.get(
            f"{self.url}?search=Python",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_unauthenticated_user_cannot_list_jobs(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_created_by_cannot_be_overridden(self):
        data = {
            "title": "Python Developer",
            "description": "Backend developer.",
            "city": str(self.lima.id),
            "employment_type": EmploymentType.FULL_TIME,
            "work_mode": WorkMode.HYBRID,
            "created_by": str(self.other_user.id),
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        job = Job.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            job.created_by,
            self.recruiter,
        )

    def test_recruiter_can_create_job(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.post(
            self.url,
            {
                "title": "Senior Python Developer",
                "description": "Backend developer.",
                "employment_type": "full_time",
                "work_mode": "remote",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        job = Job.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            job.organization,
            self.organization,
        )

        self.assertEqual(
            job.created_by,
            self.recruiter,
        )

    def test_job_organization_is_taken_from_authenticated_user(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.post(
            self.url,
            {
                "title": "Senior Python Developer",
                "description": "Backend developer.",
                "employment_type": "full_time",
                "work_mode": "remote",
                "organization": str(
                    self.other_organization.id,
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        job = Job.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            job.organization,
            self.organization,
        )

    def test_job_created_by_is_taken_from_authenticated_user(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.post(
            self.url,
            {
                "title": "Senior Python Developer",
                "description": "Backend developer.",
                "employment_type": "full_time",
                "work_mode": "remote",
                "created_by": str(
                    self.other_recruiter.id,
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        job = Job.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            job.created_by,
            self.recruiter,
        )

    def test_recruiter_can_list_organization_jobs(self):
        self.client.force_authenticate(
            user=self.second_recruiter,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.job.id),
        )

    def test_recruiters_from_same_organization_can_see_same_job(self):
        job = Job.objects.create(
            title="Senior Django Developer",
            description="Backend position.",
            employment_type="full_time",
            work_mode="remote",
            organization=self.organization,
            created_by=self.recruiter,
        )

        self.client.force_authenticate(
            user=self.second_recruiter,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        job_ids = {item["id"] for item in response.data["results"]}

        self.assertIn(
            str(job.id),
            job_ids,
        )

    def test_recruiter_cannot_see_jobs_from_other_organization(self):
        job = Job.objects.create(
            title="Secret Backend Position",
            description="Private position.",
            employment_type="full_time",
            work_mode="remote",
            organization=self.other_organization,
            created_by=self.other_recruiter,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        job_ids = {item["id"] for item in response.data["results"]}

        self.assertNotIn(
            str(job.id),
            job_ids,
        )

    def test_recruiter_cannot_retrieve_job_from_other_organization(self):
        job = Job.objects.create(
            title="Secret Backend Position",
            description="Private position.",
            employment_type="full_time",
            work_mode="remote",
            organization=self.other_organization,
            created_by=self.other_recruiter,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.get(
            f"{self.url}{job.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_cannot_update_job_from_other_organization(self):
        job = Job.objects.create(
            title="Original Title",
            description="Private position.",
            employment_type="full_time",
            work_mode="remote",
            organization=self.other_organization,
            created_by=self.other_recruiter,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.patch(
            f"{self.url}{job.id}/",
            {
                "title": "Hacked Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        job.refresh_from_db()

        self.assertEqual(
            job.title,
            "Original Title",
        )

    def test_recruiter_cannot_delete_job_from_other_organization(self):
        job = Job.objects.create(
            title="Private Position",
            description="Private position.",
            employment_type="full_time",
            work_mode="remote",
            organization=self.other_organization,
            created_by=self.other_recruiter,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.delete(
            f"{self.url}{job.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Job.objects.filter(
                id=job.id,
            ).exists(),
        )

    def test_user_without_organization_cannot_create_job(self):
        self.client.force_authenticate(
            user=self.unassigned_user,
        )

        response = self.client.post(
            self.url,
            {
                "title": "Backend Developer",
                "description": "Backend position.",
                "employment_type": "full_time",
                "work_mode": "remote",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_without_organization_cannot_list_jobs(self):
        self.client.force_authenticate(
            user=self.unassigned_user,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_list_job_applications(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            str(response.data[0]["candidate"]),
            str(self.candidate.id),
        )

    def test_list_job_applications_returns_empty_list(self):
        response = self.client.get(
            f"{self.url}{self.job.id}/applications/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data,
            [],
        )

    def test_create_job_application(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/applications/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Application.objects.count(),
            1,
        )

        application = Application.objects.get()

        self.assertEqual(
            application.job,
            self.job,
        )

        self.assertEqual(
            application.candidate,
            self.candidate,
        )

        self.assertEqual(
            application.status,
            ApplicationStatus.APPLIED,
        )

    def test_create_application_uses_job_from_url(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/applications/",
            {
                "candidate": str(self.candidate.id),
                "job": str(self.other_job.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        application = Application.objects.get()

        self.assertEqual(
            application.job,
            self.job,
        )

    def test_create_duplicate_application_is_rejected(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_recruiter_cannot_access_other_organization_job_applications(self):
        response = self.client.get(
            f"{self.url}{self.other_job.id}/applications/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_cannot_create_application_for_other_organization_job(
        self,
    ):
        response = self.client.post(
            f"{self.url}{self.other_job.id}/applications/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            Application.objects.filter(
                job=self.other_job,
                candidate=self.candidate,
            ).exists(),
        )

    def test_application_can_move_to_screening(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/status/",
            {
                "application": str(application.id),
                "status": ApplicationStatus.SCREENING,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            ApplicationStatus.SCREENING,
        )

    def test_application_cannot_move_directly_to_hired(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/status/",
            {
                "application": str(application.id),
                "status": ApplicationStatus.HIRED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_application_can_be_rejected(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.INTERVIEW,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/status/",
            {
                "application": str(application.id),
                "status": ApplicationStatus.REJECTED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            ApplicationStatus.REJECTED,
        )

    def test_rejected_application_cannot_return_to_pipeline(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.REJECTED,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/status/",
            {
                "application": str(application.id),
                "status": ApplicationStatus.INTERVIEW,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_update_application_from_another_job(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.other_job,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/status/",
            {
                "application": str(application.id),
                "status": ApplicationStatus.SCREENING,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
