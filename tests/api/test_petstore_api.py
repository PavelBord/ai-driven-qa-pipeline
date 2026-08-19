import httpx

BASE_URL = "https://petstore.swagger.io/v2"


def test_create_pet():

    response = httpx.post(f"{BASE_URL}/pet",
        json={
            "id": 100,
            "name": "AI Dog",
            "status": "available",
        },
    )

    assert response.status_code == 200


def test_get_pet():

    response = httpx.get(f"{BASE_URL}/pet/100")

    assert response.status_code == 200


def test_get_missing_pet():

    response = httpx.get(f"{BASE_URL}/pet/999999999")

    assert response.status_code == 404