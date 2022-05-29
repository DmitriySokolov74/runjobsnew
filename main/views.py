from robots.models import Robots, Clients, Email
from django.shortcuts import render
from .forms import SearchRobotsForm
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required


@login_required
def post_search(request):
    form = SearchRobotsForm()
    if 'query' in request.GET:
        form = SearchRobotsForm(request.GET)
        # теперь form содержит данные, введенные в форму
        if form.is_valid():
            # словарь введенных в форму данных
            cd = form.cleaned_data
            keyword = cd['query']
            results = Robots.objects.filter(name__icontains=keyword)
            # число найденных в модели Robots записей
            results_count = results.count()
            context = {'form': form, 'cd': cd, 'results': results, 'results_count': results_count}
            return render(request, 'main/index.html', context)
    else:
        form = SearchRobotsForm()
    context = {'form': form}
    return render(request, 'main/index.html', context)


@login_required
def home(request):
    return render(request, "main/index.html")


@login_required
def go_admin(request):
    return render(request)



class SignUp(CreateView):
    """Контроллер авторизации пользователя"""
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def account(request):
    clients_info = Clients.objects.filter(client_name=request.user)
    run_emails = Email.objects.filter(user_name=request.user)
    client_info = clients_info[0] if clients_info.count() == 1 else None
    run_emails = run_emails if run_emails.count() > 0 else None
    robots = Robots.objects.filter(client=client_info) if client_info is not None else None
    context = {'request': request, 'client_info': client_info, 'run_emails': run_emails, 'robots': robots}
    return render(request, "main/profile.html", context)
