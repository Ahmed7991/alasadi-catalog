from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        PUBLIC = "public", _("General Public")
        CONTRACTOR = "contractor", _("Contractor / Wholesaler")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PUBLIC,
    )
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        suffix = self.company_name if self.company_name else self.get_role_display()
        return f"{self.username} ({suffix})"
