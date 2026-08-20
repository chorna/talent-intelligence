from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.jobs.choices import Currency, OfferStatus
from apps.jobs.models import Offer

from .base import JobsTestMixin


class OfferModelTests(JobsTestMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.submission = self.create_submission()

    def test_create_offer(self):
        offered_at = timezone.now()
        expires_at = offered_at + timedelta(days=7)

        offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
            status=OfferStatus.SENT,
            offered_at=offered_at,
            expires_at=expires_at,
            notes="Backend Engineer offer.",
        )

        self.assertIsNotNone(offer.id)
        self.assertEqual(offer.submission, self.submission)
        self.assertEqual(offer.salary, "8500.00")
        self.assertEqual(offer.currency, Currency.PEN)
        self.assertEqual(offer.status, OfferStatus.SENT)
        self.assertEqual(offer.notes, "Backend Engineer offer.")

    def test_default_status_is_draft(self):
        offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
        )

        self.assertEqual(
            offer.status,
            OfferStatus.DRAFT,
        )

    def test_currency_uses_choices(self):
        self.assertEqual(
            Offer._meta.get_field("currency").choices,
            Currency.choices,
        )

    def test_currency_choices_are_valid(self):
        field = Offer._meta.get_field("currency")

        valid_values = {value for value, _ in field.choices}

        self.assertIn(Currency.PEN, valid_values)
        self.assertIn(Currency.USD, valid_values)
        self.assertIn(Currency.EUR, valid_values)

    def test_offer_belongs_to_submission(self):
        offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
        )

        self.assertIn(
            offer,
            self.submission.offers.all(),
        )

    def test_submission_can_have_multiple_offers(self):
        first_offer = Offer.objects.create(
            submission=self.submission,
            salary="8000.00",
            currency=Currency.PEN,
        )

        second_offer = Offer.objects.create(
            submission=self.submission,
            salary="9000.00",
            currency=Currency.PEN,
        )

        self.assertEqual(
            self.submission.offers.count(),
            2,
        )

        self.assertIn(
            first_offer,
            self.submission.offers.all(),
        )

        self.assertIn(
            second_offer,
            self.submission.offers.all(),
        )

    def test_offer_is_deleted_when_submission_is_deleted(self):
        offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
        )

        offer_id = offer.id

        self.submission.delete()

        self.assertFalse(
            Offer.objects.filter(
                id=offer_id,
            ).exists(),
        )

    def test_optional_dates_and_notes(self):
        offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
        )

        self.assertIsNone(
            offer.offered_at,
        )

        self.assertIsNone(
            offer.expires_at,
        )

        self.assertIsNone(
            offer.responded_at,
        )

        self.assertEqual(
            offer.notes,
            "",
        )

    def test_offer_string_representation(self):
        offer = Offer.objects.create(
            submission=self.submission,
            salary="8500.00",
            currency=Currency.PEN,
        )

        self.assertEqual(
            str(offer),
            f"{self.submission.candidate} - 8500.00 PEN",
        )
