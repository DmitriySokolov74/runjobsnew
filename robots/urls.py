"""runjobsnew URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from .views import RobotsCreate, RobotsUpdate, RobotsDeleteView, RobotsDetail, robots, EmailCreate, ClientCreate


urlpatterns = [
    path('', robots, name='robots'),
    path('add', RobotsCreate.as_view(), name='robot-add'),
    path('<int:pk>/update', RobotsUpdate.as_view(), name='robot-update'),
    path('<int:pk>/delete', RobotsDeleteView.as_view(), name='robot-delete'),
    path('<int:pk>/', RobotsDetail.as_view(), name='robot-detail'),
    path('emails', EmailCreate.as_view(), name="emails"),
    path('clients', ClientCreate.as_view(), name="clients")
]
