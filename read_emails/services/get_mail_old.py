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


# от кого ждем письма
# sender_init = 'raskalovdima@yandex.ru'
# Ищется среди входящих писем письмо от адресанта [adresant] с темой [subj] и выводится дата из тела этого письма
# В случае ошибки или отсутствия писем выводится сообщение ошибки

def encoded_words_to_text(encoded_words):
    '''
	Преобразует заголовок письма формата [=?charset?decoding?text?=]
	в читабельный текст
	'''
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


def get_mails(subjs_addr, subjs, Robots):
    '''
    :param subjs_addr: словарь "тема:разрешенные адреса (ч/з ;)"
    :param subjs: список допустимых тем письма
    :param Robots: Модель Robots
    :return: Словарь имя процесса: адрес отправителя для запуска по API
    '''
    try:
        # учётные данные
        print('Тело функции get_mails')
        out_subj_addr = {}
        username = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        server_imap = settings.GET_EMAIL_HOST
        mail = imaplib.IMAP4_SSL(host=server_imap, port=settings.GET_EMAIL_PORT)
        # print("username:", username, "password:", password)
        mail.login(username, password)

        mail.list()
        mail.select("inbox")

        # Поиск последнего письма
        result, data = mail.search(None, "UNSEEN")  # Получаем массив со списком найденных почтовых сообщений
        ids = data[0]  # Сохраняем в переменную ids строку с номерами писем
        id_list = ids.split()  # Получаем массив номеров писем
        if len(id_list) == 0:
            print('Нету новых писем')
        # ПЕРЕБОР ПИСЕМ:
        for cur_mail_id in id_list:
            try:
                latest_email_id = cur_mail_id
                # latest_email_id = id_list[-1] #Задаем переменную latest_email_id, значением которой будет номер последнего письма
                result, data = mail.fetch(latest_email_id,
                                          "(RFC822)")  # Получаем письмо с идентификатором latest_email_id (последнее письмо).
                raw_email = data[0][1]  # В переменную raw_email заносим необработанное письмо
                raw_email_string = raw_email.decode(
                    'utf-8')  # Переводим текст письма в кодировку UTF-8 и сохраняем в переменную raw_email_string

                # чтение заголовков
                email_message = email.message_from_string(raw_email_string)
                #############FROM################
                from_list = []
                try:
                    for from_sub in email.utils.parseaddr(email_message['From']):
                        decode_sub = encoded_words_to_text(from_sub)
                        from_list.append(encoded_words_to_text(from_sub))
                    all_addr_str = ' '.join(from_list)
                    print(f'all_addr_str = {all_addr_str}')
                    re_template = "\S+@\w+\.\w{2,4}"
                    mail_addr_str = re.search(re_template, all_addr_str).group(0)
                    print(f'mail_addr_str = {mail_addr_str}')
                    found_addr = mail_addr_str
                    # if not mail_addr_str in addresses_subjs:
                    #     print(f'Адресант \'{mail_addr_str}\' не входит в список разрешенных адресантов, пропуск текущего письма')
                    #     mail.store(cur_mail_id, '+FLAGS', '\Seen')
                    #     continue
                    # else:
                    #     print(f'Адресант \'{mail_addr_str}\' входит в список разрешенных, осуществим проверку темы в данном письме')
                    #     found_addr = mail_addr_str
                except:
                    print(f'Ошибка при чтении адресанта письма: {traceback.format_exc()}')
                    mail.store(cur_mail_id, '+FLAGS', '\Seen')
                    continue
                #############SUBJECT##############
                full_subject = ''
                print('email_message: ' + email_message['Subject'])
                for header_subject in email_message['Subject'].split('\n'):
                    try:
                        full_subject += encoded_words_to_text(header_subject.strip())
                    except:
                        print('Ошибка преобразования заголовка SUBJECT')
                try:
                    print('Тема письма: ' + full_subject)
                    # В теме указан процесс, который мы сможем запустить?
                    if subjs.count(full_subject) == 0:
                        print('Тема письма не совпала с требуемой, пропуск текущего письма')
                        mail.store(cur_mail_id, '+FLAGS', '\Seen')
                        continue
                    else:
                        print('Тема письма совпала с требуемой')
                        found_subj = full_subject
                        # экземпляр с именем, совпадающем с темой письма
                        robot_instance = Robots.objects.get(name=found_subj)
                        # получим набор всех экземпляров писем для найденного экземпляра робота
                        emails_query_set = robot_instance.email.all()
                        # получим список значений поля 'email' экземпляров писем
                        emails = [m.email for m in emails_query_set]
                        print(f'type={str(type(emails))}')
                        print(f'count = {str(emails.count)}')
                        for m in emails:
                            print(f'!!!!!!{m}')
                        # Отправителю разрешено запускать данного робота?
                        if found_addr in emails:
                            out_subj_addr[found_subj] = found_addr
                            print(f'Адресату письма {found_addr} разрешено запускать job')
                        else:
                            print(f'Адресату письма {found_addr} не разрешено запускать job')
                        # if found_subj in subjs_addr and found_addr in subjs_addr[found_subj]:
                        #     out_subj_addr[found_subj] = found_addr
                        #     print(f'Адресату письма {found_addr} разрешено запускать job')
                        # else:
                        #     print(f'Адресату письма {found_addr} не разрешено запускать job')
                except:
                    print('Тема письма: НЕ УДАЛОСЬ ПРОЧЕСТЬ, пропуск текущего письма')
                    print(f'Текст ошибки: {traceback.format_exc()}')
                    mail.store(cur_mail_id, '+FLAGS', '\Seen')
                    continue
            except:
                print('Общая ошибка чтения письма, пропуск текущего письма...')
                continue
            # Помечаем письмо как прочтённое
            print("Помечаем письма как прочитанное")
            mail.store(cur_mail_id, '+FLAGS', '\Seen')
            print("Письмо помечено как прочитанное")
            print('@@@-----END MAIL-----@@@')
        # Закончили перебор писем

    # ошибки в теле цикла перебора писем:
    except TimeoutError:
        print('Не удалось подключиться к серверу: превышен Timeout')
    except:
        print('Неизвестная ошибка при чтении письма или авторизации в почте: ', traceback.format_exc())
    else:
        print('Чтение входящих сообщений прошло без критических ошибок')
    return out_subj_addr
