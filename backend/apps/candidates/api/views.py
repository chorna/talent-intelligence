from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.candidates.models import Candidate, CandidateFavorite, CandidateNote
from apps.core.pagination import DefaultPagination

from .serializers import CandidateNoteSerializer, CandidateSerializer


@extend_schema(tags=["Candidates"])
class CandidateViewSet(ModelViewSet):
    queryset = Candidate.objects.select_related(
        "city",
        "city__country",
    ).prefetch_related(
        "skills",
        "experiences",
        "educations",
    )
    serializer_class = CandidateSerializer
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]

    ordering_fields = [
        "first_name",
        "last_name",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        skill = self.request.query_params.get("skill")
        skills = self.request.query_params.get("skills")
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        search = self.request.query_params.get("search")

        # Single skill:
        # ?skill=python
        if skill:
            queryset = queryset.filter(
                skills__slug__iexact=skill.strip(),
            )

        # Multiple skills (AND):
        # ?skills=python,django
        if skills:
            skill_slugs = [
                value.strip().lower() for value in skills.split(",") if value.strip()
            ]

            for skill_slug in skill_slugs:
                queryset = queryset.filter(
                    skills__slug__iexact=skill_slug,
                )

        if city:
            queryset = queryset.filter(
                city__name__iexact=city,
            )

        if country:
            queryset = queryset.filter(
                city__country__code__iexact=country,
            )

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(headline__icontains=search)
                | Q(summary__icontains=search)
            )

        return queryset.distinct()

    @action(
        detail=True,
        methods=["post"],
        url_path="favorite",
    )
    def favorite(self, request, pk=None):
        candidate = self.get_object()

        favorite, created = CandidateFavorite.objects.get_or_create(
            user=request.user,
            candidate=candidate,
        )

        return Response(
            {
                "is_favorite": True,
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        candidate = self.get_object()

        deleted, _ = CandidateFavorite.objects.filter(
            user=request.user,
            candidate=candidate,
        ).delete()

        return Response(
            {
                "is_favorite": False,
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="favorites",
    )
    def favorites(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(
                favorited_by__user=request.user,
            )
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="notes",
    )
    def notes(self, request, pk=None):
        candidate = self.get_object()

        notes = CandidateNote.objects.filter(
            candidate=candidate,
            user=request.user,
        )

        serializer = CandidateNoteSerializer(
            notes,
            many=True,
        )

        return Response(serializer.data)

    @notes.mapping.post
    def create_note(self, request, pk=None):
        candidate = self.get_object()

        serializer = CandidateNoteSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        note = serializer.save(
            candidate=candidate,
            user=request.user,
        )

        return Response(
            CandidateNoteSerializer(note).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path=r"notes/(?P<note_id>[0-9a-f-]+)",
    )
    def note_detail(self, request, pk=None, note_id=None):
        note = self._get_user_note(
            request=request,
            candidate_id=pk,
            note_id=note_id,
        )

        if note is None:
            return Response(
                {"detail": "Note not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CandidateNoteSerializer(note)

        return Response(serializer.data)

    @note_detail.mapping.patch
    def update_note(self, request, pk=None, note_id=None):
        note = self._get_user_note(
            request=request,
            candidate_id=pk,
            note_id=note_id,
        )

        if note is None:
            return Response(
                {"detail": "Note not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CandidateNoteSerializer(
            note,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @note_detail.mapping.delete
    def delete_note(self, request, pk=None, note_id=None):
        note = self._get_user_note(
            request=request,
            candidate_id=pk,
            note_id=note_id,
        )

        if note is None:
            return Response(
                {"detail": "Note not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        note.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    def _get_user_note(self, request, candidate_id, note_id):
        return CandidateNote.objects.filter(
            id=note_id,
            candidate_id=candidate_id,
            user=request.user,
        ).first()
