import json
import pandas as pd


color_ip = "#507EA4"          # Немного приглушенный синий
color_net_gr = "#EB7852"      # Теплый оранжевый
color_geo = "#7FB99D"         # Приятный зеленый
color_fqdn = "#DF8743"        # Более теплый оранжевый
color_net_range = "#ED7AA1"   # Мягкий розовый
color_tcp = "#42516F"         # Глубокий синий
color_udp = "#FF6347"         # Классический красный
color_service_gr = "#48BFAD"  # Ярко-голубовато-зеленый



legend_html = f"""
<div style="margin-top: 12px; font-weight: bold; text-align: center;">
    <table border="1" cellspacing="0" cellpadding="5" style="font-size: 18px; border-collapse: collapse; width: auto; table-layout: fixed; margin: 0 auto;">
        <tr>
            <th>Название</th>
            <th>Цвет</th>
        </tr>
        <tr>
            <td>network Ip Address</td>
            <td style="background-color: {color_ip}; color: white;"></td>
        </tr>
        <tr>
            <td>network Group</td>
            <td style="background-color: {color_net_gr}; color: white;"></td>
        </tr>
        <tr>
            <td>network Geo Address</td>
            <td style="background-color: {color_geo}; color: white;"></td>
        </tr>
        <tr>
            <td>network Fqdn</td>
            <td style="background-color: {color_fqdn}; color: white;"></td>
        </tr>
        <tr>
            <td>network Range</td>
            <td style="background-color: {color_net_range}; color: white;"></td>
        </tr>
        <tr>
            <td>service TCP</td>
            <td style="background-color: {color_tcp}; color: white;"></td>
        </tr>
        <tr>
            <td>service UDP</td>
            <td style="background-color: {color_udp}; color: white;"></td>
        </tr>
        <tr>
            <td>service Group</td>
            <td style="background-color: {color_service_gr}; color: white;"></td>
        </tr>
    </table>
</div>

"""

css_style = """
<style type="text/css">

.container {
    width: 80%;
    margin: auto;
    text-align: center;
}
th {
        text-align: center; /* Центрируем текст */
    }
.dataframe tbody td {
    white-space: nowrap; /* Запрет переноса строк */
}

.dataframe {
    margin: auto;
    border-collapse: separate;
}
.dataframe thead th {
    background-color: #f2f2f2; /* Цвет фона заголовков */
    color: #333; /* Цвет текста заголовков */
}
.dataframe tbody tr:nth-child(even) {
    background-color: #f9f9f9; /* Цвет фона четных строк */
}
.dataframe tbody tr:hover {
    background-color: #f1f1f1; /* Цвет фона при наведении */
}
.dataframe th,
.dataframe td {
    padding: 5px;
    text-align: left;
}

/* Перенос текста и ограничение ширины для 4 столбца */
.dataframe td:nth-child(4),
.dataframe th:nth-child(4) {
    max-width: 150px;
    word-wrap: break-word;
    white-space: normal;
}
.dataframe td:nth-child(15),
.dataframe th:nth-child(15) {
    max-width: 200px;
    word-wrap: break-word;
    white-space: normal;
}

</style>
"""

# Функция для извлечения имени или IP-адреса
def extract_name_or_ip(objects, color):
    ip_list = []
      
    if color:
        for obj in objects:
            if "networkIpAddress" in obj:
                ip_list.append(f'<span style="color: {color_ip}">{obj["networkIpAddress"].get("inet", "")}</span>')
            elif "networkGroup" in obj:
                ip_list.append(f'<span style="color: {color_net_gr}">{obj["networkGroup"].get("name", "")}</span>')
            elif "networkGeoAddress" in obj:
                ip_list.append(f'<span style="color: {color_geo}">{obj["networkGeoAddress"].get("name", "")}</span>')
            elif "networkFqdn" in obj:
                ip_list.append(f'<span style="color: {color_fqdn}">{obj["networkFqdn"].get("fqdn", "")}</span>')
            elif "networkIpRange" in obj:
                ip_list.append(f'<span style="color: {color_net_range}">{obj["networkIpRange"].get("name", "")}</span>')
            else:
                ip_list.append("Error")
    else:
        for obj in objects:
            if "networkIpAddress" in obj:
                ip_list.append(obj["networkIpAddress"].get("inet", ""))
            elif "networkGroup" in obj:
                ip_list.append(obj["networkGroup"].get("name", ""))
            elif "networkGeoAddress" in obj:
                ip_list.append(obj["networkGeoAddress"].get("name", ""))
            elif "networkFqdn" in obj:
                ip_list.append(obj["networkFqdn"].get("fqdn", ""))
            elif "ipV4Range" in obj:
                ip_list.append(obj["ipV4Range"].get("name", ""))
            else:
                ip_list.append("Error")

    return "<br> ".join(ip_list)

def extract_name(objects, key):
    zones = [] 
    for obj in objects:
        value = obj.get(key, "")
        zones.append(value)
    return "<br> ".join(zones)

def extract_name_or_port(objects, color):
    ports = []
    if color:
        for obj in objects["objects"]:
            if 'service' in obj:
                if obj['service']['protocol'] == 'SERVICE_PROTOCOL_TCP':
                    ports.append(f'<span style="color: {color_tcp}">{obj["service"].get("name", "")}</span>')
                elif obj['service']['protocol'] == 'SERVICE_PROTOCOL_UDP':
                    ports.append(f'<span style="color: {color_udp}">{obj["service"].get("name", "")}</span>')
                elif obj['service']['protocol'] == 'SERVICE_PROTOCOL_ICMP':
                    ports.append(obj["service"].get("name", ""))
            elif 'serviceGroup' in obj:
                ports.append(f'<span style="color: {color_service_gr}">{obj["serviceGroup"].get("name", "")}</span>')
            else:
                ports.append("Error")
    else:
        for obj in objects["objects"]:
            if 'service' in obj:
                if obj['service']['protocol'] == 'SERVICE_PROTOCOL_TCP':
                    ports.append(obj["service"].get("name", ""))
                elif obj['service']['protocol'] == 'SERVICE_PROTOCOL_UDP':
                    ports.append(obj["service"].get("name", ""))
                elif obj['service']['protocol'] == 'SERVICE_PROTOCOL_ICMP':
                    ports.append(obj["service"].get("name", ""))
            elif 'serviceGroup' in obj:
                ports.append(obj["serviceGroup"].get("name", ""))
            else:
                ports.append("Error")

    return "<br> ".join(ports)

def main(folder_path_json: str, folder_path_html: str, color: bool):
    
    with open(f"{folder_path_json}env.json") as file:
        data_env = json.load(file)
        mgmt_ip = data_env.get("mgmt_ip")
        groupe_name = data_env.get("groupe_name")
        precedence = data_env.get("precedence")

    html_h = f'''
    <div class="container">
        <h3>Security Rules</h3>
        <p>IP адрес системы управления: <strong>{mgmt_ip}</strong></p>
        <p>Имя группы: <strong>{groupe_name}</strong></p>
        <p>Приоритет: <strong>{precedence}</strong></p>
    </div>
    '''



    with open(f"{folder_path_json}rules.json") as file:
        data = json.load(file)

    items = data["items"]
    records = []

    for item in items:
        record = {}
        # Имя правила
        record["Enabled"] = item.get("enabled", "")
        record["Name"] = item.get("name", "")
        # Описание правила
        record["Description"] = item.get("description", "")
        
        # Источник зоны
        source_zone_objects = item.get("sourceZone", {}).get("objects", [])
        record["Source Zone"] = extract_name(source_zone_objects, "name")
    
        # Источник IP
        source_addr_objects = item.get("sourceAddr", {}).get("objects", [])
        record["Source IP"] = extract_name_or_ip(source_addr_objects, color)

        # Зона назначения
        dst_zone_objects = item.get("destinationZone", {}).get("objects", [])
        record["Destination Zone"] = extract_name(dst_zone_objects, "name")

        # IP-адрес назначения
        dst_addr_objects = item.get("destinationAddr", {}).get("objects", [])
        record["Destination IP"] = extract_name_or_ip(dst_addr_objects, color)

        # Сервисы (Порты)
        services = item.get("service", [])
        record["Service"] = extract_name_or_port(services, color)

        # Приложения
        app = item.get("application", {}).get("objects", [])
        record["Application"] = extract_name(app, "name")
        
        # URL
        url_category = item.get("urlCategory", {}).get("objects", [])
        record["URL Category"] = extract_name(url_category, "name")

        # IPS
        record["IPS"] = item.get("ipsProfile", {}).get("name", [])

        # AV
        record["Antivirus"] = item.get("avProfile", {}).get("name", [])
        
        record["action"] = item.get("action","").replace("SECURITY_RULE_ACTION_", "")

        record["Log Mode"] = item.get("logMode").replace("SECURITY_RULE_LOG_MODE_", "")

        record["Schedule"] = item.get("schedule")

        records.append(record)

    df = pd.DataFrame(records)

    if color:
        html = css_style + html_h + df.to_html(classes='dataframe', escape=False) + legend_html + '</div>'
    else:
        html = css_style + html_h + df.to_html(classes='dataframe', escape=False) + '</div>'

    name = "rules.html"
    if color: name = "rules_color.html" 

    with open(f"{folder_path_html}{groupe_name}_{name}", 'w', encoding='utf-8') as f:
        f.write(html)


# Путь к папкам
folder_path_json = "H:/WORK/PT/scripts/pt-Rule-to-HTML/json/"
folder_path_html = "H:/WORK/PT/scripts/pt-Rule-to-HTML/html/"

#  Соlor = True выделить разным цветами типы объектов и группы 
main(folder_path_json, folder_path_html, color=True)
