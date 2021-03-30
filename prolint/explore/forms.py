from django import forms

from .models import ExploreResults

from django.db import models
from django.conf import settings

class ExploreResultsForm(forms.ModelForm):

    class Meta:
        model = ExploreResults
        user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
        )

        # fields = ('title', 'prot_name', 'scatter', 'radii', 'lipids')
        fields = ('description',)
