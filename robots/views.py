from django.shortcuts import render
from .models import Robots, Email, Clients
from django.views.generic import UpdateView, CreateView, DetailView, DeleteView
from .forms import RobotsForm, EmailsForm, ClientsForm
from django.urls import reverse_lazy


def robots(request):
    context = {'robots': Robots.objects.all(), 'emails': Email.objects.all()}
    return render(request, 'robots/robots.html', context)


class RobotsUpdate(UpdateView):
    model = Robots
    form_class = RobotsForm
    success_url = reverse_lazy('robots')
    template_name = 'robots/add.html'


class RobotsCreate(CreateView):
    model = Robots
    form_class = RobotsForm
    success_url = reverse_lazy('robots')
    template_name = 'robots/add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emails'] = Email.objects.all()
        return context


class RobotsDetail(DetailView):
    # наша модель
    model = Robots
    # путь к динамической странице
    template_name = 'robots/robot.html'
    # кл. слово, по кот. будем передавать объект в шаблон
    context_object_name = 'robot'


class RobotsDeleteView(DeleteView):
    model = Robots
    template_name = 'robots/robot-delete.html'
    success_url = reverse_lazy('robots')


class EmailCreate(CreateView):
    model = Email
    template_name = 'robots/emails.html'
    form_class = EmailsForm
    success_url = reverse_lazy('emails')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emails'] = Email.objects.all()
        return context


class ClientCreate(CreateView):
    model = Clients
    form_class = ClientsForm
    template_name = 'robots/clients.html'
    success_url = reverse_lazy('clients')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Clients.objects.all()
        return context
