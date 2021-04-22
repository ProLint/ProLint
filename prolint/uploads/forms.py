from django import forms
from django.db import models
from django.conf import settings

from .models import FileMD

class FileMDForm(forms.ModelForm):

    class Meta:
        model = FileMD

        fields = ('title', 'prot_name', 'traj', 'coor', 'group', 'chains', 'radii', 'lipids', 'resolution', 'apps', 'email')
        labels = {
            'prot_name': 'Give a name to your protein(s):',
            'traj': 'Upload your trajectory file.',
            'coor': 'Upload your coordinate file.',
            'group': 'Would you like to group lipids according to their headgroup type?',
            'chains': 'Would you like to group identical proteins/chains together (measuring thus average properties)?',
            'radii': 'Distance cutoff:',
            'lipids': 'Consider only the following lipids (comma separated, leave blank for all lipids)',
            'resolution': 'Select the appropriate resolution:',
            'apps': 'Type of analysis:',
            'email': 'Provide an email to notify you when results are done (OPTIONAL).'
        }
