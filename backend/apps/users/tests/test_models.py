# Create your tests here.
import pytest

from apps.users.models import User


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="christian@example.com",
            password="secure-password",
            first_name="Christian",
            last_name="Horna",
        )

        assert user.email == "christian@example.com"
        assert user.first_name == "Christian"
        assert user.last_name == "Horna"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("secure-password")

    def test_email_is_normalized(self):
        user = User.objects.create_user(
            email="Christian@EXAMPLE.COM",
            password="secure-password",
        )

        assert user.email == "Christian@example.com"

    def test_password_is_hashed(self):
        user = User.objects.create_user(
            email="christian@example.com",
            password="secure-password",
        )

        assert user.password != "secure-password"
        assert user.check_password("secure-password")

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match="email must be set"):
            User.objects.create_user(
                email="",
                password="secure-password",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="secure-password",
        )

        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_cannot_disable_staff(self):
        with pytest.raises(
            ValueError,
            match="is_staff=True",
        ):
            User.objects.create_superuser(
                email="admin@example.com",
                password="secure-password",
                is_staff=False,
            )

    def test_create_superuser_cannot_disable_superuser(self):
        with pytest.raises(
            ValueError,
            match="is_superuser=True",
        ):
            User.objects.create_superuser(
                email="admin@example.com",
                password="secure-password",
                is_superuser=False,
            )

    def test_user_string_representation(self):
        user = User.objects.create_user(
            email="christian@example.com",
            password="secure-password",
        )

        assert str(user) == "christian@example.com"

    def test_user_has_email_as_username_field(self):
        assert User.USERNAME_FIELD == "email"

    def test_create_superuser_sets_required_flags(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="secure-password",
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True
