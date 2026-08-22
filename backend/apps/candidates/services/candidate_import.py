from django.db import transaction

from apps.candidates.choices import CandidateImportStatus
from apps.candidates.models import Candidate
from apps.candidates.services.candidate_extractor import (
    CandidateDataExtractor,
)
from apps.candidates.services.cv_parser import CVParser


class CandidateImportProcessor:
    def __init__(self):
        self.parser = CVParser()
        self.extractor = CandidateDataExtractor()

    def process(self, candidate_import):

        candidate_import.status = CandidateImportStatus.PROCESSING
        candidate_import.error_message = ""
        candidate_import.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ],
        )

        try:
            with transaction.atomic():
                text = self.parser.parse(
                    candidate_import.file,
                )

                data = self.extractor.extract(text)

                candidate = Candidate.objects.create(
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    phone=data["phone"],
                    linkedin_url=data["linkedin_url"],
                    github_url=data["github_url"],
                    headline=data["headline"],
                    summary=data["summary"],
                )

                candidate_import.candidate = candidate
                candidate_import.status = CandidateImportStatus.COMPLETED
                candidate_import.error_message = ""

                candidate_import.save(
                    update_fields=[
                        "candidate",
                        "status",
                        "error_message",
                        "updated_at",
                    ],
                )

                return candidate

        except Exception as exc:
            candidate_import.status = CandidateImportStatus.FAILED
            candidate_import.error_message = str(exc)

            candidate_import.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ],
            )

            raise
