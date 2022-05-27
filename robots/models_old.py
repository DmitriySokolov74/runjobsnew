import uuid
from django.db import models
from django.conf import settings


class EmailService(models.Model):
    '''
    Почтовые службы (gmail, yandex, mail.ru)
    '''
    service_name = models.CharField('Имя почтовой службы', max_length=50, unique=True)
    use_ssl = models.BooleanField('SSL')
    use_tls = models.BooleanField('TLS')
    host_imap = models.CharField('Сервер imap', max_length=50)
    port_imap = models.IntegerField('Порт imap', editable=False, default=993)
    host_smtp = models.CharField('Сервер smtp', max_length=50)
    port_smtp = models.IntegerField('Порт smtp', editable=False)


class Email(models.Model):
    email = models.EmailField(unique=True, verbose_name="Разрешённая почта")
    #some_field = models.UUIDField(unique=True, default=uuid.uuid4)
    user_name = models.CharField(verbose_name="Пользователь сайта", max_length=100, blank=True, null=True) #Auto

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Разрешенный адрес запуска"
        verbose_name_plural = "Разрешенные адреса запуска"


# Данные из оркестраторов клиентов
class Clients(models.Model):
    client_name = models.CharField('Имя клиента', unique=False, max_length=300) #Auto
    client_id = models.CharField('id клиента', unique=False, max_length=300)
    user_key = models.CharField('Ключ клиента', unique=False, max_length=300)
    org = models.CharField('Имя организации', unique=False, max_length=300)
    folder = models.CharField('Имя папки', max_length=300)
    tenant = models.CharField('Имя тенанта', max_length=300)
    # uipath_email = models.EmailField('Почта UIPath', unique=False, max_length=300, default="None")
    # service_email = models.EmailField('Сервисная почта', unique=False, max_length=300, null=True, blank=True) #EMAIL_HOST_USER
    # service_password = models.CharField('Пароль почтового сервиса', max_length=200, null=True, blank=True)
    # service = models.ForeignKey(EmailService, on_delete=models.PROTECT, default='gmail')


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
    #email = models.ManyToManyField(Email) #Auto
    client = models.ForeignKey(Clients, on_delete=models.PROTECT, null=True, blank=True) #Auto
    # db_index - уникальное поле

    def __str__(self):
        return self.name

    # # куда переадресовывать user'а после обновления в БД
    # def get_absolute_url(self):
    #     return f'/robots/{self.id}'

    class Meta:
        verbose_name = 'Робот'
        verbose_name_plural = 'Роботы'



