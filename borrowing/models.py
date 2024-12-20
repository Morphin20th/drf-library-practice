from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.timezone import now

from book_service.models import Book
from telegram_bot.telegram_helper import send_telegram_message
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )
    is_active = models.BooleanField(default=True)

    @staticmethod
    def validate_borrowing(
        expected_return_date,
        borrow_date,
        actual_return_date,
        book,
        user,
        error_to_raise,
    ):
        if expected_return_date and borrow_date:
            if expected_return_date < borrow_date:
                raise error_to_raise(
                    {
                        "expected_return_date": "Expected return date must be later than or equal to the borrow date."
                    }
                )
        if actual_return_date and borrow_date:
            if actual_return_date < borrow_date:
                raise error_to_raise(
                    {
                        "actual_return_date": "Actual return date must be later or equal than the borrow date."
                    }
                )
        if book.inventory == 0:
            raise error_to_raise({"book.inventory": "Inventory must be more than 0"})
        if user.borrowings.filter(is_active=True).count() == 1:
            raise error_to_raise({"user": "User already has an active borrowing."})

    def return_borrowing(self):
        if self.actual_return_date:
            raise ValidationError("It has already been returned.")

        with transaction.atomic():
            self.actual_return_date = now().date()
            self.is_active = False

            self.book.inventory += 1
            self.book.save(update_fields=["inventory"])

            super(Borrowing, self).save(
                update_fields=["actual_return_date", "is_active"]
            )

    def clean(self):
        self.validate_borrowing(
            expected_return_date=self.expected_return_date,
            borrow_date=self.borrow_date,
            actual_return_date=self.actual_return_date,
            book=self.book,
            user=self.user,
            error_to_raise=ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        if self.actual_return_date:
            self.is_active = False

        self.full_clean()

        is_new = self.pk is None

        with transaction.atomic():
            if is_new:
                if self.book.inventory < 1:
                    raise ValidationError(
                        "Cannot borrow book. Inventory must be at least 1."
                    )
                self.book.inventory -= 1
                self.book.save(update_fields=["inventory"])
                try:
                    message = (
                        f"New Borrowing Created:\n"
                        f"Book: {self.book.title}\n"
                        f"User: {self.user.email}\n"
                        f"Expected Return: {self.expected_return_date}"
                    )
                    send_telegram_message(message)
                except Exception as e:
                    raise ValidationError(f"Failed to send notification: {e}")

        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(expected_return_date__gte=models.F("borrow_date")),
                name="expected_return_date_gte_borrow_date",
            ),
            models.CheckConstraint(
                check=models.Q(actual_return_date__gte=models.F("borrow_date")),
                name="actual_return_date_gte_borrow_date",
            ),
        ]

    def __str__(self):
        return f"Borrow date: {self.borrow_date}, expected return date: {self.expected_return_date}"
