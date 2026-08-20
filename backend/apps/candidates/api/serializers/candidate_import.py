from rest_framework import serializers

from apps.candidates.models import CandidateImport


class CandidateImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateImport
        fields = [
            "id",
            "file",
            "original_filename",
            "status",
            "error_message",
            "candidate",
            "imported_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "status",
            "error_message",
            "candidate",
            "imported_by",
            "created_at",
            "updated_at",
        ]

    def validate_file(self, value):
        allowed_extensions = {
            ".pdf",
            ".doc",
            ".docx",
        }

        extension = value.name.lower().rsplit(".", 1)

        if len(extension) != 2:
            raise serializers.ValidationError(
                "Unsupported file type.",
            )

        extension = f".{extension[1]}"

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF, DOC, and DOCX files are supported.",
            )

        return value
