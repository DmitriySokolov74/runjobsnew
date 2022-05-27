import re
import imaplib
import email  # Импортируем модуль email для получения заголовков и тела писем
from email.header import decode_header
from django.conf import settings
import base64
import quopri
import traceback
import time
from robots.models import Robots, Email, Clients, EmailService


class BusinessError(Exception):
    """Класс бизнес-ошибки, которая вызывается при несоблюдении
    условий проверок в той или иной функции
    """
    def __init__(self, message, log_level):
        self.message = message
        print(f'{log_level}: {self.message}')


def log(message, level):
    """Функция лога
    """
    print(f'{level}: {message}')


def get_service_mails():
    """Возвращает список почтовых адресов всех сервисных почт, зарегистрированных на сайте
    """
    return [x.service_email for x in Clients.objects.all() if x.service_email is not None]

# от кого ждем письма
# sender_init = 'raskalovdima@yandex.ru'
# Ищется среди входящих писем письмо от адресанта [adresant] с темой [subj] и выводится дата из тела этого письма
# В случае ошибки или отсутствия писем выводится сообщение ошибки

def encoded_words_to_text(encoded_words):
    """Преобразует заголовок письма формата [=?charset?decoding?text?=]
	в читабельный текст
    """
    encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q|b|q])\?{1}(.+)\?{1}='
    full_encoded_text = ''
 	# Имеем дело с закодированной строкой?
    if encoded_words.find('=?') != -1:
        # Текст разбит символом перехода на нов строку?
        if encoded_words.find('\n') != -1:
            encoded_text = ''
            for line in encoded_words.split('\n'):
                encoded_text += re.match(encoded_word_regex, line).group(2)
                charset = re.match(encoded_word_regex, line).group(0)
                encoding = re.match(encoded_word_regex, line).group(1)
        # Текст разбит пробелом?
        elif encoded_words.find('?= =?') != -1:
            for line in encoded_words.split(' '):
                charset, encoding, encoded_text = re.match(encoded_word_regex, line).groups()
                full_encoded_text += encoded_text
            encoded_text = full_encoded_text
        # Текст ничем не разбит?
        else:
            charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
        if encoding.upper() == 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding.upper() == 'Q':
            byte_string = quopri.decodestring(encoded_text)
        return byte_string.decode(charset)
    else:
        return encoded_words


def get_clients_data(service_email_address):
    """Получение данных клиента по имени его сервисной почты (service_email_address)"""
    client = Clients.objects.get(service_email=service_email_address)
    service_data = EmailService.objects.get(service_name=client.service)
    return {'client': {
        'client_name': client.client_name,
        'client_id': client.client_id,
        'user_key': client.user_key,
        'org': client.org,
        'folder': client.folder,
        'tenant': client.tenant,
        'user': client.user,
        'service': client.service,
        'service_password': client.service_password,
        'service_mail_folder': client.service_mail_folder,
        'use_ssl': service_data.use_ssl,
        'use_tls': service_data.use_tls,
        'host_imap': service_data.host_imap,
        'port_imap': service_data.port_imap,
        'host_smtp': service_data.host_smtp,
        'port_smtp': service_data.port_smtp,
    }}


def get_run_emails_data(client_name):
    """Получение всех существующих почтовых адресов, используемых для запуска"""
    emails = Email.objects.filter(user_name=client_name)
    result = [x.email for x in emails]
    return result


def get_robot_data(client_name):
    """Возвращает список объектов модели Robots для клиента client_name"""
    client = Clients.objects.get(client_name=client_name)
    result = Robots.objects.filter(client=client)
    return result


def read_mailbox(service_email_address):
    """Чтение почтового ящика, на который приходят письма о запуске
    Возвращает словарь, содержащий имя пользователя нашего сайта (client_name) и
    словарь соответствий имени процесса и адреса отправителя для запуска по API (mapping)
    """
    try:
        out_data = {
            'client_name': None,
            'mapping': {}
        }
        client_data = get_clients_data(service_email_address)
        client_name = client_data['client']['client_name']
        out_data['client_name'] = client_name
        robots = get_robot_data(client_name=client_name)
        # Разрешенные темы письма
        acceptable_subjects = [x.name for x in robots]
        if robots.count() == 0:
            raise BusinessError(f'Не найдено роботов для клиента {client_name}', 'warn')
        host_imap = client_data['client']['host_imap']
        service_password = client_data['client']['service_password']
        service_mail_folder = client_data['client']['service_mail_folder']
        port_imap = client_data['client']['port_imap']
        mail = imaplib.IMAP4_SSL(host=host_imap, port=port_imap)
        mail.login(service_email_address, service_password)
        mail.list()
        mail.select(service_mail_folder)
        result, data = mail.search(None, "UNSEEN")
        ids = data[0]  # Сохраняем в переменную ids строку с номерами писем
        id_list = ids.split()  # Получаем массив номеров писем
        if len(id_list) == 0:
            raise BusinessError(f'Нету новых писем для клиента {client_name}', 'warn')
        for cur_mail_id in id_list:
            try:
                result, data = mail.fetch(cur_mail_id, "(RFC822)")
                # необработанное письмо
                raw_email = data[0][1]
                raw_email_string = raw_email.decode('utf-8')
                # чтение заголовков
                email_message = email.message_from_string(raw_email_string)
                log('Извлечение отправителя письма', 'info')
                from_list = []
                try:
                    for from_sub in email.utils.parseaddr(email_message['From']):
                        decode_sub = encoded_words_to_text(from_sub)
                        from_list.append(decode_sub)
                    # почтовый адрес отправителя письма
                    full_addr_str = ' '.join(from_list)
                    log(f'Отправитель письма: "{full_addr_str}"', 'info')
                    re_template = "\S+@\w+\.\w{2,4}"
                    mail_addr_str = re.search(re_template, full_addr_str).group(0)
                    log(f'Почтовый адрес отправителя письма: "{mail_addr_str}"', 'info')
                    found_address = mail_addr_str
                except:
                    log(f'Ошибка при чтении адресанта письма: "{traceback.format_exc()}"', 'error')
                    mail.store(cur_mail_id, '+FLAGS', '\Seen')
                    continue
                log('Извлечение темы письма', 'info')
                full_subject = ''
                log(f"email_message {email_message['Subject']}", 'info')
                for header_subject in email_message['Subject'].split('\n'):
                    try:
                        full_subject += encoded_words_to_text(header_subject.strip())
                    except:
                        log('Ошибка преобразования заголовка SUBJECT', 'error')
                try:
                    log(f'Тема письма: {full_subject}', 'info')
                    # Тема письма подходящая?
                    if acceptable_subjects.count(full_subject) == 0:
                        log(f'Тема письма "{full_subject}" не совпала с требуемой, пропуск текущего письма', 'warn')
                        mail.store(cur_mail_id, '+FLAGS', '\Seen')
                        continue
                    else:
                        log('Тема письма совпала с одной из требуемых', 'info')
                        found_subj = full_subject
                        # Список почтовых адресов, с которых разрешён запуск
                        run_emails = get_run_emails_data(client_name=client_name)
                        # Почтовый адрес письма подходящий?
                        if found_address in run_emails:
                            out_data['mapping'][found_subj] = found_address
                            log(f'Адресату письма {found_address} разрешено запускать job', 'info')
                        else:
                            log(f'Адресату письма {found_address} не разрешено запускать job', 'info')
                except:
                    log(f'Не удалось прочесть тему письма, ошибка: "{traceback.format_exc()}"', 'error')
                    mail.store(cur_mail_id, '+FLAGS', '\Seen')
                    continue
            except:
                log(f'Неизвестная ошибка чтения письма: "{traceback.format_exc()}"', 'error')
                continue
            # Помечаем письмо как прочтённое
            mail.store(cur_mail_id, '+FLAGS', '\Seen')
            log('Письмо прочтено успешно', 'info')
    except BusinessError:
        log('Чтение почтового ящика завершено с предупреждением', 'info')
    except TimeoutError:
        log('Чтение почтового ящика завершено с ошибкой таймаута', 'error')
    except:
        log(f'Чтение почтового ящика завершено с системной ошибкой при чтении письма или авторизации в почте: "{traceback.format_exc()}"', 'fatal')
    else:
        log('Чтение почтового ящика завершено успешно', 'info')
    return out_data
