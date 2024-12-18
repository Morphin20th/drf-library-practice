from django.core.exceptions import ValidationError
from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)

    def clean(self):
        if self.expected_return_date <= self.borrow_date:
            raise ValidationError(
                {
                    "expected_return_date": "Expected return date must be later than the borrow date."
                }
            )
        if self.actual_return_date <= self.borrow_date:
            raise ValidationError(
                {
                    "actual_return_date": "Actual return date must be later than the borrow date."
                }
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(expected_return_date__gt=models.F("borrow_date")),
                name="expected_return_date_gt_borrow_date",
            ),
            models.CheckConstraint(
                check=models.Q(actual_return_date__gt=models.F("borrow_date")),
                name="actual_return_date_gt_borrow_date",
            ),
        ]

    def __str__(self):
        return f"Borrow date: {self.borrow_date}, expected return date: {self.expected_return_date}"
