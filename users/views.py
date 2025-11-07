from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from dotenv import load_dotenv
import os

from .forms import CustomUserCreationForm
from mailing.models import Mailing

load_dotenv(override=True)

User = get_user_model()


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('catalog:index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в наш сервис'
        message = 'Спасибо, что зарегистрировались в нашем сервисе!'
        from_email = os.getenv('EMAILHOSTUSER')
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)


def is_manager(user):
    return hasattr(user, 'profile') and user.profile.role == 'manager'


@user_passes_test(is_manager)
def users_list(request):
    users = User.objects.all().select_related('profile')
    return render(request, 'users/users_list.html', {'users': users})


@user_passes_test(is_manager)
def toggle_block_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile
    profile.is_blocked = not profile.is_blocked
    profile.save()

    if profile.is_blocked:
        messages.warning(request, f'Пользователь {user.username} заблокирован.')
    else:
        messages.success(request, f'Пользователь {user.username} разблокирован.')

    return redirect('users:users_list')


@user_passes_test(is_manager)
def deactivate_mailing(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    if mailing.status != Mailing.STATUS_FINISHED:
        mailing.status = Mailing.STATUS_FINISHED
        mailing.save()
        messages.info(request, f'Рассылка "{mailing}" была отключена менеджером.')
    else:
        messages.info(request, f'Рассылка "{mailing}" уже завершена.')

    return redirect('mailing:mailings_list')
