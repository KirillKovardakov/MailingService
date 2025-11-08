from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    """Дополнительная информация о пользователе: роль и блокировка.
    Используется OneToOneField с AUTH_USER_MODEL.
    """
    ROLE_USER = 'user'
    ROLE_MANAGER = 'manager'
    ROLE_CHOICES = [
        (ROLE_USER, 'Пользователь'),
        (ROLE_MANAGER, 'Менеджер'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile({self.user.username}, {self.role})"

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Recipient(models.Model):
    """
    Класс "Получатели"
    """

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipients')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} ({self.full_name})"


    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'


class Message(models.Model):
    """
    Класс "Сообщение"
    """

    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    """
    Класс "Рассылка"
    """

    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_FINISHED = 'finished'
    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_RUNNING, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings')
    recipients = models.ManyToManyField(Recipient, related_name='mailings')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mailings')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f"Mailing({self.id}) — {self.message.subject}"

    def update_status_by_time(self, now=None):
        now = now or timezone.now()
        if now > self.end_at:
            self.status = self.STATUS_FINISHED
        elif now >= self.start_at:
            # If it was created but sending started, set running
            if self.status == self.STATUS_CREATED:
                self.status = self.STATUS_RUNNING
        self.save(update_fields=['status'])


class MailingAttempt(models.Model):
    """
    Класс "Статус рассылки"
    """

    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='attempts')
    attempted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Статус рассылки'
        verbose_name_plural = 'Статусы рассылок'
        ordering = ['-attempted_at']

    def __str__(self):
        return f"Attempt(mailing={self.mailing_id}, recipient={self.recipient.email}, status={self.status})"
