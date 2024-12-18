from django.shortcuts import render
from rest_framework import viewsets, mixins

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer, BorrowingSerializer


class BorrowingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        return BorrowingSerializer
