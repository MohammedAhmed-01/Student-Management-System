# tests/test_filtering_pagination.py
# Member 4 - Tests for filtering and pagination on GET /api/students/
#
# Run with: pytest tests/test_filtering_pagination.py -v

import math
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from utils.filters import apply_student_filters
from utils.pagination import paginate_query, calc_pages
from models.student import Student


# ============================================================
# Helpers
# ============================================================

def make_student(**kwargs) -> Student:
    defaults = dict(
        student_id=1,
        user_id=1,
        first_name="Ahmed",
        last_name="Ali",
        email="ahmed@example.com",
        phone="01000000000",
        gender="male",
        department="CS",
        major="Software Engineering",
        enrollment_year=2021,
        year_of_study=3,
        gpa=3.5,
        status="active",
    )
    defaults.update(kwargs)
    s = Student()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


def mock_query(students: list):
    """Return a MagicMock that behaves like a filtered SQLAlchemy Query."""
    q = MagicMock()
    q.filter.return_value = q
    q.count.return_value = len(students)
    q.offset.return_value = q
    q.limit.return_value = q
    q.all.return_value = students
    return q


# ============================================================
# calc_pages
# ============================================================

class TestCalcPages:
    def test_exact_division(self):
        assert calc_pages(100, 10) == 10

    def test_rounds_up(self):
        assert calc_pages(101, 10) == 11

    def test_zero_total(self):
        assert calc_pages(0, 10) == 0

    def test_single_item(self):
        assert calc_pages(1, 10) == 1

    def test_page_size_zero_returns_zero(self):
        assert calc_pages(50, 0) == 0


# ============================================================
# apply_student_filters
# ============================================================

class TestApplyStudentFilters:

    def test_no_filters_does_not_call_filter(self):
        q = MagicMock()
        result = apply_student_filters(q)
        q.filter.assert_not_called()
        assert result is q

    def test_department_filter_applied(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(q, department="CS")
        assert q.filter.call_count == 1

    def test_gpa_min_filter_applied(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(q, gpa_min=3.0)
        assert q.filter.call_count == 1

    def test_gpa_max_filter_applied(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(q, gpa_max=3.8)
        assert q.filter.call_count == 1

    def test_status_filter_applied(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(q, status="active")
        assert q.filter.call_count == 1

    def test_year_of_study_filter_applied(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(q, year_of_study=2)
        assert q.filter.call_count == 1

    def test_all_filters_applied(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(
            q,
            department="CS",
            gpa_min=2.5,
            gpa_max=4.0,
            status="active",
            year_of_study=3,
        )
        assert q.filter.call_count == 5

    def test_partial_filters(self):
        q = MagicMock(); q.filter.return_value = q
        apply_student_filters(q, department="Math", status="graduated")
        assert q.filter.call_count == 2


# ============================================================
# paginate_query
# ============================================================

class TestPaginateQuery:
    def _students(self, n: int):
        return [make_student(student_id=i) for i in range(1, n + 1)]

    def test_returns_correct_total(self):
        students = self._students(25)
        q = mock_query(students)
        _, total = paginate_query(q, page=1, page_size=10)
        assert total == 25

    def test_offset_calculated_correctly_page1(self):
        q = mock_query(self._students(10))
        paginate_query(q, page=1, page_size=10)
        q.offset.assert_called_once_with(0)

    def test_offset_calculated_correctly_page2(self):
        q = mock_query(self._students(10))
        paginate_query(q, page=2, page_size=10)
        q.offset.assert_called_once_with(10)

    def test_offset_calculated_correctly_page3(self):
        q = mock_query(self._students(5))
        paginate_query(q, page=3, page_size=5)
        q.offset.assert_called_once_with(10)

    def test_limit_equals_page_size(self):
        q = mock_query(self._students(10))
        paginate_query(q, page=1, page_size=15)
        q.limit.assert_called_once_with(15)

    def test_empty_result(self):
        q = mock_query([])
        items, total = paginate_query(q, page=1, page_size=10)
        assert items == []
        assert total == 0

    def test_items_returned(self):
        students = self._students(3)
        q = mock_query(students)
        items, _ = paginate_query(q, page=1, page_size=10)
        assert items == students


# ============================================================
# Router response shape (with mocked DB)
# ============================================================

class TestRouterResponseShape:

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from routers.students import router
        from core.database import get_db
        from core.dependencies import get_current_user, require_admin
        from schemas.auth import CurrentUser

        app = FastAPI()
        app.include_router(router)

        fake_user = CurrentUser(user_id=999, username="admin", email="admin@test.com", role="admin")
        fake_students = [make_student(student_id=i) for i in range(1, 16)]

        def override_db():
            db = MagicMock(spec=Session)
            q = mock_query(fake_students)
            q.order_by.return_value = q
            db.query.return_value = q
            yield db

        def override_user():
            return fake_user

        app.dependency_overrides[get_db]           = override_db
        app.dependency_overrides[get_current_user] = override_user
        app.dependency_overrides[require_admin]    = override_user

        return TestClient(app)

    def test_default_response_keys(self, client):
        resp = client.get("/api/students/")
        assert resp.status_code == 200
        body = resp.json()
        for key in ("total", "page", "page_size", "pages", "data"):
            assert key in body, f"Missing key: {key}"

    def test_default_page_is_1(self, client):
        body = client.get("/api/students/").json()
        assert body["page"] == 1

    def test_default_page_size_is_10(self, client):
        body = client.get("/api/students/").json()
        assert body["page_size"] == 10

    def test_pages_calculation(self, client):
        body = client.get("/api/students/").json()
        expected = math.ceil(body["total"] / body["page_size"])
        assert body["pages"] == expected

    def test_custom_page_size(self, client):
        body = client.get("/api/students/?page_size=5").json()
        assert body["page_size"] == 5

    def test_custom_page(self, client):
        body = client.get("/api/students/?page=2").json()
        assert body["page"] == 2

    def test_all_filter_params_accepted(self, client):
        resp = client.get(
            "/api/students/?department=CS&gpa_min=3.0&gpa_max=4.0&status=active&year_of_study=3"
        )
        assert resp.status_code == 200

    def test_invalid_status_rejected(self, client):
        resp = client.get("/api/students/?status=unknown")
        assert resp.status_code == 422

    def test_gpa_min_out_of_range_rejected(self, client):
        resp = client.get("/api/students/?gpa_min=5.0")
        assert resp.status_code == 422

    def test_page_zero_rejected(self, client):
        resp = client.get("/api/students/?page=0")
        assert resp.status_code == 422

    def test_page_size_over_100_rejected(self, client):
        resp = client.get("/api/students/?page_size=101")
        assert resp.status_code == 422

    def test_gpa_min_greater_than_gpa_max_rejected(self, client):
        resp = client.get("/api/students/?gpa_min=4.0&gpa_max=2.0")
        assert resp.status_code == 422
