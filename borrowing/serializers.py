from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        ]


class BorrowingReadSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
