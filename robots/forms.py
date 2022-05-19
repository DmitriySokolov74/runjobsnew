from django.forms import ModelForm
from .models import Robots, Email, Clients


class RobotsForm(ModelForm):
    class Meta:
        model = Robots
        fields = ('name', 'info', 'email', 'client')


class EmailsForm(ModelForm):
    class Meta:
        model = Email
        fields = ('email', )


class ClientsForm(ModelForm):
    class Meta:
        model = Clients
        fields = ('client_name', 'client_id', 'user_key', 'org', 'folder', 'tenant', 'user')


