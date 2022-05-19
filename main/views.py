from robots.models import Robots
from django.shortcuts import render
from .forms import SearchRobotsForm


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
