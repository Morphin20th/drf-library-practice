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
            "is_active",
        ]


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)


class BorrowingListSerializer(BorrowingSerializer):
    book = SlugRelatedField(read_only=True, slug_field="title")
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "expected_return_date",
            "book",
        ]

    def create(self, validated_data):
        request = self.context.get("request")

        validated_data["user"] = request.user
        return super().create(validated_data)
