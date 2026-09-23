import pytest


@pytest.mark.django_db
def test_register_login_me(api_client):
    # Регистрация
    register_response = api_client.post(
        "/api/register/",
        {
            "username": "authuser",
            "email": "authuser@example.com",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert register_response.status_code == 201

    # Логин
    token_response = api_client.post(
        "/api/token/",
        {
            "username": "authuser",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert token_response.status_code == 200
    assert "access" in token_response.data

    # GET /api/me/
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
    )

    me_response = api_client.get("/api/me/")

    assert me_response.status_code == 200
    assert me_response.data["username"] == "authuser"


@pytest.mark.django_db
def test_me_without_token(api_client):
    response = api_client.get("/api/me/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_with_wrong_password(api_client, create_user):
    create_user(
        username="wrongpassuser",
        password="CorrectPassword123!",
    )

    response = api_client.post(
        "/api/token/",
        {
            "username": "wrongpassuser",
            "password": "WrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 401