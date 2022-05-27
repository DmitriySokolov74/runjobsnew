from django.core.mail import send_mail
from django.conf import settings
from read_emails.services.get_data import log
import traceback
from django.conf import settings


print("!!!!!!!!!!!!"+settings.PROJECT_ROOT)

def send(subj, body, addrs, from_name, auth_user, auth_password, host, port, use_ssl, use_tls):
    """Вызов стандартной django функции (send_mail)
    с предварительной переинициализацией системных переменных
    под конкретный сервисный почтовый ящик
    """
    try:
        settings.EMAIL_HOST = host
        settings.EMAIL_PORT = port
        settings.EMAIL_USE_SSL = use_ssl
        settings.EMAIL_USE_TLS = use_tls
        send_mail(subject=subj, message=body, from_email=from_name, recipient_list=addrs,
            fail_silently=False, auth_user=auth_user, auth_password=auth_password)
    except:
        log(f'Ошибка при отправке уведомления пользователю: "{traceback.format_exc()}"', 'warn')
