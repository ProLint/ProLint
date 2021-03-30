from django import forms

class FindResultForm(forms.Form):
    task_id = forms.CharField(label='Your provided ID', max_length=36, widget=forms.Textarea(attrs={'cols': 60, 'rows': 1}))
