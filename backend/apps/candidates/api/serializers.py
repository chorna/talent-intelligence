from rest_framework import serializers

from apps.candidates.models import Candidate, CandidateFavorite, CandidateNote
from apps.education.api.serializers import EducationSerializer
from apps.experiences.api.serializers import ExperienceSerializer
from apps.locations.models import City
from apps.skills.api.serializers import SkillSerializer
from apps.skills.models import Skill


class CandidateSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(
        many=True,
        read_only=True,
    )

    skill_ids = serializers.PrimaryKeyRelatedField(
        source="skills",
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    experiences = ExperienceSerializer(
        many=True,
        read_only=True,
    )

    educations = EducationSerializer(
        many=True,
        read_only=True,
    )
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "headline",
            "summary",
            "linkedin_url",
            "github_url",
            "skills",
            "skill_ids",
            "experiences",
            "educations",
            "is_favorite",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "skills",
            "experiences",
            "educations",
            "created_at",
            "updated_at",
        ]

    def validate_email(self, value):
        return value.strip().lower()

    def get_is_favorite(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return CandidateFavorite.objects.filter(
            user=request.user,
            candidate=obj,
        ).exists()


class CandidateFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateFavorite
        fields = [
            "id",
            "candidate",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class CandidateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateNote
        fields = [
            "id",
            "candidate",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "candidate",
            "created_at",
            "updated_at",
        ]
