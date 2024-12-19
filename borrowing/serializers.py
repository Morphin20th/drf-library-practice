from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from book_service.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)


class BorrowingListSerializer(BorrowingSerializer):
    book = SlugRelatedField(read_only=True, slug_field="title")
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")
