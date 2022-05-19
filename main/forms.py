from django import forms
from robots.models import Robots


# Форма запроса с одним полем
class SearchRobotsForm(forms.Form):
    query = forms.CharField()
