import re

from rest_framework import serializers

from apps.education.choices import DegreeChoices
from apps.education.models import Education


class DegreeChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            value = re.sub(r"\s+", " ", data.strip()).lower()

            degree_aliases = {
                "high school": DegreeChoices.HIGH_SCHOOL,
                "associate degree": DegreeChoices.ASSOCIATE,
                "bachelor degree": DegreeChoices.BACHELOR,
                "master degree": DegreeChoices.MASTER,
                "doctorate degree": DegreeChoices.DOCTORATE,
            }

            value = degree_aliases.get(value, value)

        return super().to_internal_value(value)


class EducationSerializer(serializers.ModelSerializer):
    degree = DegreeChoiceField(
        choices=DegreeChoices.choices,
    )

    class Meta:
        model = Education
        fields = [
            "id",
            "candidate",
            "institution",
            "degree",
            "field_of_study",
            "description",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )
        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None),
        )
        is_current = attrs.get(
            "is_current",
            getattr(self.instance, "is_current", False),
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        if is_current and end_date:
            raise serializers.ValidationError(
                {"end_date": "Current education cannot have an end date."}
            )

        return attrs

    def validate_institution(self, value):
        return " ".join(value.strip().split())

    def validate_field_of_study(self, value):
        return " ".join(value.strip().split())

    def validate_location(self, value):
        return " ".join(value.strip().split())
