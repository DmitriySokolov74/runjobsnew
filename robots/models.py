from django.db import models
from django.conf import settings
import uuid
from django import forms


class PasswordField(forms.CharField):
    widget = forms.PasswordInput


class PasswordModelField(models.CharField):

    def formfield(self, **kwargs):
        defaults = {'form_class': PasswordField}
        defaults.update(kwargs)
        return super(PasswordModelField, self).formfield(**defaults)


class EmailService(models.Model):
    '''
    Почтовые службы (gmail, yandex, mail.ru),
    заполняются администратором сайта
    '''
    service_name = models.CharField('Имя почтовой службы', max_length=50, unique=True)
    use_ssl = models.BooleanField('SSL')
    use_tls = models.BooleanField('TLS')
    host_imap = models.CharField('Сервер imap', max_length=50)
    port_imap = models.IntegerField('Порт imap')
    host_smtp = models.CharField('Сервер smtp', max_length=50)
    port_smtp = models.IntegerField('Порт smtp')

    def __str__(self):
        return self.service_name

    class Meta:
        verbose_name = 'Почтовый сервис'
        verbose_name_plural = 'Почтовые сервисы'


class Email(models.Model):
    email = models.EmailField(verbose_name="Почта запуска")
    user_name = models.CharField(verbose_name="Пользователь сайта", max_length=100, blank=True, null=True)  # Auto
    email_owner_name = models.CharField(verbose_name="Владелец почты", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Разрешенный адрес запуска"
        verbose_name_plural = "Разрешенные адреса запуска"


# Данные из оркестраторов клиентов
class Clients(models.Model):
    # Имя пользователя сайта (заполняется автоматически для зарегистрированного пользователя)
    client_name = models.CharField('Имя клиента', unique=True, max_length=50)
    client_id = models.CharField('id клиента', unique=False, max_length=70)
    user_key = models.CharField('Ключ клиента', unique=False, max_length=70)
    org = models.CharField('Имя организации', unique=False, max_length=70)
    folder = models.CharField('Имя папки', max_length=70)
    tenant = models.CharField('Имя тенанта', max_length=70)
    user = models.EmailField('Почта пользователя uipath', max_length=70)
    service = models.ForeignKey(EmailService, on_delete=models.PROTECT, null=True, blank=True)
    service_email = models.EmailField('Сервисная почта', max_length=300, null=True, blank=True, unique=True)  # EMAIL_HOST_USER
    service_password = PasswordModelField('Пароль почтового сервиса', max_length=200, null=True, blank=True)
    service_mail_folder = models.CharField('Имя почтового ящика', max_length=200, default='inbox')

    def __str__(self):
        return self.client_name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Robots(models.Model):
    name = models.CharField('Имя', max_length=50, db_index=True)
    info = models.TextField('Описание', null=True, blank=True)
    date = models.DateTimeField('Дата добавления', auto_now_add=True)
    folder_id = models.IntegerField('id папки', null=True, blank=True)
    process_key = models.CharField('Ключ процесса', max_length=100, null=True, blank=True)
    robot_id = models.IntegerField('id робота', null=True, blank=True)
    email = models.ManyToManyField(Email) #Auto
    client = models.ForeignKey(Clients, on_delete=models.PROTECT, null=True, blank=True) #Auto
    # db_index - уникальное поле

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Робот'
        verbose_name_plural = 'Роботы'



