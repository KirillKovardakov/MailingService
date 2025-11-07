from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.utils import timezone
from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Отправка сообщений по активным рассылкам'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='ID конкретной рассылки для отправки')

    def handle(self, *args, **options):
        mailing_id = options.get('id')

        if mailing_id:
            mailings = Mailing.objects.filter(id=mailing_id)
        else:
            now = timezone.now()
            mailings = Mailing.objects.filter(
                start_at__lte=now,
                end_at__gte=now
            ).exclude(status=Mailing.STATUS_FINISHED)

        if not mailings.exists():
            raise CommandError('Нет доступных рассылок для отправки.')

        for mailing in mailings:
            self.stdout.write(self.style.MIGRATE_HEADING(f'Отправка рассылки #{mailing.id}'))
            recipients = mailing.recipients.all()
            message = mailing.message

            sent_count = 0
            failed_count = 0

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

            self.stdout.write(
                self.style.SUCCESS(
                    f'Рассылка #{mailing.id} завершена: успешно — {sent_count}, ошибок — {failed_count}.'
                )
            )
