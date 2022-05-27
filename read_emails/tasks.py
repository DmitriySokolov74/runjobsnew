from django.core.mail import send_mail
from .celery import app
from .services import get_data, send_notification, runjob
from .services.get_data import log
from robots.models import Robots, Clients
import datetime


@app.task
def performer(service_email_address):
    """Функция-исполнитель, в которой вызываются основные сервисные функции:
    1) чтение сервисного почтового ящика (read_mailbox)
    2) отправка запроса на запуск ч/з API (run)
    3) отправка уведомления пользователю, отправившему письмо запуска, о статусе запуска (send_notification)
    """
    log(f'Чтение почтового ящика {service_email_address}', 'info')
    read_mails_data = get_data.read_mailbox(service_email_address=service_email_address)
    if read_mails_data['client_name'] is not None:
        client_name = read_mails_data.get('client_name')
        service = service_email = Clients.objects.get(client_name=client_name).service
        host_smtp = service.host_smtp
        port_smtp = service.port_smtp
        use_ssl = service.use_ssl
        use_tls = service.use_tls
        service_email = Clients.objects.get(client_name=client_name).service_email
        service_password = Clients.objects.get(client_name=client_name).service_password
        service_host = Clients.objects.get(client_name=client_name).service_password
        for robot, address in read_mails_data['mapping'].items():
            result = runjob.run(process_name=robot, client_name=client_name)
            if not result[0]:
                mail_body = f'Не удалось запустить процесс "{robot}", обратитесь в тех. поддержку\n'
                f'Текст ошибки: "{result[1]}"'
            else:
                mail_body = f'Процесс "{robot}" успешно запущен'
            send_notification.send(subj='Уведомление о запуске процесса', body=mail_body,
                                   addrs=(address,), from_name=service_email,
                                   auth_user=service_email, auth_password=service_password,
                                   host=host_smtp, port=port_smtp, use_ssl=use_ssl, use_tls=use_tls)


@app.task
def dispatcher():
    """Сервисная функция диспетчера, получающая коллекцию адресов всех сервисных
    почтовых ящиков и запускающая функцию-исполнитель (performer) для каждого адреса
    """
    service_emails = get_data.get_service_mails()
    for service_email in service_emails:
        # Создание задачи для исполнителя (performer)
        performer.delay(service_email)
