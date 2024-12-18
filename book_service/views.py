from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly

from book_service.models import Book
from book_service.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        elif self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
