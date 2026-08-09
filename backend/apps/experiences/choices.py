from django.db import models


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full time"
    PART_TIME = "part_time", "Part time"
    CONTRACT = "contract", "Contract"
    FREELANCE = "freelance", "Freelance"
    INTERNSHIP = "internship", "Internship"
    TEMPORARY = "temporary", "Temporary"
    OTHER = "other", "Other"


class WorkMode(models.TextChoices):
    REMOTE = "remote", "Remote"
    HYBRID = "hybrid", "Hybrid"
    ONSITE = "onsite", "On-site"
