from rest_framework import viewsets, mixins

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingReadSerializer


class BorrowingViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingReadSerializer
        if self.action == "retrieve":
            return BorrowingReadSerializer
        return BorrowingSerializer
