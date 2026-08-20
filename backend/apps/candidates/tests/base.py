from apps.candidates.models import Candidate
from apps.organizations.models import Organization
from apps.users.models import User


class CandidatesTestMixin:
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Talent Agency",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="password123",
            organization=self.organization,
        )

        self.candidate = self.create_candidate()

    def create_candidate(self, **kwargs):
        defaults = {
            "first_name": "Christian",
            "last_name": "Horna",
            "email": "christian@example.com",
        }
        defaults.update(kwargs)

        return Candidate.objects.create(**defaults)
