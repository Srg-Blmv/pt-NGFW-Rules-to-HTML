import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


global_gr_id = ""
cookies = ""
headers = {"Content-Type": "application/json"}

def auth():
    global global_gr_id, cookies
    url = f"https://{mgmt_ip}/api/v2/Login"

    payload = {
        "login": mgmt_login,
        "password": mgmt_pass
    }
    

    response_auth = requests.post(url, json=payload, headers=headers, verify=False)
    if response_auth.status_code == 200:
        print("auth ok")
        payload={}
        url =  f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
        r = requests.post(url, headers=headers, json=payload, verify=False, cookies=response_auth.cookies)
        cookies = response_auth.cookies
        # ПОЛУЧАЕМ ID глобальной группы
        global_gr_id = get_id_groupe(r.json()['groups'][0])
        # Пример 1 группы в глобальной:
        #global_gr_id = (r.json()['groups'][0].get("subgroups")[0].get('id'))
        # Или заберите нужное ID через web api интерфейс: https://IP_MGMT/apidoc/v2/ui/#tag/device-groups/POST/api/v2/GetDeviceGroupsTree
        # сохраним имя группы для 
        
    else:
        print("auth fail")
        exit()



def save_env():
    data = {
    "mgmt_ip": mgmt_ip,
    "groupe_name": groupe_name,
    "precedence": precedence
    }
    # Записываем данные в файл JSON
    with open(f'{path_save_json}env.json', "w") as file:
        json.dump(data, file)


def get_id_groupe(groups):
    # Проверка текущей группы
    if groups.get("name") == groupe_name:
        return groups.get("id")
    # Проверка вложенных групп, если они существуют
    if "subgroups" in groups:
        for subgroup in groups["subgroups"]:  # Проходим по списку подгрупп
            result = get_id_groupe(subgroup)
            if result:  # Если id найдено, возвращаем его
                return result
    return None  # Возвращаем None, если ничего не найдено

def get_rules():
    url_list_url  = f"https://{mgmt_ip}/api/v2/ListSecurityRules"
    
    payload_list_url = {
            "limit": 10000,
            "deviceGroupId": f"{global_gr_id}",
            "precedence": precedence
        }  
    response_ser = requests.post(url_list_url, json=payload_list_url, headers=headers, verify=False, cookies=cookies)
    
    if response_ser.status_code == 200:
        data = response_ser.json()
        with open(f'{path_save_json}rules.json', 'w') as file:
            json.dump(data, file)

# Функция для получения групп IP 
def get_gr_ip():
    url_list_url  = f"https://{mgmt_ip}/api/v2/ListNetworkObjectGroups"
    url_obj_gr  = f"https://{mgmt_ip}/api/v2/GetNetworkObjectGroup"
    
    payload_list_url = {
            "limit": 10000,
            "deviceGroupId": f"{global_gr_id}",
        }
    response_ser = requests.post(url_list_url, json=payload_list_url, headers=headers, verify=False, cookies=cookies)
    
    if response_ser.status_code == 200:
        id_groups = []
        data = response_ser.json()
        for id in data["groups"]:
            id_groups.append(id.get('id', ''))


    if len(id_groups) > 0:
        with open(f'{path_save_json}groups_ip.json', 'w') as file:
            file.write('[')  # Начальная скобка массива
            first_iteration = True  # Флаг для первой итерации

            for id in id_groups:
                payload_obj_gr = {"id": id}
                response_obj = requests.post(url_obj_gr, json=payload_obj_gr, headers=headers, verify=False, cookies=cookies)
                
                if response_obj.status_code == 200:
                    data = response_obj.json()
                    
                    # Добавляем запятую после каждого объекта, кроме первого
                    if not first_iteration:
                        file.write(',')
                    else:
                        first_iteration = False
                    
                    json.dump(data, file)  # Запись данных в файл

            file.write(']')  # Закрывающая скобка массива



# Функция для получения групп port 
def get_gr_service():
    url_list_url  = f"https://{mgmt_ip}/api/v2/ListServiceGroups"
    url_obj_gr  = f"https://{mgmt_ip}/api/v2/GetServiceGroup"
    
    payload_list_url = {
            "limit": 10000,
            "deviceGroupId": f"{global_gr_id}",
        }
    response_ser = requests.post(url_list_url, json=payload_list_url, headers=headers, verify=False, cookies=cookies)
    
    if response_ser.status_code == 200:
        id_groups = []
        data = response_ser.json()
        for id in data["serviceGroups"]:
            id_groups.append(id.get('id', ''))


    if len(id_groups) > 0:
        with open(f'{path_save_json}groups_service.json', 'w') as file:
            file.write('[')  # Начальная скобка массива
            first_iteration = True  # Флаг для первой итерации

            for id in id_groups:
                payload_obj_gr = {"id": id}
                response_obj = requests.post(url_obj_gr, json=payload_obj_gr, headers=headers, verify=False, cookies=cookies)
                
                if response_obj.status_code == 200:
                    data = response_obj.json()
                    
                    # Добавляем запятую после каждого объекта, кроме первого
                    if not first_iteration:
                        file.write(',')
                    else:
                        first_iteration = False
                    
                    json.dump(data, file)  # Запись данных в файл

            file.write(']')  # Закрывающая скобка массива

def get_nat():
    url_list_url  = f"https://{mgmt_ip}/api/v2/ListNatRules"
    
    payload_list_url = {
            "limit": 10000,
            "deviceGroupId": f"{global_gr_id}",
            "precedence": "pre"
        }  
    response_ser = requests.post(url_list_url, json=payload_list_url, headers=headers, verify=False, cookies=cookies)
    
    if response_ser.status_code == 200:
        data = response_ser.json()
        with open(f'{path_save_json}nat.json', 'w') as file:
            json.dump(data, file)



def get_ip():
    url_list_url  = f"https://{mgmt_ip}/api/v2/ListNetworkObjects"
    

    payload_list_url = {
            "limit": 10000,
            "deviceGroupId": f"{global_gr_id}",
            "precedence": "pre",
            "objectKinds":["OBJECT_NETWORK_KIND_IPV4_ADDRESS","OBJECT_NETWORK_KIND_IPV4_RANGE","OBJECT_NETWORK_KIND_FQDN"]
        }  
    response_ser = requests.post(url_list_url, json=payload_list_url, headers=headers, verify=False, cookies=cookies)
    
    if response_ser.status_code == 200:
        data = response_ser.json()
        with open(f'{path_save_json}ip.json', 'w') as file:
            json.dump(data, file)


mgmt_ip = "192.168.1.100"       # IP MGMT
mgmt_login =  "admin"           # LOGIN 
mgmt_pass = "xxXX1234$"         # Password
groupe_name = "Global"          # Имя группы
precedence = "pre"              # Pre or Post


####   Это  путь до папки  в конце нужен слеш  /
path_save_json = "H:/WORK/json/" 

auth()
save_env()
get_rules()                # json c rules
get_gr_ip()                # json c группами IP
get_gr_service()           # json c группами сервисов      
get_nat()                  # json c NAT
get_ip()                   # json только с IP без Групп

