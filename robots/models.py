from django.db import models
from django.conf import settings


class Email(models.Model):
    email = models.EmailField(unique=True, verbose_name="Почта")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Разрешенный адрес запуска"
        verbose_name_plural = "Разрешенные адреса запуска"


# Данные из оркестраторов клиентов
class Clients(models.Model):
    client_name = models.CharField('Имя клиента', unique=True, max_length=50)
    client_id = models.CharField('id клиента', unique=True, max_length=70)
    user_key = models.CharField('Ключ клиента', unique=True, max_length=70)
    org = models.CharField('Имя организации', unique=True, max_length=70)
    folder = models.CharField('Имя папки', max_length=70)
    tenant = models.CharField('Имя тенанта', max_length=70)
    user = models.EmailField('Почта пользователя', unique=True, max_length=70)

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
    email = models.ManyToManyField(Email)
    client = models.ForeignKey(Clients, on_delete=models.PROTECT, null=True, blank=True)
    # db_index - уникальное поле

    def __str__(self):
        return self.name

    # # куда переадресовывать user'а после обновления в БД
    # def get_absolute_url(self):
    #     return f'/robots/{self.id}'

    class Meta:
        verbose_name = 'Робот'
        verbose_name_plural = 'Роботы'



