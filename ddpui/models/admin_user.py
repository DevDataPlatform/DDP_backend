from django.db import models
from ninja import ModelSchema


class AdminUser(models.Model):
    """Docstring"""

    active = models.BooleanField(default=True)
    email = models.CharField(max_length=50, null=True, unique=True)


class AdminUserResponse(ModelSchema):
    """Docstring"""

    class Config:
        """Docstring"""

        model = AdminUser
        model_fields = ["email", "active"]
