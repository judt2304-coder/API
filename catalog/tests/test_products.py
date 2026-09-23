import pytest


@pytest.mark.django_db
def test_product_list_available_without_auth(api_client, category):
    response = api_client.get("/api/products/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_product_price_range_filter(api_client, category):
    from catalog.models import Product

    Product.objects.create(
        category=category,
        name="Cheap Product",
        description="Cheap",
        price=100,
        in_stock=10,
    )
    Product.objects.create(
        category=category,
        name="Expensive Product",
        description="Expensive",
        price=1000,
        in_stock=10,
    )

    response = api_client.get(
        "/api/products/?min_price=200&max_price=800"
    )

    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_anonymous_cannot_create_product(api_client, category):
    response = api_client.post(
        "/api/products/",
        {
            "category": category.id,
            "name": "Test Product",
            "description": "Test description",
            "price": 500,
            "in_stock": 10,
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_can_create_product(auth_client, category):
    client, user = auth_client

    response = client.post(
        "/api/products/",
        {
            "category": category.id,
            "name": "Test Product",
            "description": "Test description",
            "price": 500,
            "in_stock": 10,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["owner"] == user.username


@pytest.mark.django_db
def test_negative_price_rejected(auth_client, category):
    client, _ = auth_client

    response = client.post(
        "/api/products/",
        {
            "category": category.id,
            "name": "Test Product",
            "description": "Test description",
            "price": -100,
            "in_stock": 10,
        },
        format="json",
    )

    assert response.status_code == 400


# assert response.data["count"] == 0