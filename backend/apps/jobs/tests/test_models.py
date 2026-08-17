from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
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
    CandidateShortlist,
    Job,
    JobSkill,
)
from apps.locations.models import City, Country
from apps.organizations.models import Organization
from apps.skills.models import Skill
from apps.users.models import User


class JobModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ACME Technologies",
        )

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
            organization=self.organization,
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

    def test_job_belongs_to_organization(self):
        job = Job.objects.create(
            title="Backend Engineer",
            description="Backend position.",
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            organization=self.organization,
            created_by=self.user,
        )

        self.assertEqual(
            job.organization,
            self.organization,
        )

    def test_organization_can_have_multiple_jobs(self):
        Job.objects.create(
            title="Python Developer",
            description="Backend position.",
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            organization=self.organization,
            created_by=self.user,
        )

        Job.objects.create(
            title="Django Developer",
            description="Backend position.",
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            organization=self.organization,
            created_by=self.user,
        )

        self.assertEqual(
            self.organization.jobs.count(),
            2,
        )


class ApplicationModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.user = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
            organization=self.organization,
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
            organization=self.organization,
            created_by=self.user,
        )

    def test_create_application(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertEqual(
            application.status,
            ApplicationStatus.APPLIED,
        )

    def test_application_candidate_job_is_unique(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        with self.assertRaises(IntegrityError):
            Application.objects.create(
                candidate=self.candidate,
                job=self.job,
            )

    def test_application_status_can_be_updated(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        application.status = ApplicationStatus.SCREENING
        application.save(update_fields=["status"])

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            ApplicationStatus.SCREENING,
        )

    def test_application_notes_are_optional(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertEqual(
            application.notes,
            "",
        )

    def test_application_can_have_notes(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            notes="Strong Django experience.",
        )

        self.assertEqual(
            application.notes,
            "Strong Django experience.",
        )

    def test_application_can_transition_from_applied_to_screening(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        application.transition_to(
            ApplicationStatus.SCREENING,
            changed_by=self.user,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            ApplicationStatus.SCREENING,
        )

    def test_application_cannot_transition_from_applied_to_hired(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        with self.assertRaises(ValidationError):
            application.transition_to(
                ApplicationStatus.HIRED,
                changed_by=self.user,
            )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            ApplicationStatus.APPLIED,
        )

    def test_rejected_application_is_terminal(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.REJECTED,
        )

        self.assertFalse(
            application.can_transition_to(
                ApplicationStatus.SCREENING,
            ),
        )

    def test_hired_application_is_terminal(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=ApplicationStatus.HIRED,
        )

        self.assertFalse(
            application.can_transition_to(
                ApplicationStatus.REJECTED,
            ),
        )

    def test_can_transition_to_returns_true_for_valid_transition(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertTrue(
            application.can_transition_to(
                ApplicationStatus.SCREENING,
            ),
        )

    def test_application_creation_creates_status_history(self):
        application = Application.create_with_history(
            candidate=self.candidate,
            job=self.job,
            changed_by=self.user,
        )

        history = application.status_history.get()

        self.assertIsNone(
            history.from_status,
        )

        self.assertEqual(
            history.to_status,
            ApplicationStatus.APPLIED,
        )

        self.assertEqual(
            history.changed_by,
            self.user,
        )

    def test_application_transition_creates_status_history(self):
        application = Application.create_with_history(
            candidate=self.candidate,
            job=self.job,
            changed_by=self.user,
        )

        application.transition_to(
            ApplicationStatus.SCREENING,
            changed_by=self.user,
        )

        history = application.status_history.order_by(
            "created_at",
        ).last()

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
            self.user,
        )

    def test_invalid_transition_does_not_create_history(self):
        application = Application.create_with_history(
            candidate=self.candidate,
            job=self.job,
            changed_by=self.user,
        )

        with self.assertRaises(ValidationError):
            application.transition_to(
                ApplicationStatus.HIRED,
                changed_by=self.user,
            )

        self.assertEqual(
            application.status_history.count(),
            1,
        )


class JobSkillModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
            organization=self.organization,
        )

        self.job = Job.objects.create(
            title="Senior Backend Engineer",
            description="Python Django backend engineer.",
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        self.python = Skill.objects.create(
            name="Python",
            slug="python",
        )

    def test_create_job_skill(self):
        job_skill = JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        self.assertEqual(
            job_skill.job,
            self.job,
        )

        self.assertEqual(
            job_skill.skill,
            self.python,
        )

        self.assertTrue(
            job_skill.is_required,
        )

    def test_job_skill_is_unique_per_job(self):
        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        with self.assertRaises(IntegrityError):
            JobSkill.objects.create(
                job=self.job,
                skill=self.python,
            )

    def test_skill_can_be_used_by_multiple_jobs(self):
        another_job = Job.objects.create(
            title="Python Developer",
            description="Python position.",
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.REMOTE,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        JobSkill.objects.create(
            job=self.job,
            skill=self.python,
        )

        JobSkill.objects.create(
            job=another_job,
            skill=self.python,
        )

        self.assertEqual(
            JobSkill.objects.filter(
                skill=self.python,
            ).count(),
            2,
        )

    def test_job_skill_can_be_optional(self):
        job_skill = JobSkill.objects.create(
            job=self.job,
            skill=self.python,
            is_required=False,
        )

        self.assertFalse(
            job_skill.is_required,
        )


class CandidateShortlistModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Talent Agency",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="password123",
            organization=self.organization,
        )

        self.country = Country.objects.create(
            name="Peru",
            code="PE",
        )

        self.city = City.objects.create(
            country=self.country,
            name="Lima",
        )

        self.job = Job.objects.create(
            title="Senior Backend Engineer",
            description="Python and Django backend engineer.",
            city=self.city,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
            city=self.city,
            headline="Senior Backend Engineer",
            summary="Python and Django specialist.",
        )

    def test_create_candidate_shortlist(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.assertIsNotNone(
            shortlist.id,
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
            "",
        )

    def test_create_candidate_shortlist_with_notes(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
            notes="Strong Python and Django experience.",
        )

        self.assertEqual(
            shortlist.notes,
            "Strong Python and Django experience.",
        )

    def test_candidate_shortlist_str(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.assertEqual(
            str(shortlist),
            f"{self.candidate} - {self.job}",
        )

    def test_candidate_cannot_be_shortlisted_twice_for_same_job(self):
        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        with self.assertRaises(
            IntegrityError,
        ):
            CandidateShortlist.objects.create(
                job=self.job,
                candidate=self.candidate,
                created_by=self.recruiter,
            )

    def test_candidate_can_be_shortlisted_for_different_jobs(self):
        second_job = Job.objects.create(
            title="Python Developer",
            description="Another Python position.",
            city=self.city,
            employment_type=EmploymentType.FULL_TIME,
            work_mode=WorkMode.HYBRID,
            status=JobStatus.OPEN,
            organization=self.organization,
            created_by=self.recruiter,
        )

        first_shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        second_shortlist = CandidateShortlist.objects.create(
            job=second_job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.assertNotEqual(
            first_shortlist.id,
            second_shortlist.id,
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
            city=self.city,
            headline="Python Developer",
            summary="Python developer.",
        )

        first_shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        second_shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=second_candidate,
            created_by=self.recruiter,
        )

        self.assertNotEqual(
            first_shortlist.id,
            second_shortlist.id,
        )

        self.assertEqual(
            CandidateShortlist.objects.filter(
                job=self.job,
            ).count(),
            2,
        )

    def test_shortlist_ordering_by_created_at(self):
        first_shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        second_candidate = Candidate.objects.create(
            first_name="Juan",
            last_name="Perez",
            email="juan@example.com",
            city=self.city,
        )

        second_shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=second_candidate,
            created_by=self.recruiter,
        )

        shortlist = list(
            CandidateShortlist.objects.filter(
                job=self.job,
            ),
        )

        self.assertEqual(
            shortlist[0],
            first_shortlist,
        )

        self.assertEqual(
            shortlist[1],
            second_shortlist,
        )

    def test_shortlist_belongs_to_job(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.assertIn(
            shortlist,
            self.job.shortlist.all(),
        )

    def test_candidate_has_shortlist_relationship(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.assertIn(
            shortlist,
            self.candidate.shortlists.all(),
        )

    def test_recruiter_has_shortlist_relationship(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        self.assertIn(
            shortlist,
            self.recruiter.candidate_shortlists.all(),
        )

    def test_delete_job_deletes_shortlist(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        shortlist_id = shortlist.id

        self.job.delete()

        self.assertFalse(
            CandidateShortlist.objects.filter(
                id=shortlist_id,
            ).exists(),
        )

    def test_delete_candidate_deletes_shortlist(self):
        shortlist = CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        shortlist_id = shortlist.id

        self.candidate.delete()

        self.assertFalse(
            CandidateShortlist.objects.filter(
                id=shortlist_id,
            ).exists(),
        )

    def test_delete_recruiter_is_protected(self):
        CandidateShortlist.objects.create(
            job=self.job,
            candidate=self.candidate,
            created_by=self.recruiter,
        )

        with self.assertRaises(
            ProtectedError,
        ):
            self.recruiter.delete()
