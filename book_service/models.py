import enum

from django.db import models


class CoverType(enum.Enum):
    hard = "HARD"
    soft = "SOFT"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4, choices=[(tag.name, tag.value) for tag in CoverType]
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=4,
        decimal_places=2,
    )

    def __str__(self) -> str:
        return self.title
