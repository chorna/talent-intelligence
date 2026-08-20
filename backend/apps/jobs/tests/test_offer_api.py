from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.jobs.choices import Currency, OfferStatus
from apps.jobs.models import CandidateSubmission, Offer

from .base import JobsTestMixin


class OfferViewSetTests(JobsTestMixin, APITestCase):
    def setUp(self):
        super().setUp()

        self.client.force_authenticate(
            user=self.recruiter,
        )

        self.submission = self.create_submission()

        self.url = f"/api/jobs/{self.job.id}/submissions/{self.submission.id}/offers/"

        self.offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
            status=OfferStatus.SENT,
            offered_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=7),
            notes="Initial offer.",
        )

    def test_create_offer(self):
        response = self.client.post(
            self.url,
            {
                "salary": "9000.00",
                "currency": Currency.PEN,
                "status": OfferStatus.SENT,
                "offered_at": timezone.now().isoformat(),
                "expires_at": (timezone.now() + timedelta(days=7)).isoformat(),
                "notes": "New offer.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Offer.objects.filter(
                submission=self.submission,
            ).count(),
            2,
        )

        offer = Offer.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            offer.submission,
            self.submission,
        )

        self.assertEqual(
            offer.salary,
            Decimal("9000.00"),
        )

        self.assertEqual(
            offer.currency,
            Currency.PEN,
        )

    def test_list_offers(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data

        if isinstance(data, dict):
            data = data["results"]

        self.assertEqual(
            len(data),
            1,
        )

        self.assertEqual(
            str(data[0]["id"]),
            str(self.offer.id),
        )

    def test_list_offers_returns_empty_list(self):
        self.offer.delete()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data

        if isinstance(data, dict):
            data = data["results"]

        self.assertEqual(
            data,
            [],
        )

    def test_retrieve_offer(self):
        response = self.client.get(
            f"{self.url}{self.offer.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(self.offer.id),
        )

        self.assertEqual(
            response.data["currency"],
            Currency.PEN,
        )

    def test_update_offer(self):
        response = self.client.patch(
            f"{self.url}{self.offer.id}/",
            {
                "salary": "9500.00",
                "currency": Currency.USD,
                "notes": "Updated offer.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.offer.refresh_from_db()

        self.assertEqual(
            self.offer.salary,
            Decimal("9500.00"),
        )

        self.assertEqual(
            self.offer.currency,
            Currency.USD,
        )

        self.assertEqual(
            self.offer.notes,
            "Updated offer.",
        )

    def test_delete_offer(self):
        response = self.client.delete(
            f"{self.url}{self.offer.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Offer.objects.filter(
                id=self.offer.id,
            ).exists(),
        )

    def test_cannot_retrieve_offer_from_other_job(self):
        other_submission = CandidateSubmission.objects.create(
            job=self.other_job,
            candidate=self.candidate,
            client=self.other_job.client,
            submitted_by=self.other_recruiter,
        )

        other_offer = Offer.objects.create(
            submission=other_submission,
            salary="7000.00",
            currency=Currency.PEN,
        )

        response = self.client.get(
            f"{self.url}{other_offer.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_update_offer_from_other_job(self):
        other_submission = CandidateSubmission.objects.create(
            job=self.other_job,
            candidate=self.candidate,
            client=self.other_job.client,
            submitted_by=self.other_recruiter,
        )

        other_offer = Offer.objects.create(
            submission=other_submission,
            salary="7000.00",
            currency=Currency.PEN,
        )

        response = self.client.patch(
            f"{self.url}{other_offer.id}/",
            {
                "salary": "10000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_delete_offer_from_other_job(self):
        other_submission = CandidateSubmission.objects.create(
            job=self.other_job,
            candidate=self.candidate,
            client=self.other_job.client,
            submitted_by=self.other_recruiter,
        )

        other_offer = Offer.objects.create(
            submission=other_submission,
            salary="7000.00",
            currency=Currency.PEN,
        )

        response = self.client.delete(
            f"{self.url}{other_offer.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
