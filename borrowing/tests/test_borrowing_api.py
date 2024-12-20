from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from book_service.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    return reverse("borrowing:borrowing-return-borrowing", args=[borrowing_id])


def sample_borrowing(**params):
    defaults = {
        "borrow_date": "2024-12-12",
        "expected_return_date": "2024-12-21",
        "book": sample_book(),
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


def sample_book(**params):
    defaults = {
        "title": "book",
        "author": "author",
        "inventory": 10,
        "cover": "hard",
        "daily_fee": 10.00,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user_1 = get_user_model().objects.create_user(
            email="test@test.test", password="Test1234!", is_staff=False
        )
        self.regular_user_2 = get_user_model().objects.create_user(
            email="test2@test.test", password="Test1234!", is_staff=False
        )
        self.regular_user_3 = get_user_model().objects.create_user(
            email="test3@test.test", password="Test1234!", is_staff=False
        )
        self.client.force_authenticate(self.regular_user_1)

        self.book_1 = sample_book(title="test1")
        self.book_2 = sample_book(title="test2")
        self.borrowing_1 = sample_borrowing(book=self.book_1, user=self.regular_user_1)
        self.borrowing_2 = sample_borrowing(book=self.book_2, user=self.regular_user_2)

    def test_user_can_see_only_their_borrowing(self):
        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.regular_user_1)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.borrowing_2, res.data)
        self.assertEqual(res.data, serializer.data)

    def test_return_borrowing_action(self):
        res = self.client.post(return_url(self.borrowing_1.id))

        self.borrowing_1.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(self.borrowing_1.is_active)
        self.assertIsNotNone(self.borrowing_1.actual_return_date)

    def test_inventory_changes_on_borrowing(self):
        self.client.force_authenticate(self.regular_user_3)
        book = sample_book(inventory=2)
        payload = {"book": book.id, "expected_return_date": "2024-12-31"}
        res = self.client.post(BORROWING_URL, payload)
        book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.inventory, 1)

        borrowing = Borrowing.objects.get(id=res.data["id"])
        res = self.client.post(return_url(borrowing.id))

        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, 2)

    def test_filter_borrowings_by_is_active(self):
        url = f"{BORROWING_URL}?is-active=True"
        res = self.client.get(url)

        active_borrowings = Borrowing.objects.filter(
            is_active=True, user=self.regular_user_1
        )
        serializer = BorrowingListSerializer(active_borrowings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_cannot_have_multiple_active_borrowings(self):
        self.client.force_authenticate(self.regular_user_3)

        payload_1 = {
            "book": self.book_1.id,
            "expected_return_date": "2024-12-31",
        }
        res_1 = self.client.post(BORROWING_URL, payload_1)
        self.assertEqual(res_1.status_code, status.HTTP_201_CREATED)

        payload_2 = {
            "book": self.book_2.id,
            "expected_return_date": "2024-12-31",
        }
        with self.assertRaises(ValidationError):
            res_2 = self.client.post(BORROWING_URL, payload_2)

        borrowings = Borrowing.objects.filter(user_id=self.regular_user_3.id)
        self.assertEqual(borrowings.count(), 1)


class AdminBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user = get_user_model().objects.create_user(
            email="test@test.test", password="Test1234!", is_staff=False
        )
        self.admin = get_user_model().objects.create_user(
            email="admin@admin.admin", password="Test1234!", is_staff=False
        )
        self.client.force_authenticate(self.admin)

        self.book_1 = sample_book(title="test1")
        self.book_2 = sample_book(title="test2")
        self.borrowing_1 = sample_borrowing(book=self.book_1, user=self.regular_user)
        self.borrowing_2 = sample_borrowing(book=self.book_2, user=self.admin)

    def test_filter_borrowings_by_user_ids(self):
        res = self.client.get(
            BORROWING_URL,
            {"user_ids": f"{self.admin.id}"},
        )

        serializer_correct_user = BorrowingListSerializer(self.borrowing_2)
        serializer_wrong_user = BorrowingListSerializer(self.borrowing_1)

        self.assertIn(serializer_correct_user.data, res.data)
        self.assertNotIn(serializer_wrong_user.data, res.data)

    def test_admin_cannot_delete_borrowing(self):
        res = self.client.delete(detail_url(self.borrowing_1.id))

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_admin_cannot_update_borrowing(self):
        url = detail_url(self.borrowing_1.id)
        payload = {"actual_return_date": "2024-12-25"}
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
