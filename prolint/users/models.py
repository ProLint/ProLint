from django.contrib.auth.models import AbstractUser
from django.db import models

from uploads.models import FileMD

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=20, blank=False, null=True)
    last_name = models.CharField(max_length=20, blank=False, null=True)

    email = models.EmailField(blank=False)

    age = models.PositiveIntegerField(null=True, blank=False)

    def __str__(self):
        return self.email