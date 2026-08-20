from django.db import models


class JobStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    OPEN = "open", "Open"
    PAUSED = "paused", "Paused"
    CLOSED = "closed", "Closed"


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full time"
    PART_TIME = "part_time", "Part time"
    CONTRACT = "contract", "Contract"
    FREELANCE = "freelance", "Freelance"
    INTERNSHIP = "internship", "Internship"


class WorkMode(models.TextChoices):
    REMOTE = "remote", "Remote"
    HYBRID = "hybrid", "Hybrid"
    ON_SITE = "on_site", "On site"


class ApplicationStatus(models.TextChoices):
    APPLIED = "applied", "Applied"
    SCREENING = "screening", "Screening"
    INTERVIEW = "interview", "Interview"
    OFFER = "offer", "Offer"
    HIRED = "hired", "Hired"
    REJECTED = "rejected", "Rejected"


class SubmissionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    INTERVIEW_REQUESTED = (
        "interview_requested",
        "Interview requested",
    )


class ClientFeedbackDecision(models.TextChoices):
    INTERESTED = "interested", "Interested"
    NOT_INTERESTED = "not_interested", "Not interested"


class InterviewStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    NO_SHOW = "no_show", "No show"


class InterviewType(models.TextChoices):
    HR = "hr", "HR"
    TECHNICAL = "technical", "Technical"
    CLIENT = "client", "Client"
    FINAL = "final", "Final"
    OTHER = "other", "Other"


class OfferStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"
    WITHDRAWN = "withdrawn", "Withdrawn"


class Currency(models.TextChoices):
    PEN = "PEN", "Peruvian Sol"
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
