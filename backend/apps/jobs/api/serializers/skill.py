from rest_framework import serializers

from apps.jobs.models import JobSkill


class JobSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True,
    )

    class Meta:
        model = JobSkill
        fields = [
            "id",
            "skill",
            "skill_name",
            "is_required",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "skill_name",
            "created_at",
        ]

    def validate_skill(self, skill):
        job = self.context.get("job")

        if (
            job
            and JobSkill.objects.filter(
                job=job,
                skill=skill,
            ).exists()
        ):
            raise serializers.ValidationError(
                "This skill is already associated with this job.",
            )

        return skill
