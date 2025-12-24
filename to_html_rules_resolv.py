import json
import pandas as pd

# Определение цветовой палитры (менее яркие цвета)
color_ip = "#6B9AC4"
color_net_gr = "#F4A261"
color_geo = "#A3C9A8"
color_fqdn = "#E8A969"
color_net_range = "#F4A8C2"
color_service_gr = "#6ACCB9"

css_style = """
<style type="text/css">
body {
    background: #f8f9fa;
    font-family: 'Roboto', 'Arial', sans-serif;
    color: #333;
    font-size: 15px;
    line-height: 1.6;
    margin: 20px;
}
.container {
    max-width: 1400px;
    margin: 0 auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
h3 {
    color: #42516F;
    font-size: 24px;
    margin-bottom: 20px;
    border-bottom: 2px solid #42516F;
    padding-bottom: 8px;
}
p {
    margin: 8px 0;
}
.dataframe {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    background: #fff;
}
.dataframe th, .dataframe td {
    border: 2px solid #d1d5db;
    padding: 10px;
    text-align: left;
    vertical-align: top;
}
.dataframe th {
    background: #42516F;
    color: white;
    font-weight: 600;
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 100;
}
.dataframe tr:nth-child(even) {
    background-color: #f9fafb;
}
.dataframe tr:hover {
    background-color: #f0f4f8;
}
.dataframe td {
    font-size: 16px;
}
table.nested {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0;
}
table.nested th {
    background: #9ca3af;
    color: white;
    font-weight: 500;
    font-size: 13px;
    padding: 6px;
    text-align: center;
    z-index: 10;
}
table.nested td {
    border: 2px solid #d1d5db;
    padding: 8px;
    font-size: 15px;
    text-align: center; 
}
.header-info {
    background: #f1f5f9;
    padding: 15px;
    border-radius: 6px;
    margin-bottom: 20px;
}
</style>
"""




iana_protocols = {
    0: "HOPOPT",
    1: "ICMP",
    2: "IGMP",
    6: "TCP",
    17: "UDP",
    41: "IPv6",
    47: "GRE",
    50: "ESP",
    51: "AH",
    58: "IPv6-ICMP",
    89: "OSPFIGP",
    103: "PIM",
    112: "VRRP",
    115: "L2TP",
    124: "ISIS",
    132: "SCTP",
    136: "UDPLite",
    137: "MPLS-in-IP",
    139: "HIP",
    255: "Reserved",
}



def get_all_group_items(groups_data, group_id, visited=None):
    if visited is None:
        visited = set()
    if group_id in visited:
        return []
    visited.add(group_id)

    for group in groups_data:
        if group.get("id") == group_id:
            result = []
            items = group.get("items", [])
            for item in items:
                if "networkGroup" in item:
                    nested_id = item["networkGroup"].get("id")
                    result.extend(get_all_group_items(groups_data, nested_id, visited))
                else:
                    result.append(item)
            return result
    return []

def format_ip_group(group_id, group_name, groups_data, visited=None):
    if visited is None:
        visited = set()
    if group_id in visited:
        return ""
    visited.add(group_id)

    group = next((g for g in groups_data if g.get("id") == group_id), None)
    if not group:
        return ""

    html = f'<table class="nested" style="margin-bottom:10px;">'
    html += f'<tr><th colspan="3" style="background-color:{color_net_gr};">{group_name}</th></tr>'
    html += '<tr><th>Тип</th><th>Значение</th><th>Имя</th></tr>'

    for item in group.get("items", []):
        if "networkIpAddress" in item:
            ip = item["networkIpAddress"].get("inet", "")
            name = item["networkIpAddress"].get("name", "-")
            html += f'<tr><td><span style="color:#888;">IP</span></td><td>{ip}</td><td><span style="color:#888;">{name}</span></td></tr>'
        elif "networkGeoAddress" in item:
            geo_name = item["networkGeoAddress"].get("name", "")
            html += f'<tr><td><span style="color:#888;">Geo</span></td><td>{geo_name}</td><td>-</td></tr>'
        elif "networkFqdn" in item:
            fqdn = item["networkFqdn"].get("fqdn", "")
            html += f'<tr><td><span style="color:#888;">FQDN</span></td><td>{fqdn}</td><td>-</td></tr>'
        elif "networkIpRange" in item:
            from_range = item["networkIpRange"].get("from", "")
            to_range = item["networkIpRange"].get("to", "")
            name = item["networkIpRange"].get("name", "")
            html += f'<tr><td><span style="color:#888;">Range</span></td><td>{from_range} - {to_range}</td><td><span style="color:#888;">{name}</span></td></tr>'
        elif "networkGroup" in item:
            nested_id = item["networkGroup"].get("id")
            nested_name = item["networkGroup"].get("name")
            html += f'<tr><td colspan="3">{format_ip_group(nested_id, nested_name, groups_data, visited)}</td></tr>'
        else:
            html += f'<tr><td>?</td><td>Error</td><td>-</td></tr>'
    html += '</table>'
    return html

def format_service_group(group_id, group_name, groups_data, visited=None):
    if visited is None:
        visited = set()
    if group_id in visited:
        return ""
    visited.add(group_id)

    group = next((g for g in groups_data if g.get("id") == group_id), None)
    if not group:
        return ""

    html = f'<table class="nested" style="margin-bottom:10px;">'
    html += f'<tr><th colspan="4" style="background-color:{color_service_gr};">{group_name}</th></tr>'
    html += '<tr><th>Src Port</th><th>Dst Port</th><th>Имя</th><th>Протокол</th></tr>'

    for item in group.get("items", []):
        if "service" in item:
            protocol = item["service"].get("protocol", "")
            name = item["service"].get("name", "")
            src_port = ""
            for i in item["service"].get("srcPorts", []):
                if 'singlePort' in i:
                    src_port += f"{i['singlePort']['port']}<br>"
                elif 'portRange' in i:
                    pr = i['portRange']
                    src_port += f"{pr.get('from', '')}-{pr.get('to', '')}<br>"
            dst_port = ""
            for i in item["service"].get("dstPorts", []):
                if 'singlePort' in i:
                    dst_port += f"{i['singlePort']['port']}<br>"
                elif 'portRange' in i:
                    pr = i['portRange']
                    dst_port += f"{pr.get('from', '')}-{pr.get('to', '')}<br>"
            protocol_str = iana_protocols[protocol]
            html += f'<tr><td>{src_port}</td><td>{dst_port}</td><td><span style="color:#888;">{name}</span></td><td><span style="color:#888;">{protocol_str}</span></td></tr>'
        elif "serviceGroup" in item:
            nested_id = item["serviceGroup"].get("id")
            nested_name = item["serviceGroup"].get("name")
            html += f'<tr><td colspan="4">{format_service_group(nested_id, nested_name, groups_data, visited)}</td></tr>'
        else:
            html += f'<tr><td>-</td><td>Error</td><td>-</td><td>-</td></tr>'
    html += '</table>'
    return html

def extract_name_or_ip(objects, data_group_ip):
    ip_list = []
    for obj in objects:
        if "networkIpAddress" in obj:
            ip = obj["networkIpAddress"].get("inet", "")
            name = obj["networkIpAddress"].get("name", "")
            ip_list.append(f'<span>{ip}</span> <span style="color:#888;">{name}</span>')
        elif "networkGroup" in obj:
            group_id = obj["networkGroup"].get("id")
            group_name = obj["networkGroup"].get("name")
            ip_list.append(format_ip_group(group_id, group_name, data_group_ip))
        elif "networkGeoAddress" in obj:
            name = obj["networkGeoAddress"].get("name", "")
            ip_list.append(f'<span style="color:{color_geo}">{name}</span>')
        elif "networkFqdn" in obj:
            fqdn = obj["networkFqdn"].get("fqdn", "")
            ip_list.append(f'<span">{fqdn}</span>')
        elif "networkIpRange" in obj:
            from_range = obj["networkIpRange"].get("from", "")
            to_range = obj["networkIpRange"].get("to", "")
            name = obj["networkIpRange"].get("name", "")
            ip_list.append(f'<span">{from_range} - {to_range}</span> <span style="color:#888;">{name}</span>')
        else:
            ip_list.append("Error")
    return "<br>".join(ip_list)

def extract_name(objects, key):
    zones = [obj.get(key, "") for obj in objects]
    return "<br>".join(zones)

def extract_name_or_port(objects, data_group_service):
    ports = []
    if isinstance(objects, dict) and "objects" in objects:
        objects = objects["objects"]

    for obj in objects:
        if "service" in obj:
            protocol = obj["service"].get("protocol", "")
            name = obj["service"].get("name", "")
            src_port = ""
            for i in obj["service"].get("srcPorts", []):
                if 'singlePort' in i:
                    src_port += f"{i['singlePort']['port']}<br>"
                elif 'portRange' in i:
                    pr = i['portRange']
                    src_port += f"{pr.get('from', '')}-{pr.get('to', '')}<br>"
            dst_port = ""
            for i in obj["service"].get("dstPorts", []):
                if 'singlePort' in i:
                    dst_port += f"{i['singlePort']['port']}<br>"
                elif 'portRange' in i:
                    pr = i['portRange']
                    dst_port += f"{pr.get('from', '')}-{pr.get('to', '')}<br>"
            protocol_str = iana_protocols[protocol]
            row = (
                f'<table class="nested"><tr><th>Src Port</th><th>Dst Port</th><th>Имя</th><th>Протокол</th></tr>'
                f'<tr><td>{src_port}</td><td>{dst_port}</td><td><span style="color:#888;">{name}</span></td><td><span style="color:#888;">{protocol_str}</span></td></tr></table>'
            )
            ports.append(row)
        elif "serviceGroup" in obj:
            group_id = obj["serviceGroup"].get("id")
            group_name = obj["serviceGroup"].get("name")
            ports.append(format_service_group(group_id, group_name, data_group_service))
        else:
            ports.append("Error")
    return "<br>".join(ports)

def main(folder_path_json: str, folder_path_html: str):
    with open(f"{folder_path_json}env.json") as file:
        data_env = json.load(file)
        mgmt_ip = data_env.get("mgmt_ip")
        groupe_name = data_env.get("groupe_name")
        precedence = data_env.get("precedence")

    html_h = f'''
    <div class="container">
        <h3>Firewall Security Rules</h3>
        <div class="header-info">
            <p><strong>Management IP:</strong> {mgmt_ip}</p>
            <p><strong>Group Name:</strong> {groupe_name}</p>
            <p><strong>Precedence:</strong> {precedence}</p>
        </div>
    </div>
    '''

    with open(f"{folder_path_json}rules.json") as file:
        data = json.load(file)

    with open(f"{folder_path_json}groups_service.json") as file:
        data_service = json.load(file)

    with open(f"{folder_path_json}groups_ip.json") as file:
        data_ip = json.load(file)

    items = data["items"]
    data_group_ip = [item["group"] for item in data_ip]
    data_group_service = [item["serviceGroup"] for item in data_service]
    records = []

    for item in items:
        enabled = "On ✅" if item.get("enabled", False) else "Off❌"
        record = {
            "Enabled": enabled,
            "Name": item.get("name", ""),
            "Description": item.get("description", ""),
            "Source Zone": extract_name(item.get("sourceZone", {}).get("objects", []), "name"),
            "Source IP": extract_name_or_ip(item.get("sourceAddr", {}).get("objects", []), data_group_ip),
            "Destination Zone": extract_name(item.get("destinationZone", {}).get("objects", []), "name"),
            "Destination IP": extract_name_or_ip(item.get("destinationAddr", {}).get("objects", []), data_group_ip),
            "Service": extract_name_or_port(item.get("service", []), data_group_service),
            "Application": extract_name(item.get("application", {}).get("objects", []), "name"),
            "URL Category": extract_name(item.get("urlCategory", {}).get("objects", []), "name"),
            "IPS": item.get("ipsProfile", {}).get("name", ""),
            "Antivirus": item.get("avProfile", {}).get("name", ""),
            "Action": item.get("action", "").replace("SECURITY_RULE_ACTION_", ""),
            "Log Mode": item.get("logMode", "").replace("SECURITY_RULE_LOG_MODE_", ""),
            "Schedule": item.get("schedule", "")
        }
        records.append(record)

    df = pd.DataFrame(records)
    # Изменяем индекс: начинаем с 1 вместо 0
    df.index = df.index + 1
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Firewall Rules - {groupe_name}</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600&display=swap" rel="stylesheet">
        {css_style}
    </head>
    <body>
        {html_h}
        {df.to_html(classes='dataframe', escape=False)}
    </body>
    </html>
    '''

    name = "rules_resolv.html"
    with open(f"{folder_path_html}{groupe_name}_{name}", 'w', encoding='utf-8') as f:
        f.write(html)


folder_path_json = "/home/sb/Documents/WORK/NGFW-scripts/pt-NGFW-Rules-to-HTML/json/"
folder_path_html = "/home/sb/Documents/WORK/NGFW-scripts/pt-NGFW-Rules-to-HTML/html/"

main(folder_path_json, folder_path_html) 
