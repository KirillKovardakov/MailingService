from django.contrib import admin
from django.urls import path, include
from mailing.apps import MailingConfig

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailing.urls', namespace='mailing')),
    path('users/', include('users.urls', namespace='users')),
]
