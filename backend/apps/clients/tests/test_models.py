# Create your tests here.
from django.db import IntegrityError
from django.test import TestCase

from apps.clients.choices import ClientStatus
from apps.clients.models import Client, ClientContact
from apps.organizations.models import Organization


class ClientModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Talent Agency",
        )

    def test_create_client(self):
        client = Client.objects.create(
            organization=self.organization,
            name="ACME",
            website="https://acme.com",
            description="Technology company",
        )

        self.assertIsNotNone(client.pk)
        self.assertEqual(
            client.organization,
            self.organization,
        )
        self.assertEqual(
            client.name,
            "ACME",
        )
        self.assertEqual(
            client.website,
            "https://acme.com",
        )
        self.assertEqual(
            client.status,
            ClientStatus.ACTIVE,
        )

    def test_client_status_defaults_to_active(self):
        client = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        self.assertEqual(
            client.status,
            ClientStatus.ACTIVE,
        )

    def test_client_string_representation(self):
        client = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        self.assertEqual(
            str(client),
            "ACME",
        )

    def test_client_name_is_unique_per_organization(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                organization=self.organization,
                name="ACME",
            )

    def test_same_client_name_is_allowed_for_different_organizations(self):
        another_organization = Organization.objects.create(
            name="Another Agency",
        )

        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        client = Client.objects.create(
            organization=another_organization,
            name="ACME",
        )

        self.assertIsNotNone(client.pk)

    def test_client_ordering_by_name(self):
        Client.objects.create(
            organization=self.organization,
            name="Zeta",
        )
        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        clients = list(Client.objects.all())

        self.assertEqual(
            clients[0].name,
            "ACME",
        )
        self.assertEqual(
            clients[1].name,
            "Zeta",
        )


class ClientContactModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Talent Agency",
        )
        self.client = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

    def test_create_client_contact(self):
        contact = ClientContact.objects.create(
            client=self.client,
            name="John Doe",
            email="john@acme.com",
            phone="+51999999999",
            position="HR Manager",
        )

        self.assertIsNotNone(contact.pk)
        self.assertEqual(
            contact.client,
            self.client,
        )
        self.assertEqual(
            contact.name,
            "John Doe",
        )
        self.assertEqual(
            contact.email,
            "john@acme.com",
        )
        self.assertEqual(
            contact.phone,
            "+51999999999",
        )
        self.assertEqual(
            contact.position,
            "HR Manager",
        )

    def test_optional_fields_can_be_empty(self):
        contact = ClientContact.objects.create(
            client=self.client,
            name="John Doe",
            email="john@acme.com",
        )

        self.assertEqual(
            contact.phone,
            "",
        )
        self.assertEqual(
            contact.position,
            "",
        )

    def test_client_contact_string_representation(self):
        contact = ClientContact.objects.create(
            client=self.client,
            name="John Doe",
            email="john@acme.com",
        )

        self.assertEqual(
            str(contact),
            "John Doe - ACME",
        )

    def test_client_contacts_are_related_to_client(self):
        contact = ClientContact.objects.create(
            client=self.client,
            name="John Doe",
            email="john@acme.com",
        )

        self.assertEqual(
            list(self.client.contacts.all()),
            [contact],
        )

    def test_deleting_client_deletes_contacts(self):
        contact = ClientContact.objects.create(
            client=self.client,
            name="John Doe",
            email="john@acme.com",
        )

        self.client.delete()

        self.assertFalse(
            ClientContact.objects.filter(
                pk=contact.pk,
            ).exists(),
        )
