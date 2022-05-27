from django.shortcuts import render
from .models import Robots, Email, Clients
from django.views.generic import UpdateView, CreateView, DetailView, DeleteView
from .forms import RobotsForm, EmailsForm, ClientsForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


@login_required
def robots(request):
    context = {'robots': Robots.objects.all(), 'emails': Email.objects.all()}
    return render(request, 'robots/robots.html', context)


class RobotsUpdate(LoginRequiredMixin, UpdateView):
    model = Robots
    form_class = RobotsForm
    success_url = reverse_lazy('account')
    template_name = 'robots/add.html'

    def get_form_kwargs(self):
        """Функция, позволяющая передать объект request object в форму.
         В жальнейшем из этого объекта будет получено имя пользователя сайта"""

        kwargs = super(RobotsUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class RobotsCreate(LoginRequiredMixin, CreateView):
    model = Robots
    form_class = RobotsForm
    success_url = reverse_lazy('account')
    template_name = 'robots/add.html'

    def get_context_data(self, **kwargs):
        user_name = self.request.user
        context = super().get_context_data(**kwargs)
        context['emails'] = Email.objects.all()
        # context['form'] = RobotsForm({'user_name': user_name})
        return context

    def form_valid(self, form):
        # account = form.save(commit=False)
        client = Clients.objects.get(client_name=self.request.user)
        form.instance.client = client
        form.save
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Функция, позволяющая передать объект request object в форму.
         В жальнейшем из этого объекта будет получено имя пользователя сайта"""

        kwargs = super(RobotsCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class RobotsDetail(LoginRequiredMixin, DetailView):
    # наша модель
    model = Robots
    # путь к динамической странице
    template_name = 'robots/robot.html'
    # кл. слово, по кот. будем передавать объект в шаблон
    context_object_name = 'robot'


class RobotsDeleteView(LoginRequiredMixin, DeleteView):
    model = Robots
    template_name = 'robots/robot-delete.html'
    success_url = reverse_lazy('account')


class EmailCreate(LoginRequiredMixin, CreateView):
    model = Email
    template_name = 'robots/emails.html'
    form_class = EmailsForm
    success_url = reverse_lazy('account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emails'] = Email.objects.all()
        return context

    def form_valid(self, form):
        # account = form.save(commit=False)
        form.instance.user_name = self.request.user
        form.save
        return super().form_valid(form)


class EmailDelete(LoginRequiredMixin, DeleteView):
    model = Email
    template_name = 'robots/email-delete.html'
    success_url = reverse_lazy('account')


class EmailUpdate(LoginRequiredMixin, UpdateView):
    model = Email
    template_name = 'robots/emails.html'
    context_object_name = 'email'
    form_class = EmailsForm
    success_url = reverse_lazy('account')


class ClientCreate(LoginRequiredMixin, CreateView):
    model = Clients
    form_class = ClientsForm
    template_name = 'robots/clients.html'
    success_url = reverse_lazy('account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Clients.objects.all()
        return context

    def form_valid(self, form):
        # account = form.save(commit=False)
        form.instance.client_name = self.request.user
        form.save
        return super().form_valid(form)


class ClientDetail(LoginRequiredMixin, DetailView):
    model = Clients
    template_name = 'robots/client.html'
    context_object_name = 'client'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            print('yyyy')
            return HttpResponseRedirect('/success/')
        else:
            print('nnnnn')

        return render(request, self.template_name, {'form': form})


class ClientDelete(LoginRequiredMixin, DeleteView):
    model = Clients
    template_name = 'robots/client-delete.html'
    success_url = reverse_lazy('account')
    context_object_name = 'client'


class ClientUpdate(LoginRequiredMixin, UpdateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('account')
    template_name = 'robots/clients.html'
