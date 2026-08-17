from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.clients.models import Client
from apps.jobs.choices import (
    ApplicationStatus,
    EmploymentType,
    JobStatus,
    WorkMode,
)
from apps.jobs.models import Application, CandidateShortlist, Job, JobSkill
from apps.locations.models import City, Country
from apps.organizations.models import Organization
from apps.skills.models import Skill

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
            description="Python and Django backend engineer.",
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

        self.python = Skill.objects.create(
            name="Python",
            slug="python",
        )

        self.django = Skill.objects.create(
            name="Django",
            slug="django",
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
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            str(response.data["results"][0]["job"]),
            str(self.job.id),
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
            response.data["count"],
            0,
        )

        self.assertEqual(
            response.data["results"],
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
            f"{self.url}{self.job.id}/applications/{application.id}/status/",
            {
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
            f"{self.url}{self.job.id}/applications/{application.id}/status/",
            {
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
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/{application.id}/status/",
            {
                "status": ApplicationStatus.REJECTED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_rejected_application_cannot_return_to_pipeline(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.REJECTED,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/{application.id}/status/",
            {
                "status": ApplicationStatus.SCREENING,
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
            f"{self.url}{self.job.id}/applications/{application.id}/status/",
            {
                "status": ApplicationStatus.SCREENING,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_can_list_application_history(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        application.transition_to(
            ApplicationStatus.SCREENING,
            changed_by=self.recruiter,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/{application.id}/history/",
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
            response.data[0]["from_status"],
            ApplicationStatus.APPLIED,
        )

        self.assertEqual(
            response.data[0]["to_status"],
            ApplicationStatus.SCREENING,
        )

        self.assertEqual(
            response.data[0]["changed_by"],
            self.recruiter.email,
        )

    def test_application_history_must_belong_to_job(self):
        other_job = Job.objects.create(
            title="Other Backend Engineer",
            description="Other position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        application = Application.objects.create(
            candidate=self.candidate,
            job=other_job,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/{application.id}/history/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_from_other_organization_cannot_view_application_history(
        self,
    ):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        application.transition_to(
            ApplicationStatus.SCREENING,
            changed_by=self.recruiter,
        )

        self.client.force_authenticate(
            user=self.other_recruiter,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/{application.id}/history/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_application_status_creates_history(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/applications/{application.id}/status/",
            {
                "status": ApplicationStatus.SCREENING,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        history = application.status_history.get()

        self.assertEqual(
            history.from_status,
            ApplicationStatus.APPLIED,
        )

        self.assertEqual(
            history.to_status,
            ApplicationStatus.SCREENING,
        )

        self.assertEqual(
            history.changed_by,
            self.recruiter,
        )

    def test_list_job_skills(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
            is_required=True,
        )

        JobSkill.objects.create(
            job=self.job,
            skill=self.django,
            is_required=False,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/skills/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        skill_names = {item["skill_name"] for item in response.data}

        self.assertEqual(
            skill_names,
            {"Python", "Django"},
        )

    def test_add_job_skill(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/skills/",
            {
                "skill": str(self.python.id),
                "is_required": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            JobSkill.objects.filter(
                job=self.job,
                skill=self.python,
            ).count(),
            1,
        )

        self.assertTrue(
            response.data["is_required"],
        )

    def test_add_optional_job_skill(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/skills/",
            {
                "skill": str(self.python.id),
                "is_required": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertFalse(
            response.data["is_required"],
        )

    def test_add_duplicate_job_skill_is_rejected(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/skills/",
            {
                "skill": str(self.python.id),
                "is_required": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_delete_job_skill(self):
        job_skill = JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.delete(
            f"{self.url}{self.job.id}/skills/{self.python.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            JobSkill.objects.filter(
                id=job_skill.id,
            ).exists(),
        )

    def test_recruiter_cannot_list_skills_from_other_organization_job(self):
        response = self.client.get(
            f"{self.url}{self.other_job.id}/skills/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_cannot_add_skill_to_other_organization_job(self):
        response = self.client.post(
            f"{self.url}{self.other_job.id}/skills/",
            {
                "skill": str(self.python.id),
                "is_required": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            JobSkill.objects.filter(
                job=self.other_job,
                skill=self.python,
            ).exists(),
        )

    def test_recruiter_cannot_delete_skill_from_other_organization_job(self):
        job_skill = JobSkill.objects.create(
            job=self.other_job,
            skill=self.python,
        )

        response = self.client.delete(
            f"{self.url}{self.other_job.id}/skills/{self.python.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            JobSkill.objects.filter(
                id=job_skill.id,
            ).exists(),
        )

    def test_user_without_organization_cannot_list_job_skills(self):
        self.client.force_authenticate(
            user=self.unassigned_user,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/skills/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_without_organization_cannot_add_job_skill(self):
        self.client.force_authenticate(
            user=self.unassigned_user,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/skills/",
            {
                "skill": str(self.python.id),
                "is_required": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_list_job_skills(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/skills/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_retrieve_job_includes_skills(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
            is_required=True,
        )

        JobSkill.objects.create(
            job=self.job,
            skill=self.django,
            is_required=False,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["skills"]),
            2,
        )

        skills = {
            item["skill_name"]: item["is_required"] for item in response.data["skills"]
        }

        self.assertEqual(
            skills,
            {
                "Python": True,
                "Django": False,
            },
        )

    def test_retrieve_job_without_skills_returns_empty_list(self):
        response = self.client.get(
            f"{self.url}{self.job.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["skills"],
            [],
        )

    def test_filter_jobs_by_skill(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.get(
            f"{self.url}?skill=python",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_jobs_by_skill_returns_no_match(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.get(
            f"{self.url}?skill=golang",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_filter_jobs_by_multiple_skills(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        JobSkill.objects.create(
            job=self.job,
            skill=self.django,
        )

        response = self.client.get(
            f"{self.url}?skills=python,django",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_jobs_by_multiple_skills_uses_and_logic(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.get(
            f"{self.url}?skills=python,django",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_search_jobs_by_skill_name(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.get(
            f"{self.url}?search=python",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_search_jobs_by_skill_when_skill_is_not_in_job_text(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        response = self.client.get(
            f"{self.url}?search=python",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_job_applications_by_status(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.SCREENING,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/?status=screening",
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
            str(application.id),
        )

    def test_filter_job_applications_by_status_returns_empty(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.SCREENING,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/?status=hired",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_search_job_applications_by_candidate(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/?search=christian",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_recruiter_cannot_see_applications_from_other_job(self):
        other_job = Job.objects.create(
            title="Other Job",
            description="Other position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            organization=self.organization,
            created_by=self.recruiter,
        )

        Application.objects.create(
            candidate=self.candidate,
            job=other_job,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_recruiter_cannot_access_applications_from_other_organization_job(self):
        other_job = Job.objects.create(
            title="Other Organization Job",
            description="Other position.",
            city=self.bogota,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            organization=self.other_organization,
            created_by=self.other_recruiter,
        )

        response = self.client.get(
            f"{self.url}{other_job.id}/applications/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_order_job_applications_by_created_at(self):
        first = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        second_candidate = Candidate.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            city=self.bogota,
        )

        second = Application.objects.create(
            candidate=second_candidate,
            job=self.job,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/?ordering=created_at",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            str(first.id),
        )

        self.assertEqual(
            response.data["results"][1]["id"],
            str(second.id),
        )

    def test_update_application_notes(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.patch(
            f"{self.url}{self.job.id}/applications/{application.id}/notes/",
            {
                "notes": "Strong Django experience.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.notes,
            "Strong Django experience.",
        )

    def test_update_application_notes_replaces_existing_notes(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            notes="Old note",
        )

        response = self.client.patch(
            f"{self.url}{self.job.id}/applications/{application.id}/notes/",
            {
                "notes": "Updated note",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.notes,
            "Updated note",
        )

    def test_update_application_notes_requires_notes(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        response = self.client.patch(
            f"{self.url}{self.job.id}/applications/{application.id}/notes/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "notes",
            response.data,
        )

    def test_update_application_notes_cannot_update_application_from_other_job(
        self,
    ):
        other_job = Job.objects.create(
            title="Other job",
            description="Other job",
            organization=self.recruiter.organization,
            created_by=self.recruiter,
        )

        application = Application.objects.create(
            candidate=self.candidate,
            job=other_job,
        )

        response = self.client.patch(
            f"{self.url}{self.job.id}/applications/{application.id}/notes/",
            {
                "notes": "Should not update.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_application_summary(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.APPLIED,
        )

        second_candidate = Candidate.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            city=self.bogota,
        )

        Application.objects.create(
            candidate=second_candidate,
            job=self.job,
            status=ApplicationStatus.SCREENING,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/applications/summary/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total"],
            2,
        )

        self.assertEqual(
            response.data["pipeline"]["applied"],
            1,
        )

        self.assertEqual(
            response.data["pipeline"]["screening"],
            1,
        )

        self.assertEqual(
            response.data["pipeline"]["interview"],
            0,
        )

    def test_application_summary_returns_zero_for_empty_job(self):
        response = self.client.get(
            f"{self.url}{self.job.id}/applications/summary/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total"],
            0,
        )

        for status_value in ApplicationStatus.values:
            self.assertEqual(
                response.data["pipeline"][status_value],
                0,
            )

    def test_application_summary_cannot_access_other_organization_job(
        self,
    ):
        other_organization = Organization.objects.create(
            name="Other Organization",
        )

        other_job = Job.objects.create(
            title="Other Job",
            description="Other job",
            organization=other_organization,
            created_by=self.recruiter,
        )

        response = self.client.get(
            f"{self.url}{other_job.id}/applications/summary/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_dashboard_returns_zero_values(self):
        response = self.client.get(
            f"{self.url}dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_jobs"],
            1,
        )

        self.assertEqual(
            response.data["active_jobs"],
            1,
        )

        self.assertEqual(
            response.data["total_applications"],
            0,
        )

        for status_value in ApplicationStatus.values:
            self.assertEqual(
                response.data["pipeline"][status_value],
                0,
            )

    def test_recruiter_dashboard_returns_organization_metrics(self):
        Job.objects.create(
            title="Backend Developer",
            description="Django developer",
            organization=self.recruiter.organization,
            created_by=self.recruiter,
            status=JobStatus.OPEN,
        )

        Job.objects.create(
            title="Frontend Developer",
            description="Vue developer",
            organization=self.recruiter.organization,
            created_by=self.recruiter,
            status=JobStatus.CLOSED,
        )

        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.SCREENING,
        )

        response = self.client.get(
            f"{self.url}dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_jobs"],
            3,
        )

        self.assertEqual(
            response.data["total_applications"],
            1,
        )

        self.assertEqual(
            response.data["pipeline"]["screening"],
            1,
        )

    def test_recruiter_dashboard_does_not_include_other_organization_data(
        self,
    ):
        other_organization = Organization.objects.create(
            name="Other Organization",
        )

        other_job = Job.objects.create(
            title="Other Backend Job",
            description="Other job",
            organization=other_organization,
            created_by=self.recruiter,
            status=JobStatus.OPEN,
        )

        Application.objects.create(
            candidate=self.candidate,
            job=other_job,
            status=ApplicationStatus.HIRED,
        )

        response = self.client.get(
            f"{self.url}dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_applications"],
            0,
        )

        self.assertEqual(
            response.data["pipeline"]["hired"],
            0,
        )

    def test_recruiter_dashboard_excludes_other_organization_data(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.other_job,
            status=ApplicationStatus.HIRED,
        )

        response = self.client.get(
            f"{self.url}dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # self.job pertenece a nuestra organización.
        self.assertEqual(
            response.data["total_jobs"],
            1,
        )

        self.assertEqual(
            response.data["active_jobs"],
            1,
        )

        # La application de la otra organización no debe aparecer.
        self.assertEqual(
            response.data["total_applications"],
            0,
        )

        for status_value in ApplicationStatus.values:
            self.assertEqual(
                response.data["pipeline"][status_value],
                0,
            )

        self.assertEqual(
            response.data["metrics"]["hired_rate"],
            0,
        )

        self.assertEqual(
            response.data["metrics"]["rejected_rate"],
            0,
        )

    def test_recruiter_dashboard_returns_application_metrics(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.HIRED,
        )

        screening_candidate = Candidate.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            city=self.lima,
        )

        Application.objects.create(
            candidate=screening_candidate,
            job=self.job,
            status=ApplicationStatus.SCREENING,
        )

        response = self.client.get(
            f"{self.url}dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_applications"],
            2,
        )

        self.assertEqual(
            response.data["metrics"]["hired_rate"],
            50.0,
        )

        self.assertEqual(
            response.data["metrics"]["rejected_rate"],
            0,
        )

    def test_recruiter_dashboard_returns_zero_metrics_for_empty_job(
        self,
    ):
        response = self.client.get(
            f"{self.url}dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_applications"],
            0,
        )

        self.assertEqual(
            response.data["metrics"]["hired_rate"],
            0,
        )

        self.assertEqual(
            response.data["metrics"]["rejected_rate"],
            0,
        )

    def test_create_job_with_client(self):
        client_obj = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        data = {
            "title": "Python Developer",
            "description": "Backend developer.",
            "client": str(client_obj.id),
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
            job.client,
            client_obj,
        )

        self.assertEqual(
            job.created_by,
            self.recruiter,
        )

    def test_cannot_create_job_with_client_from_other_organization(self):
        other_client = Client.objects.create(
            organization=self.other_organization,
            name="Other Client",
        )

        response = self.client.post(
            self.url,
            {
                "title": "Senior Python Developer",
                "client": str(other_client.id),
                # demás campos requeridos
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "client",
            response.data,
        )

    def test_list_job_shortlist(self):
        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
            notes="Strong Python and Django experience.",
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/shortlist/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        item = response.data[0]

        self.assertEqual(
            str(item["candidate"]),
            str(self.candidate.id),
        )

        self.assertEqual(
            item["notes"],
            "Strong Python and Django experience.",
        )

    def test_add_candidate_to_shortlist(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "candidate": str(self.candidate.id),
                "notes": "Strong Python and Django experience.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        shortlist = CandidateShortlist.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            shortlist.job,
            self.job,
        )

        self.assertEqual(
            shortlist.candidate,
            self.candidate,
        )

        self.assertEqual(
            shortlist.created_by,
            self.recruiter,
        )

        self.assertEqual(
            shortlist.notes,
            "Strong Python and Django experience.",
        )

    def test_add_candidate_to_shortlist_without_notes(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        shortlist = CandidateShortlist.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            shortlist.notes,
            "",
        )

    def test_add_candidate_to_shortlist_requires_candidate(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "notes": "Candidate without ID.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "candidate",
            response.data,
        )

    def test_add_nonexistent_candidate_to_shortlist(self):
        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "candidate": "00000000-0000-0000-0000-000000000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "candidate",
            response.data,
        )

    def test_cannot_add_same_candidate_twice_to_shortlist(self):
        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "candidate",
            response.data,
        )

    def test_candidate_can_be_shortlisted_for_different_jobs(self):
        second_job = Job.objects.create(
            title="Python Developer",
            description="Another position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        response = self.client.post(
            f"{self.url}{second_job.id}/shortlist/",
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
            CandidateShortlist.objects.filter(
                candidate=self.candidate,
            ).count(),
            2,
        )

    def test_different_candidates_can_be_shortlisted_for_same_job(self):
        second_candidate = Candidate.objects.create(
            first_name="Juan",
            last_name="Perez",
            email="juan@example.com",
            city=self.lima,
            headline="Python Developer",
            summary="Python developer.",
        )

        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "candidate": str(second_candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            CandidateShortlist.objects.filter(
                job=self.job,
            ).count(),
            2,
        )

    def test_cannot_list_shortlist_from_other_organization_job(self):
        response = self.client.get(
            f"{self.url}{self.other_job.id}/shortlist/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_add_candidate_to_other_organization_job(self):
        response = self.client.post(
            f"{self.url}{self.other_job.id}/shortlist/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_other_organization_recruiter_cannot_access_job_shortlist(self):
        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.client.force_authenticate(
            user=self.other_recruiter,
        )

        response = self.client.get(
            f"{self.url}{self.job.id}/shortlist/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_other_organization_recruiter_cannot_add_to_job_shortlist(self):
        self.client.force_authenticate(
            user=self.other_recruiter,
        )

        response = self.client.post(
            f"{self.url}{self.job.id}/shortlist/",
            {
                "candidate": str(self.candidate.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_remove_candidate_from_shortlist(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        response = self.client.delete(
            f"{self.url}{self.job.id}/shortlist/{shortlist.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            CandidateShortlist.objects.filter(
                pk=shortlist.id,
            ).exists(),
        )

    def test_cannot_remove_shortlist_from_different_job(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        second_job = Job.objects.create(
            title="Another Python Developer",
            description="Another position.",
            city=self.lima,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        response = self.client.delete(
            f"{self.url}{second_job.id}/shortlist/{shortlist.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            CandidateShortlist.objects.filter(
                pk=shortlist.id,
            ).exists(),
        )

    def test_remove_nonexistent_shortlist_returns_404(self):
        response = self.client.delete(
            f"{self.url}{self.job.id}/shortlist/00000000-0000-0000-0000-000000000000/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
