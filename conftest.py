import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from catalog.models import Category


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(
        username="testuser",
        password="TestPassword123!",
        **extra_fields,
    ):
        return User.objects.create_user(
            username=username,
            password=password,
            **extra_fields,
        )

    return make_user


@pytest.fixture
def auth_client(create_user):
    user = create_user()

    client = APIClient()
    token = AccessToken.for_user(user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    return client, user


@pytest.fixture
def category():
    return Category.objects.create(
        name="Test Category",
        slug="test-category",
    )