from django.db import models


class DegreeChoices(models.TextChoices):
    HIGH_SCHOOL = "high_school", "High School"
    ASSOCIATE = "associate", "Associate"
    BACHELOR = "bachelor", "Bachelor"
    MASTER = "master", "Master"
    DOCTORATE = "doctorate", "Doctorate"
    DIPLOMA = "diploma", "Diploma"
    CERTIFICATE = "certificate", "Certificate"
