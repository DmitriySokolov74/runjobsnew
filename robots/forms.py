from django.forms import ModelForm
from .models import Robots, Email, Clients
from django import forms
from django.db import models


class RobotsForm(ModelForm):
    class Meta:
        model = Robots
        fields = ('name', 'info', 'email')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RobotsForm, self).__init__(*args, **kwargs)
        if self.request is not None:
            self.fields['email'].queryset = Email.objects.filter(user_name=self.request.user)


    # def __init__(self, user, *args, **kwargs):
    #     self.user = user
    #     super(RobotsForm, self).__init__(*args, **kwargs)
    #     self.fields['email'].queryset = Email.objects.filter(user_name=self.user)


class EmailsForm(ModelForm):
    class Meta:
        model = Email
        fields = ('email', 'email_owner_name')


class ClientsForm(ModelForm):
    class Meta:
        model = Clients
        password = forms.CharField(widget=forms.PasswordInput())
        fields = ('client_id', 'user_key', 'org', 'folder', 'tenant', 'user', 'service',
                  'service_email', 'service_password', 'service_mail_folder')

