from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView


urlpatterns = [
    path('', include('main.urls'), name='home'),
    path('robots/', include('robots.urls'), name='robots'),
]
