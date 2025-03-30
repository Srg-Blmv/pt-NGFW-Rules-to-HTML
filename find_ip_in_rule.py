import json
import os
import pandas as pd



css_style = """
<style type="text/css">
body {
    display: flex;
    justify-content: center;
    margin: 20px;
}

.container {
    width: 80%;
    margin: auto;
    text-align: center;
}

.dataframe {
    margin: auto;
    border-spacing: 0 15px;
    border-collapse: separate;
}

.dataframe th,
.dataframe td {
    padding: 10px;
    text-align: center;
}

.dataframe th {
    background-color: #f2f2f2;
    color: #333;
}



.dataframe td table {
    font-size: 15px;
    word-break: break-word;
    border: 1px solid #ddd;
}

.dataframe td table th,
.dataframe td table td {
    padding: 6px;
    vertical-align: middle;
    max-width: 200px;
    overflow-wrap: anywhere;
}

.dataframe td table th {
    background-color: #f7f7f7;
}

.dataframe td table td strong {
    display: inline-block;
}


</style>
"""



def extract_names(objects):
    result = []
    if isinstance(objects, dict):
        for key, value in objects.items():
            if key == "name":
                result.append(value)
            else:
                result.extend(extract_names(value))
    elif isinstance(objects, list):
        for item in objects:
            result.extend(extract_names(item))
    return result


def check_ip_match(ip_obj, ip_name):
    if "networkIpAddress" in ip_obj:
        if ip_name == ip_obj["networkIpAddress"].get("name", ""):
            return True
    elif "networkGroup" in ip_obj:
        if ip_name == ip_obj["networkGroup"].get("name", ""):
            return True
    elif "networkFqdn" in ip_obj:
        if ip_name == ip_obj["networkFqdn"].get("name", ""):
            return True
    elif "networkIpRange" in ip_obj:
        if ip_name == ip_obj["networkIpRange"].get("name", ""):
            return True
    return False


def extract_name_rules(ip_name, objects):
    src_name_rows = []
    dst_name_rows = []
    
    for obj in objects.get('items', []):
        src_ips = obj.get("sourceAddr", {}).get("objects", [])
        dst_ips = obj.get("destinationAddr", {}).get("objects", [])
        
        for src_ip in src_ips:
            if check_ip_match(src_ip, ip_name):
                src_name_rows.append(obj.get('name', ''))

        for dst_ip in dst_ips:
            if check_ip_match(dst_ip, ip_name):
                dst_name_rows.append(obj.get('name', ''))

 # Генерация строк таблицы без предварительного выравнивания
    max_rows = max(len(src_name_rows), len(dst_name_rows))
    src_name_rows.extend([''] * (max_rows - len(src_name_rows)))
    dst_name_rows.extend([''] * (max_rows - len(dst_name_rows)))
    
    rows_html = ""
    for src, dst in zip(src_name_rows, dst_name_rows):
        rows_html += f"<tr><td>{src}</td><td>{dst}</td></tr>"

    # Итоговая HTML таблица
    html = f"""
    <table style="width:100%; border-collapse: collapse;" border="1">
        <thead>
            <tr>
                <th style="text-align:center;">Source</th>
                <th style="text-align:center;">Destination</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    return html.replace("\n", '')

def extract_name_nat(ip_name, objects):
    src_name_nat = []
    dst_name_nat = []
    src_trc_name_nat = []
    dst_trc_name_nat = []

    # Сбор данных
    for obj in objects.get('items', []):
        src_trns_ips = obj.get("srcTranslatedAddress", {}).get("objects", [])
        dst_trns_ips = obj.get("dstTranslatedAddress", {}).get("objects", [])
        src_ips = obj.get("sourceAddr", {}).get("objects", [])
        dst_ips = obj.get("destinationAddr", {}).get("objects", [])

        for src_ip in src_ips:
            if check_ip_match(src_ip, ip_name):
                src_name_nat.append(obj.get("name", ""))

        for dst_ip in dst_ips:
            if check_ip_match(dst_ip, ip_name):
                dst_name_nat.append(obj.get("name", ""))
        
        for src_trns_ip in src_trns_ips:
            if check_ip_match(src_trns_ip, ip_name):
                src_trc_name_nat.append(obj.get("name", ""))
        
        for dst_trns_ip in dst_trns_ips:
            if check_ip_match(dst_trns_ip, ip_name):
                dst_trc_name_nat.append(obj.get("name", ""))

    # Выравнивание списков по длине
    max_rows = max(len(src_name_nat), len(dst_name_nat), len(src_trc_name_nat), len(dst_trc_name_nat))
    src_name_nat.extend([''] * (max_rows - len(src_name_nat)))
    dst_name_nat.extend([''] * (max_rows - len(dst_name_nat)))
    src_trc_name_nat.extend([''] * (max_rows - len(src_trc_name_nat)))
    dst_trc_name_nat.extend([''] * (max_rows - len(dst_trc_name_nat)))
    
    # Генерация строк таблицы с корректной структурой
    rows_html = ""
    for src, dst, src_trc, dst_trc in zip(src_name_nat, dst_name_nat, src_trc_name_nat, dst_trc_name_nat):
        rows_html += f"<tr><td>{src}</td><td>{dst}</td><td>{src_trc}</td><td>{dst_trc}</td></tr>"

    # Итоговая HTML таблица
    html = f"""
    <table style="width:100%; border-collapse: collapse;" border="1">
        <thead>
            <tr>
                <th style="text-align:center;">Source</th>
                <th style="text-align:center;">Destination</th>
                <th style="text-align:center;">Source Trans</th>
                <th style="text-align:center;">Dst Trans</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    return html.replace("\n", '')


def extract_name_group_ip(ip_name, objects):
    group_names = []

    # Проходим по всем группам
    for items in objects:
        for i in items["group"].get("items", {}):
                if check_ip_match(i, ip_name):
                    group_names.append(items["group"].get("name", ""))

    # Генерация строк таблицы
    rows_html = ""
    for group_name in group_names:
        rows_html += f"<tr><td>{group_name}</td></tr>"

    # Итоговая HTML таблица
    html = f"""
    <table style="width:100%; border-collapse: collapse;" border="1">
        <thead>
            <tr>
                <th style="text-align:center;">Group Name</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    return html.replace("\n", '')


def main(folder_path_json, folder_path_html):


    with open(f"{folder_path_json}env.json") as file:
        data_env = json.load(file)
        mgmt_ip = data_env.get("mgmt_ip")
        groupe_name = data_env.get("groupe_name")
        precedence = data_env.get("precedence")

    html_h = f'''
    <div class="container">
        <h3>Where IP </h3>
        <p>IP адрес системы управления: <strong>{mgmt_ip}</strong></p>
        <p>Имя группы: <strong>{groupe_name}</strong></p>
        <p>Приоритет: <strong>{precedence}</strong></p>
    '''

    
    with open(f"{folder_path_json}ip.json") as file:
        data_ip = json.load(file)

    with open(f"{folder_path_json}rules.json") as file:
        data_rules = json.load(file)


    with open(f"{folder_path_json}nat.json") as file:
        data_nat = json.load(file)


    with open(f"{folder_path_json}groups_ip.json") as file:
        data_groups_ip = json.load(file)


    # Извлекаем все имена
    all_names_ip_obj = extract_names(data_ip)
    records = []

    # Выводим все имена
    for name in all_names_ip_obj:
        record = {}

        record["name Address"] = f'{name}'
        record["name security rules"] = extract_name_rules(name,data_rules)
        record["name nat rules"] = extract_name_nat(name,data_nat)
        record["name address group"] = extract_name_group_ip(name,data_groups_ip)

        records.append(record)


    df = pd.DataFrame(records)
    html = css_style +  html_h + df.to_html(classes='dataframe', escape=False, index=False) + '</div>'

    with open(f"{folder_path_html}{groupe_name}_where_IP.html", 'w', encoding='utf-8') as f:
        f.write(html)



# Путь к папкам
folder_path_json = "H:/WORK/json/"
folder_path_html = "H:/WORK/html/"

main(folder_path_json, folder_path_html)