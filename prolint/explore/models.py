from django.db import models
from django import forms

from multiselectfield import MultiSelectField

from django.conf import settings

class ExploreResults(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=100)
    prot_name = models.CharField(max_length=20, null=False, blank=False, default="Protein")
    scatter = models.BooleanField(null=False, default=True)
    lipids = models.CharField(max_length=300, null=True, blank=True, default="")
    task_id = models.CharField(max_length=40, default='0')
    radii = MultiSelectField(choices=())

    description = models.TextField(null=True)

