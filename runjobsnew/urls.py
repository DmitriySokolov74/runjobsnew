from django.urls import path, include


urlpatterns = [
    path('', include('main.urls'), name='home'),
    path('robots/', include('robots.urls'), name='robots'),
]
