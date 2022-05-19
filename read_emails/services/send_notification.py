from django.core.mail import send_mail
from django.conf import settings


def send(subj, body, addrs):
    '''
    :param subj: str
    :param body: str
    :param addrs: list<str>
    :return: None
    '''
    send_mail(
            subj,
            body,
            settings.EMAIL_HOST_USER,
            addrs,
            fail_silently=False,
    )
