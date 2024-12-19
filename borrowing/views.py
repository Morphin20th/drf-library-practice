from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)


def _params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=bool,
                description="Filter by is-active state (e.g., ?is-active=True)",
            ),
            OpenApiParameter(
                name="user",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by user IDs " "(e.g., ?user=1,3)",
            ),
        ]
    )
)
class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related()

        is_active = self.request.query_params.get("is-active")
        user = self.request.query_params.get("user")

        if is_active:
            queryset = queryset.filter(is_active=is_active)

        if user:
            user_ids = _params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)
