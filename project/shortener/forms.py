# project/shortener/forms.py

from django import forms


class DirectionForm(forms.Form):
    """The main form of the app."""

    target = forms.URLField(label='Long link', widget=forms.TextInput(attrs={'placeholder': 'Enter your link here'}))
    subpart = forms.CharField(label='Alias', required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'Your alias (optional)'}))
