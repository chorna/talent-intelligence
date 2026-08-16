from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.choices import ClientStatus
from apps.clients.models import Client, ClientContact
from apps.organizations.models import Organization
from apps.users.models import User


class ClientViewSetTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Talent Agency",
        )
        self.other_organization = Organization.objects.create(
            name="Other Agency",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="password123",
            organization=self.organization,
        )
        self.other_recruiter = User.objects.create_user(
            email="other@example.com",
            password="password123",
            organization=self.other_organization,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        self.url = "/api/clients/"

    def test_recruiter_can_list_organization_clients(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )
        Client.objects.create(
            organization=self.other_organization,
            name="Other Client",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            1,
        )
        self.assertEqual(
            response.data["results"][0]["name"],
            "ACME",
        )

    def test_recruiter_cannot_see_other_organization_client(self):
        client = Client.objects.create(
            organization=self.other_organization,
            name="Other Client",
        )

        response = self.client.get(
            f"{self.url}{client.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_recruiter_can_create_client(self):
        response = self.client.post(
            self.url,
            {
                "name": "ACME",
                "website": "https://acme.com",
                "description": "Technology company",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        client = Client.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            client.organization,
            self.organization,
        )
        self.assertEqual(
            client.name,
            "ACME",
        )
        self.assertEqual(
            client.status,
            ClientStatus.ACTIVE,
        )

    def test_recruiter_cannot_assign_client_to_other_organization(self):
        response = self.client.post(
            self.url,
            {
                "name": "ACME",
                "organization": str(self.other_organization.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        client = Client.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            client.organization,
            self.organization,
        )

    def test_recruiter_can_retrieve_client(self):
        client = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        response = self.client.get(
            f"{self.url}{client.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["name"],
            "ACME",
        )

    def test_recruiter_can_update_client(self):
        client = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        response = self.client.patch(
            f"{self.url}{client.id}/",
            {
                "name": "ACME Corporation",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        client.refresh_from_db()

        self.assertEqual(
            client.name,
            "ACME Corporation",
        )

    def test_recruiter_can_delete_client(self):
        client = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        response = self.client.delete(
            f"{self.url}{client.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Client.objects.filter(
                pk=client.pk,
            ).exists(),
        )

    def test_filter_clients_by_status(self):
        Client.objects.create(
            organization=self.organization,
            name="Active Client",
            status=ClientStatus.ACTIVE,
        )
        Client.objects.create(
            organization=self.organization,
            name="Inactive Client",
            status=ClientStatus.INACTIVE,
        )

        response = self.client.get(
            f"{self.url}?status=active",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            1,
        )
        self.assertEqual(
            response.data["results"][0]["name"],
            "Active Client",
        )

    def test_search_clients_by_name(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME Corporation",
        )
        Client.objects.create(
            organization=self.organization,
            name="Globex",
        )

        response = self.client.get(
            f"{self.url}?search=acme",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            1,
        )
        self.assertEqual(
            response.data["results"][0]["name"],
            "ACME Corporation",
        )

    def test_search_clients_by_description(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME",
            description="Software development company",
        )

        response = self.client.get(
            f"{self.url}?search=software",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_search_clients_by_website(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME",
            website="https://acme.com",
        )

        response = self.client.get(
            f"{self.url}?search=acme.com",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_order_clients_by_name(self):
        Client.objects.create(
            organization=self.organization,
            name="Zeta",
        )
        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        response = self.client.get(
            f"{self.url}?ordering=name",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        names = [item["name"] for item in response.data["results"]]

        self.assertEqual(
            names,
            ["ACME", "Zeta"],
        )

    def test_cannot_create_duplicate_client_in_organization(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        response = self.client.post(
            self.url,
            {
                "name": "ACME",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "name",
            response.data,
        )

    def test_same_client_name_is_allowed_for_other_organization(self):
        Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        self.client.force_authenticate(
            user=self.other_recruiter,
        )

        response = self.client.post(
            self.url,
            {
                "name": "ACME",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


class ClientContactViewSetTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Talent Agency",
        )
        self.other_organization = Organization.objects.create(
            name="Other Agency",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="password123",
            organization=self.organization,
        )

        self.other_recruiter = User.objects.create_user(
            email="other@example.com",
            password="password123",
            organization=self.other_organization,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        self.client_obj = Client.objects.create(
            organization=self.organization,
            name="ACME",
        )

        self.other_client = Client.objects.create(
            organization=self.other_organization,
            name="Other Client",
        )

        self.url = f"/api/clients/{self.client_obj.id}/contacts/"

    def test_list_client_contacts(self):
        ClientContact.objects.create(
            client=self.client_obj,
            name="John Doe",
            email="john@acme.com",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            1,
        )
        self.assertEqual(
            response.data[0]["name"],
            "John Doe",
        )

    def test_list_client_contacts_returns_empty_list(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            [],
        )

    def test_create_client_contact(self):
        response = self.client.post(
            self.url,
            {
                "name": "John Doe",
                "email": "john@acme.com",
                "phone": "+51999999999",
                "position": "HR Manager",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        contact = ClientContact.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            contact.client,
            self.client_obj,
        )
        self.assertEqual(
            contact.name,
            "John Doe",
        )

    def test_create_contact_cannot_assign_different_client(self):
        response = self.client.post(
            self.url,
            {
                "client": str(self.other_client.id),
                "name": "John Doe",
                "email": "john@acme.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        contact = ClientContact.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            contact.client,
            self.client_obj,
        )

    def test_cannot_access_contacts_from_other_organization(self):
        ClientContact.objects.create(
            client=self.other_client,
            name="Other Contact",
            email="contact@other.com",
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.get(
            f"/api/clients/{self.other_client.id}/contacts/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_other_organization_recruiter_can_access_own_contacts(self):
        contact = ClientContact.objects.create(
            client=self.other_client,
            name="Other Contact",
            email="contact@other.com",
        )

        self.client.force_authenticate(
            user=self.other_recruiter,
        )

        response = self.client.get(
            f"/api/clients/{self.other_client.id}/contacts/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data[0]["id"],
            str(contact.id),
        )

    def test_contact_cannot_be_created_for_other_organization_client(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.post(
            f"/api/clients/{self.other_client.id}/contacts/",
            {
                "name": "Hacker Contact",
                "email": "hacker@other.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
