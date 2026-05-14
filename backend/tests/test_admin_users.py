import pytest
from fastapi import status

@pytest.fixture
def admin_token(client):
    client.post(
        "/auth/register",
        json={"email": "admin_user@test.com", "password": "admin", "role": "admin"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "admin_user@test.com", "password": "admin"},
    )
    return response.json()["access_token"]

def test_admin_list_users(client, admin_token):
    response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_admin_create_user(client, admin_token):
    response = client.post(
        "/users/",
        json={
            "email": "new_user@test.com",
            "password": "password123",
            "full_name": "New User",
            "role": "student"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "new_user@test.com"

def test_admin_delete_user(client, admin_token):
    # First create a user to delete
    reg_resp = client.post(
        "/users/",
        json={
            "email": "delete_me@test.com",
            "password": "pass",
            "full_name": "Delete Me",
            "role": "student"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    user_id = reg_resp.json()["id"]

    # Delete the user
    response = client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify user is gone
    users_resp = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    user_ids = [u["id"] for u in users_resp.json()]
    assert user_id not in user_ids

def test_admin_cannot_delete_self(client, admin_token):
    # Get current user id
    me_resp = client.get("/users/me", headers={"Authorization": f"Bearer {admin_token}"})
    my_id = me_resp.json()["id"]

    response = client.delete(f"/users/{my_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot delete your own account" in response.json()["detail"]
