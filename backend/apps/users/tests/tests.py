from django.test import TestCase

from apps.users.models import User


class UserManagerTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="christian@example.com",
            password="secret123",
        )

        self.assertEqual(user.email, "christian@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(
            email="Christian@EXAMPLE.COM",
            password="secret123",
        )

        self.assertEqual(
            user.email,
            "Christian@example.com",
        )

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="secret123",
            )

    def test_create_user_hashes_password(self):
        user = User.objects.create_user(
            email="christian@example.com",
            password="secret123",
        )

        self.assertNotEqual(
            user.password,
            "secret123",
        )
        self.assertTrue(
            user.check_password("secret123"),
        )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="secret123",
        )

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_requires_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="secret123",
                is_staff=False,
            )

    def test_create_superuser_requires_is_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="secret123",
                is_superuser=False,
            )
