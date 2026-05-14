import pytest
from fastapi import status


@pytest.fixture
def admin_token(client):
    client.post(
        "/auth/register",
        json={"email": "admin@test.com", "password": "admin", "role": "admin"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "admin"},
    )
    return response.json()["access_token"]


@pytest.fixture
def student_token(client):
    response = client.post(
        "/auth/register",
        json={"email": "student@test.com", "password": "student", "role": "student"},
    )
    user_id = response.json()["id"]
    response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "student"},
    )
    return response.json()["access_token"], user_id


def test_create_student_admin_only(client, admin_token):
    # Register a user to link the student to
    reg_resp = client.post(
        "/auth/register",
        json={"email": "s1@test.com", "password": "pass", "role": "student"},
    )
    user_id = reg_resp.json()["id"]

    response = client.post(
        "/students/",
        json={
            "university_id": "STU-001",
            "name": "Test Student",
            "department": "CS",
            "gpa": 3.8,
            "user_id": user_id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["university_id"] == "STU-001"


def test_list_students_admin_only(client, admin_token, student_token):
    token, _ = student_token
    # Student should be blocked
    resp = client.get("/students/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Admin should be allowed
    resp = client.get("/students/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == status.HTTP_200_OK


def test_student_get_own_profile(client, admin_token, student_token):
    token, user_id = student_token
    
    # Create student record for this user
    client.post(
        "/students/",
        json={
            "university_id": "STU-OWN",
            "name": "My Name",
            "department": "CS",
            "gpa": 3.5,
            "user_id": user_id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Get student id
    list_resp = client.get("/students/", headers={"Authorization": f"Bearer {admin_token}"})
    student_id = list_resp.json()[0]["id"]
    
    # Student accesses own profile
    resp = client.get(f"/students/{student_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "My Name"


def test_student_cannot_access_other_profile(client, admin_token, student_token):
    _, user_id = student_token # First student
    
    # Create second student user
    reg_resp = client.post(
        "/auth/register",
        json={"email": "s2@test.com", "password": "pass", "role": "student"},
    )
    s2_id = reg_resp.json()["id"]
    s2_login = client.post("/auth/login", json={"email": "s2@test.com", "password": "pass"})
    s2_token = s2_login.json()["access_token"]

    # Create record for first student
    s1_record = client.post(
        "/students/",
        json={
            "university_id": "STU-S1",
            "name": "Student One",
            "department": "CS",
            "gpa": 3.0,
            "user_id": user_id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    ).json()
    
    # S2 tries to access S1 profile
    resp = client.get(f"/students/{s1_record['id']}", headers={"Authorization": f"Bearer {s2_token}"})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_delete_student_admin_only(client, admin_token):
    # Create student
    reg_resp = client.post(
        "/auth/register",
        json={"email": "del_stu@test.com", "password": "pass", "role": "student"},
    )
    user_id = reg_resp.json()["id"]
    
    s_resp = client.post(
        "/students/",
        json={
            "university_id": "DEL-001",
            "name": "Delete Me",
            "department": "CS",
            "gpa": 2.0,
            "user_id": user_id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    student_id = s_resp.json()["id"]

    # Delete
    response = client.delete(f"/students/{student_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify
    get_resp = client.get(f"/students/{student_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND

