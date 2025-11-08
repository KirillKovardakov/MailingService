from django import forms
from .models import Recipient, Message, Mailing


class RecipientForm(forms.ModelForm):
    """Форма для создания и редактирования получателя рассылки."""
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите Ф.И.О.'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий'}),
        }


class MessageForm(forms.ModelForm):
    """Форма для создания и редактирования сообщения."""
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема письма'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Введите текст письма'}),
        }


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылки."""
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Дата и время начала'
    )
    end_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Дата и время окончания'
    )

    class Meta:
        model = Mailing
        fields = ['start_at', 'end_at', 'status', 'message', 'recipients']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
        labels = {
            'start_at': 'Дата и время первой отправки',
            'end_at': 'Дата и время окончания',
            'status': 'Статус',
            'message': 'Сообщение',
            'recipients': 'Получатели',
        }
