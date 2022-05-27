from django.contrib import admin
from django.urls import path, include
from .views import post_search, home, SignUp, account, go_admin
from robots.views import ClientCreate, ClientUpdate, ClientDelete, ClientDetail, EmailDelete, EmailUpdate


urlpatterns = [
    #path('', post_search, name='home'),
    path('', home, name='home'),
    path('robots/', include('robots.urls')),
    path('admin/', admin.site.urls),
    path('admin/login', go_admin, name='go_admin'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignUp.as_view(), name='signup'),
    path('accounts/profile/', account, name='account'),
    path('clients', ClientCreate.as_view(), name="clients"),
    path('client/<int:pk>/', ClientDetail.as_view(), name="client-detail"),
    path('client/<int:pk>/update/', ClientUpdate.as_view(), name="client-update"),
    path('client/<int:pk>/delete/', ClientDelete.as_view(), name="client-delete"),
    path('accept_email/<int:pk>/delete', EmailDelete.as_view(), name='email-delete'),
    path('accept_email/<int:pk>/update', EmailUpdate.as_view(), name='email-update'),
]
