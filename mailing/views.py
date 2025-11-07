from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)

from .models import Recipient, Message, Mailing, MailingAttempt, Profile
from .forms import RecipientForm, MessageForm, MailingForm
from .permissions import UserOrManagerMixin


# ======= DASHBOARD =======
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'mailing/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        mailings = Mailing.objects.filter(owner=user)
        ctx['total_mailings'] = mailings.count()
        ctx['active_mailings'] = mailings.filter(status=Mailing.STATUS_RUNNING).count()
        ctx['unique_recipients'] = Recipient.objects.filter(owner=user).count()
        return ctx

    def get_queryset(self):
        queryset = cache.get('my_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('my_queryset', queryset, 60 * 15)  # Кешируем данные на 15 минут
        return queryset


# ======= RECIPIENTS =======
@method_decorator([login_required, cache_page(60 * 15)], name='dispatch')
class RecipientListView(UserOrManagerMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipients_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        user = self.request.user
        profile = user.profile

        if profile.role == 'manager':
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


@method_decorator(login_required, name='dispatch')
class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipients_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Получатель успешно добавлен.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipients_list')

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class RecipientDeleteView(DeleteView):
    model = Recipient
    success_url = reverse_lazy('mailing:recipients_list')

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


# ======= MESSAGES =======
@method_decorator([login_required, cache_page(60 * 15)], name='dispatch')
class MessageListView(ListView):
    model = Message
    template_name = 'mailing/messages_list.html'
    context_object_name = 'messages_list'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:messages_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение создано.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:messages_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('mailing:messages_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


# ======= MAILINGS =======
@method_decorator([login_required, cache_page(60 * 15)], name='dispatch')
class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailings_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        profile = user.profile

        if profile.role == 'manager':
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


@method_decorator(login_required, name='dispatch')
class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailings_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка создана.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailings_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailing:mailings_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


@method_decorator([login_required, cache_page(60 * 15)], name='dispatch')
class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        if profile.role == 'manager':
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


@login_required
def send_mailing_now(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    recipients = mailing.recipients.all()
    message = mailing.message

    sent_count, failed_count = 0, 0
    for recipient in recipients:
        try:
            send_mail(
                subject=message.subject,
                message=message.body,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response='OK'
            )
            sent_count += 1
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e)
            )
            failed_count += 1

    mailing.update_status_by_time(timezone.now())
    messages.info(request, f'Рассылка завершена: успешно — {sent_count}, ошибок — {failed_count}.')
    return redirect('mailing:mailing_detail', pk=pk)


# ======= ATTEMPTS =======
@method_decorator([login_required, cache_page(60 * 15)], name='dispatch')
class AttemptListView(ListView):
    model = MailingAttempt
    template_name = 'mailing/attempts_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        mailing = get_object_or_404(Mailing, pk=self.kwargs['mailing_id'], owner=user)
        if profile.role == 'manager':
            return MailingAttempt.objects.all().select_related('recipient')

        return MailingAttempt.objects.filter(mailing=mailing).select_related('recipient')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mailing'] = get_object_or_404(Mailing, pk=self.kwargs['mailing_id'], owner=self.request.user)
        return ctx
