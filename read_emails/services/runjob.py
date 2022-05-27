from django.conf import settings
import requests
import json
from traceback import format_exc
from robots.models import Robots, Clients
from read_emails.services.get_data import BusinessError, log


def get_token(url, body, timeout):
    """Получение токена от оркестратора
    :param url: URL запроса для получения токена
    :param body: словарь с параметрами оркестратора
    :param timeout: таймаут запроса (сек)
    :return: список [токен, результат: True-> успех, False -> неудача]
    """
    # Инициализация возвращаемого значения
    result = ["", False]
    try:
        response = requests.post(url, json=body, timeout=timeout)
        # Запрос выполнен успешно?
        if response.status_code == 200:
            token = response.json()['access_token']
            result = [token, True]
    except:
        log('Ошибка при получении токена', 'error')
    return result


# Getting folders id:
def get_folder_id(url, folder_name, tenant_name, token):
    """
    :param url: url для get запроса
    :param folder_name: имя папки (см. в оркестраторе)
    :param tenant_name: имя тенанта (см. в оркестраторе)
    :param token: токен, полученный ранее
    :return: список [id папки, bool]
    """
    result = ["", False]
    try:
        # Добавляем фильтр в URL, чтобы в ответе остались только результаты для нашей папки folder_name
        url_filter = url + f"?$Filter=FullyQualifiedName eq '{folder_name}'"
        response = requests.get(
        url_filter,
        headers={'X-UIPATH-TenantName': tenant_name, 'Authorization': f'Bearer {token}'},
        )
        if response.status_code == 200:
            folder_id = response.json()["value"][0].get("Id")
            result = [folder_id, True]
            log(f'folder_id="{folder_id}", type={str(type(folder_id))}', 'info')
    except:
        log(f'Не удалось извлечь id папки: {format_exc()}', 'error')
    return result


# Getting robots Releases:
def get_process_key(url, process_name, tenant_name, token):
    """
    :param url: url для get запроса
    :param process_name: имя процесса, которое указывается в теме письма
    :param tenant_name: имя тенанта (см. оркестратор)
    :param token: токен, полученный ранее
    :return: возвращает ключ процесса, необходимый для финального post запроса
    """
    result = ["", False]  # изначально инициализируем возвращаемое значение неудачей
    # фильтруем запрос для получения только тех значений, которые относятся к нашему процессу [process_name]
    url_filter = url + f"?$Filter=Name eq '{process_name}'"
    try:
        response = requests.get(
            url_filter,
            headers={'X-UIPATH-TenantName': tenant_name, 'Authorization': f'Bearer {token}'},
        )
        if response.status_code == 200:
            results_count = response.json()["@odata.count"]
            if results_count == 0:
                raise BusinessError(f'Не удалось найти в оркестраторе процесс "{process_name}"', 'warn')
            process_key = response.json()["value"][0].get("Key")
            result = [process_key, True]
            log(f'process_key={process_key}, type={str(type(process_key))}', 'info')
    except BusinessError:
        log('Процесс не запущен, функция "get_process_key"', 'warn')
    except:
        log(f'Не удалось получить ключ процесса: {format_exc()}', 'error')
    return result


# Get RobotsIds
def get_robot_id(url, folder_id, tenant_name, token, user_name):
    result = ["", False]
    url_filter = url + f"?$Filter=UserName eq '{user_name}'"
    # заголовки запроса
    headers = {
        "X-UIPATH-OrganizationUnitId": str(folder_id),
        "X-UIPATH-TenantName": tenant_name,
        "Authorization": f'Bearer {token}',
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(
            url_filter,
            headers=headers
        )
        if response.status_code == 200:
            # разпарсим из response нужное нам значение id робота:
            robot_id = response.json().get("value")[0].get("UnattendedRobot").get("RobotId")
            result = [robot_id, True]
            log(f'robot_id={robot_id}, type={str(type(robot_id))}', 'info')
    except:
        log(f'Не удалось получить id робота: {format_exc()}', 'error')
    return result


# Start Job
def start_job(url, process_key, robot_id, folder_id, token, tenant_name, timeout):
    """Функция отправки последнего запроса в оркестратор для запуска процесса
    :param url:
    :param process_key:
    :param robot_id:
    :param folder_id:
    :param token:
    :param tenant_name:
    :param timeout:
    :return:
    """
    body = {
      "startInfo": {
        "ReleaseKey": process_key,
        "Strategy": "Specific",
        "JobsCount": 0,
        "RobotIds": [robot_id],
        "JobPriority": "Normal",
      }
    }
    headers = {
        "X-UIPATH-OrganizationUnitId": str(folder_id),
        "X-UIPATH-TenantName": tenant_name,
        "Authorization": f'Bearer {token}',
        "Content-Type": "application/json"
    }
    result = False
    try:
        response = requests.post(url, data=json.dumps(body), headers=headers, timeout=timeout)
        if response.status_code == 201:
            result = True
            log('Job запущен', 'info')
        else:
            log(f'Job не запущен: статус = {str(response.status_code)}', 'error')
            log(f'Job не запущен: message = {str(response.json().get("message"))}', 'error')
            raise
    except:
        mes = "Не удалось запустить процесс: "
        try:
            error_message = str(response.json().get("message"))
            mes = mes + error_message
        except:
            mes = mes + "не удалось получить сообщение ошибки"
    return result


def run(process_name=None, client_name=None, token_timeout=30):
    """Последовательность отправок GET/POST запросов в оркестратор для получения данных,
    на основе которых будет отправлен итоговый запрос запуска процесса в оркестраторе (run job)
    :param process_name: тема письма, которая также должна совпадать с именем процесса в оркестраторе
    :param model:
    :param client_name:
    :param token_timeout:
    :return:
    """
    try:
        client = Clients.objects.get(client_name=client_name)
        robots = Robots.objects.filter(client=client, name=process_name)
        # Для одного клиента в таблице Robots должна содержаться только 1 запись
        if robots.count() != 1:
            raise BusinessError('В таблице роботов для данного клиента число записей не равно 1', 'warn')
        robot = robots[0]
        user_name_uipath = client.user
        client_id = client.client_id
        user_key = client.user_key
        body_token = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": user_key
        }
        org_id = client.org
        folder_name = client.folder
        tenant_name = client.tenant
        url_folder_id = settings.ORC_URL_FOLDER_ID.format(org_id, tenant_name)
        url_process_key = settings.ORC_URL_PROCESS_KEY.format(org_id, tenant_name)
        url_start_job = settings.ORC_URL_START_JOB.format(org_id, tenant_name)
        url_token = settings.ORC_URL_TOKEN
        url_robot_id = settings.ORC_URL_ROBOT_ID.format(org_id, tenant_name)
        error_message = ""
        total_result = [False, error_message]
        # 1 - получение токена
        token_result = get_token(url=url_token,
                                 body=body_token,
                                 timeout=token_timeout)
        if token_result[1] == False:
            raise ValueError("Токен не получен")
        token = token_result[0]
        # 2 - получение id папки
        if robot.folder_id is None:
            folder_id_result = get_folder_id(url=url_folder_id,
                                             folder_name=folder_name,
                                             tenant_name=tenant_name,
                                             token=token)
            if folder_id_result[1] == False:
                raise ValueError("id папки не получено")
            folder_id = folder_id_result[0]
            robot.folder_id = folder_id
        # 3 - получение ключа процесса
        if robot.process_key is None:
            process_key_result = get_process_key(url=url_process_key,
                                                 process_name=process_name,
                                                 tenant_name=tenant_name,
                                                 token=token)
            if process_key_result[1] == False:
                raise ValueError("ключ процесса не получен")
            process_key = process_key_result[0]
            robot.process_key = process_key
        # 4 - получение id робота
        if robot.robot_id is None:
            robot_id_result = get_robot_id(url=url_robot_id,
                                           folder_id=robot.folder_id,
                                           tenant_name=tenant_name,
                                           token=token,
                                           user_name=user_name_uipath)
            if not robot_id_result[1]:
                raise ValueError("id робота не получено")
            robot_id = robot_id_result[0]
            robot.robot_id = robot_id
        # 5 - start job
        start_job_result = start_job(url=url_start_job,
                                     process_key=robot.process_key,
                                     robot_id=robot.robot_id,
                                     folder_id=robot.folder_id,
                                     token=token,
                                     tenant_name=tenant_name,
                                     timeout=30)
        if not start_job_result:
            raise ValueError("job не запущен")
        else:
            total_result[0] = start_job_result
        # 6 - сохранение изменений записи БД для имени процесса
        robot.save()
        # return start_job_result
    except BusinessError:
        error_text = f'Запуск не прошёл проверку условий'
        log(error_text, 'warn')
        error_message = error_text
        total_result[1] = error_message
    except:
        error_text = f'Не удалось запустить процесс: "{format_exc()}"'
        log(error_text, 'error')
        error_message = error_text
        total_result[1] = error_message
    return total_result
