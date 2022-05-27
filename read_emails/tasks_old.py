import time

from django.core.mail import send_mail
from .celery import app
from .services import get_mail_old, send_notification, runjob
from robots.models import Robots
from django.conf import settings
from celery import shared_task, Celery


# celery = Celery('runjobs', broker='amqp://guest@localhost//') #!


@app.task
def performer(arg):
    print(arg)
    #print(arg)


@app.task
def dispatcher():
    robots = Robots.objects.all()
    rbt_names = []
    full_name_email_dict = {}
    for robot in robots:
        name = robot.name
        rbt_names.append(name)
        robot_emails = list(Robots.objects.get(name=name).email.all())
        full_name_email_dict[name] = robot_emails
    run_data = get_mail.get_mails(subjs_addr=full_name_email_dict, subjs=rbt_names, Robots=Robots)
    for x in range(11):
        performer.delay(x)


# app.conf.beat_schedule = {
#     'task-name': {
#         'task': 'tasks.dispatcher',  # instead 'show'
#         'schedule': 5.0,
#         'args': (42,),
#     },
# }
# app.conf.timezone = 'UTC'


@app.task
def read_mails():
    # state = MailCheckState.objects.get(task_name='read_mails')
    # if state:
    print('Запуск таска')
    robots = Robots.objects.all()
    rbt_names = [x.name for x in robots]

    rbt_names = []
    full_name_email_dict = {}
    # Перебираем все записи модели Robots
    for robot in robots:
        # Добавим имя робота в список имён, который одновременно является списком допустимых тем писем
        name = robot.name
        rbt_names.append(name)
        # Для каждой записи модели получим список email-адресов
        robot_emails = list(Robots.objects.get(name=name).email.all())
        # пополним словарь "имя:список адресов" ("допустимая тема:список адресов")
        full_name_email_dict[name] = robot_emails
    # Вызовем функцию проверки почты на наличие писем, у кот-х тема и адрес отправителя
    # Соответствуют записи в словаре "full_name_email_dict"
    # Функция вернёт аналогичный словарь, составленный на основе этих писем
    run_data = get_mail.get_mails(subjs_addr=full_name_email_dict, subjs=rbt_names, Robots=Robots)
    # Для каждой записи полученного словаря выполним запуск робота при помощи функции "runjob.run"
    for rbt, address in run_data.items():
        result = runjob.run(process_name=rbt, model=Robots)
        if not result:
            mail_body = f'Не удалось запустить процесс "{rbt}", обратитесь в тех. поддержку'
        else:
            mail_body = f'Процесс "{rbt}" успешно запущен'
        send_notification.send(subj='Уведомление о запуске процесса',
                               body=mail_body,
                               addrs=(address,))


    #
    # # Словарь, где ключ = имя процесса, значение = разрешенные адреса отправителей
    # # Создали словарь при помощи списочного выражения
    # full_name_email_dict = {rbt: Robots.objects.get(name=rbt).email for rbt in rbt_names}
    # emails_dict = {rbt: Robots.objects.filter(title=rbt)[0].allowed_emails for rbt in rbt_names}
    # run_data = get_mail.get_mails(subjs_addr=emails_dict, subjs=rbt_names)
    #
    # for rbt, address in run_data.items():
    #     result = runjob.run(process_name=rbt, model=Robots)
    #     if not result:
    #         mail_body = f'Не удалось запустить процесс {rbt}, обратитесь в тех. поддержку'
    #     else:
    #         mail_body = f'Процесс {rbt} успешно запущен'
    #     send_notification.send(subj='Уведомление о запуске процесса',
    #                            body=mail_body,
    #                            addrs=(address,))
    # else:
    #     print('Таск не должен выполнятьсяя')

# @app.task
# def my_task(a, b):
#     c = a + b
#     return c
#
#
# @app.task
# def my_task_as(d, e):
#     c = d + e
#     return c
#
#
# @app.task(bind=True, default_retry_delay=5*60)
# # default_retry_delay=5*60 -> ч/з ск. секунд таска повторится в случае исключения
# def my_task_retry(self, x, y):
#     try:
#         return x + y
#     except Exception as exc:
#         raise self.retry(exc=exc, countdown=10)
#         # повторить таску  ч/з 60 сек
#         # если не укажем "countdown", то
#         # таска повторится ч/з 5*60 сек
#
#
# @shared_task()
# def my_sh_task(msg):
#     return msg + "!!!"
