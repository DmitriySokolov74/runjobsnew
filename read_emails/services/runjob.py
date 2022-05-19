from django.conf import settings
import requests
import json
from traceback import format_exc
from robots.models import Robots

#
# # info from mail:
# process_name = 'Second'


def get_token(url, body, timeout):
    '''
    :param url: URL запроса для получения токена
    :param body: словарь с параметрами оркестратора
    :param timeout: таймаут запроса (сек)
    :return: список [токен, результат: True-> успех, False -> неудача]
    '''
    result = ["", False] # изначально инициализируем возвращаемое значение неудачей
    try:
        response = requests.post(url, json=body, timeout=timeout)
        # запрос выполнен успешно?
        if response.status_code == 200:
            token = response.json()['access_token']
            result = [token, True] # инициализируем возвращаемое значение успехом
    except:
        print("Ошибка при получении токена")
    return result



#response = requests.post('https://account.uipath.com/oauth/token', json=json_dict, timeout=30)
#r_json = response.json()
#t = r_json['access_token']
#print(response.status_code)
#print(t)

# Getting folders id:
def get_folder_id(url, folder_name, tenant_name, token):
    '''
    :param url: url для get запроса
    :param folder_name: имя папки (см. в оркестраторе)
    :param tenant_name: имя тенанта (см. в оркестраторе)
    :param token: токен, полученный ранее
    :return: список [id папки, bool]
    '''
    result = ["", False]  # изначально инициализируем возвращаемое значение неудачей
    try:
        # добавляем фильтр в URL, чтобы в ответе остались только результаты для нашей папки folder_name
        url_filter = url + f"?$Filter=FullyQualifiedName eq '{folder_name}'"
        response = requests.get(
        url_filter,
        headers={'X-UIPATH-TenantName': tenant_name, 'Authorization': f'Bearer {token}'},
        )
        if response.status_code == 200:
            folder_id = response.json()["value"][0].get("Id")
            result = [folder_id, True]
            print(f"folder_id={folder_id}, type={str(type(folder_id))}")
    except:
        print("Не удалось извлечь id папки")
    return result



#print("Getting folders key and id")
#URL_filter = "https://cloud.uipath.com/neawucsnn/FalconTenant/orchestrator_/odata/Folders?$Filter=FullyQualifiedName eq 'FalconFolder'"
#URL = 'https://cloud.uipath.com/neawucsnn/FalconTenant/orchestrator_/odata/Folders'
#response = requests.get(
#    URL_filter,
#    headers={'X-UIPATH-TenantName': 'FalconTenant', 'Authorization': f'Bearer {t}'},
#)
#print("new=", response.status_code)
#folder_id = response.json()["value"][0].get("Id")
#print(folder_id)

# Getting robots Releases:
def get_process_key(url, process_name, tenant_name, token):
    '''
    :param url: url для get запроса
    :param process_name: имя процесса, которое указывается в теме письма
    :param tenant_name: имя тенанта (см. оркестратор)
    :param token: токен, полученный ранее
    :return: возвращает ключ процесса, необходимый для финального post запроса
    '''
    result = ["", False]  # изначально инициализируем возвращаемое значение неудачей
    # фильтруем запрос для получения только тех значений, которые относятся к нашему процессу [process_name]
    url_filter = url + f"?$Filter=ProcessKey eq '{process_name}'"
    try:
        response = requests.get(
            url_filter,
            headers={'X-UIPATH-TenantName': tenant_name, 'Authorization': f'Bearer {token}'},
        )
        if response.status_code == 200:
            process_key = response.json()["value"][0].get("Key")
            result = [process_key, True]
            print(f"process_key={process_key}, type={str(type(process_key))}")
    except:
        print("Не удалось получить ключ процесса")
    return result

#print("Get robots Releases")
#process_name = "Second"
#URL = "https://cloud.uipath.com/neawucsnn/FalconTenant/orchestrator_/odata/Releases"
#URL_filter = f"https://cloud.uipath.com/neawucsnn/FalconTenant/orchestrator_/odata/Releases?$Filter=ProcessKey eq '{process_name}'"
#response = requests.get(
#    URL_filter,
#    headers={'X-UIPATH-TenantName': 'FalconTenant', 'Authorization': f'Bearer {t}'},
#)
#print("new=", response.status_code)
#process_key = response.json()["value"][0].get("Key")
#print(process_key)
#print("!!!")
#print(response.json())

# Get RobotsIds
def get_robot_id(url, folder_id, tenant_name, token, user_name):
    result = ["", False]  # изначально инициализируем возвращаемое значение неудачей
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
            print(f"robot_id={robot_id}, type={str(type(robot_id))}")
    except:
        print("Не удалось получить id робота")
    return result


#user = "raskalovdima@yandex.ru" # username
#URL_filter = f"https://cloud.uipath.com/neawucsnn/FalconTenant/orchestrator_/odata/Users?$Filter=UserName eq '{user}'"
#headers = {
#    "X-UIPATH-OrganizationUnitId": str(folder_id),
#    "X-UIPATH-TenantName": "FalconTenant",
#    "Authorization": f'Bearer {t}',
#    "Content-Type": "application/json"
#}
#response = requests.get(
#    URL_filter,
#    headers=headers
#)
#robot_id = response.json().get("value")[0].get("UnattendedRobot").get("RobotId")
#print(robot_id)


# Start Job

def start_job(url, process_key, robot_id, folder_id, token, tenant_name, timeout):
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
    print(f'url = {str(url)},\nprocess_key = {str(process_key)},\nrobot_id = {str(robot_id)},\ntoken = {str(token)},\ntenant_name = {str(tenant_name)},\nfolder_id = {str(folder_id)}')
    result = False
    try:
        response = requests.post(url, data=json.dumps(body), headers=headers, timeout=timeout)
        if response.status_code == 201:
            result = True
            print('Job запущен УСПЕШНО!')
        else:
            print(f'Job не запущен: статус = {str(response.status_code)}')
            print(f'Job не запущен: message = {str(response.json().get("message"))}')
            raise
    except:
        mes = "Не удалось запустить процесс: "
        try:
            error_message = str(response.json().get("message"))
            mes = mes + error_message
        except:
            mes = mes + "не удалось получить сообщение ошибки"
    return result

#URL = "https://cloud.uipath.com/neawucsnn/FalconTenant/orchestrator_/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
#json_dict = {
#  "startInfo": {
#    "ReleaseKey": process_key,
#    "Strategy": "Specific",
#     "JobsCount": 0,
#     "RobotIds": [robot_id],
#     "JobPriority": "Normal",
#   }
# }
# json_str = json.dumps(json_dict)
# headers = {
#     "X-UIPATH-OrganizationUnitId": str(folder_id),
#     "X-UIPATH-TenantName": "FalconTenant",
#     "Authorization": f'Bearer {t}',
#     "Content-Type": "application/json"
# }
# response = requests.post(URL, data=json.dumps(json_dict), headers=headers, timeout=30)
# r_json = response.json()
# print(response.status_code)
# print(str(response.json().get("message")))
def run(process_name=None,
        model=None,
        token_timeout=30):
    try:
        client = model.objects.get(name=process_name).client
        user_name = client.user
        print(f'CHECK!!! user_name = {str(user_name)}')
        client_id = client.client_id
        print(f'CHECK!!! client_id = {str(client_id)}')
        user_key = client.user_key
        print(f'CHECK!!! user_key = {str(user_key)}')
        body_token = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": user_key
        }
        org_id = client.org
        print(f'CHECK!!! org_id = {str(org_id)}')
        folder_name = client.folder
        print(f'CHECK!!! folder_name = {str(folder_name)}')
        tenant_name = client.tenant
        print(f'CHECK!!! tenant_name = {str(tenant_name)}')
        url_folder_id = settings.ORC_URL_FOLDER_ID.format(org_id, tenant_name)
        print(f'CHECK!!! url_folder_id = {str(url_folder_id)}')
        url_process_key = settings.ORC_URL_PROCESS_KEY.format(org_id, tenant_name)
        print(f'CHECK!!! url_process_key = {str(url_process_key)}')
        url_start_job = settings.ORC_URL_START_JOB.format(org_id, tenant_name)
        print(f'CHECK!!! url_start_job = {str(url_start_job)}')
        url_token = settings.ORC_URL_TOKEN
        print(f'CHECK!!! url_token = {str(url_token)}')
        url_robot_id = settings.ORC_URL_ROBOT_ID.format(org_id, tenant_name)
        print(f'CHECK!!! url_robot_id = {str(url_robot_id)}')
        result = False
        # 0 - получение записи модели
        all_robots = model.objects.all()
        # getting model instance
        if process_name in [x.name for x in all_robots]:
            r = Robots.objects.get(name=process_name)
        else:
            raise Exception(f"Процесс {process_name} не существует в БД")
        # 1 - получение токена
        token_result = get_token(url=url_token,
                                 body=body_token,
                                 timeout=30)
        if token_result[1] == False:
            raise ValueError("Токен не получен")
        token = token_result[0]
        # 2 - получение id папки
        if r.folder_id is None:
            folder_id_result = get_folder_id(url=url_folder_id,
                                             folder_name=folder_name,
                                             tenant_name=tenant_name,
                                             token=token)
            if folder_id_result[1] == False:
                raise ValueError("id папки не получено")
            folder_id = folder_id_result[0]
            r.folder_id = folder_id
        # 3 - получение ключа процесса
        if r.process_key is None:
            process_key_result = get_process_key(url=url_process_key,
                                                 process_name=process_name,
                                                 tenant_name=tenant_name,
                                                 token=token)
            if process_key_result[1] == False:
                raise ValueError("ключ процесса не получен")
            process_key = process_key_result[0]
            r.process_key = process_key
        # 4 - получение id робота
        if r.robot_id is None:
            robot_id_result = get_robot_id(url=url_robot_id,
                                           folder_id=r.folder_id,
                                           tenant_name=tenant_name,
                                           token=token,
                                           user_name=user_name)
            if robot_id_result[1] == False:
                raise ValueError("id робота не получено")
            robot_id = robot_id_result[0]
            r.robot_id = robot_id
        # 5 - start job
        start_job_result = start_job(url=url_start_job,
                                     process_key=r.process_key,
                                     robot_id=r.robot_id,
                                     folder_id=r.folder_id,
                                     token=token,
                                     tenant_name=tenant_name,
                                     timeout=30)
        if start_job_result == False:
            raise ValueError("job не запущен")
        else:
            result = start_job_result
        # 6 - сохранение изменений записи БД для имени процесса
        r.save()
        return start_job_result
    except:
        print(f"Не удалось запустить процесс: {str(format_exc())}")
    return result

# run(
#     process_name=process_name,
#     user_name=user_name,
#     url_token=url_token,
#     body_token=body_token,
#     url_folder_id=url_folder_id,
#     url_process_key=url_process_key,
#     url_start_job=url_start_job,
#     folder_name=folder_name,
#     tenant_name=tenant_name,
#     token_timeout=30)
