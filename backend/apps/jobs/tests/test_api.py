from rest_framework import status
from rest_framework.test import APITestCase

from apps.jobs.choices import EmploymentType, JobStatus, WorkMode
from apps.jobs.models import Job
from apps.locations.models import City, Country
from apps.users.models import User


class JobViewSetTests(APITestCase):
    def setUp(self):
        self.url = "/api/jobs/"

        self.user = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
        )

        self.client.force_authenticate(
            user=self.user,
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
            created_by=self.user,
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
            self.user,
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
            created_by=self.user,
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
            created_by=self.user,
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
            self.user,
        )
