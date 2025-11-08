from django.contrib import admin
from django.urls import path, include
from mailing.apps import MailingConfig
from . import views

app_name = MailingConfig.name

urlpatterns = [
    # Главная / статистика
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Получатели
    path('recipients/', views.RecipientListView.as_view(), name='recipients_list'),
    path('recipients/add/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/edit/', views.RecipientUpdateView.as_view(), name='recipient_edit'),
    path('recipients/<int:pk>/delete/', views.RecipientDeleteView.as_view(), name='recipient_delete'),

    # Сообщения
    path('messages/', views.MessageListView.as_view(), name='messages_list'),
    path('messages/add/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', views.MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),

    # Рассылки
    path('mailings/', views.MailingListView.as_view(), name='mailings_list'),
    path('mailings/add/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_edit'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.send_mailing_now, name='mailing_send'),

    # Попытки рассылок
    path('mailings/<int:mailing_id>/attempts/', views.AttemptListView.as_view(), name='attempts_list'),
]
