import json
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
    border-spacing: 0 5px;
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

.dataframe td table tbody tr:nth-child(even) {
       background-color: #f9f9f9; 
   }

.dataframe tbody tr:hover {
    background-color: #f1f1f1;
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

/* Перенос текста и ограничение ширины для второго столбца */
.dataframe td:nth-child(2),
.dataframe th:nth-child(2) {
    max-width: 150px;
    word-wrap: break-word;
    white-space: normal;
}
</style>
"""

def extract(objects):
    rows = []
    
    for obj in objects:
        if 'networkIpAddress' in obj:
            inet = obj['networkIpAddress'].get('inet', '')
            name = obj['networkIpAddress'].get('name', '')
            ip_type = obj['networkIpAddress'].get('type', '')
            
            row = (
                '<tr>'
                f'<td><strong>{inet}</strong></td>'
                f'<td>{name}</td>'
                f'<td><i>{ip_type}</i></td>'
                '</tr>'
            )
            rows.append(row)
        elif 'networkFqdn' in obj:
            fqdn = obj['networkFqdn'].get('fqdn', '')
            name = obj['networkFqdn'].get('name', '')
            fqdn_type = obj['networkFqdn'].get('type', '')
            
            row = (
                '<tr>'
                f'<td><strong>{fqdn}</strong></td>'
                f'<td>{name}</td>'
                f'<td><i>{fqdn_type}</i></td>'
                '</tr>'
            )
            rows.append(row)
        elif 'networkGroup' in obj:
            name = obj['networkGroup'].get('name', '')
            desc = obj['networkGroup'].get('description', '')
            group_type = 'networkGroup'
            
            row = (
                '<tr>'
                f'<td><strong>{name}</strong></td>'
                f'<td>{desc}</td>'
                f'<td><i>{group_type}</i></td>'
                '</tr>'
            )
            rows.append(row)
        elif 'networkGeoAddress' in obj:
            desc = obj['networkGeoAddress'].get('description', '')
            name = obj['networkGeoAddress'].get('name', '')
            geo_address_type = obj['networkGeoAddress'].get('type', '')
            
            row = (
                '<tr>'
                f'<td><strong>{desc}</strong></td>'
                f'<td>{name}</td>'
                f'<td><i>{geo_address_type}</i></td>'
                '</tr>'
            )
            rows.append(row)
        elif 'networkIpRange' in obj:
            from_range = obj['networkIpRange'].get('from', '')
            to_range = obj['networkIpRange'].get('to', '')
            name = obj['networkIpRange'].get('name', '')
            range_type = obj['networkIpRange'].get('type', '')
            
            row = (
                '<tr>'
                f'<td><strong>{from_range} - {to_range}</strong></td>'
                f'<td>{name}</td>'
                f'<td><i>{range_type}</i></td>'
                '</tr>'
            )
            rows.append(row)
    
    table_content = ''.join(rows)
    return f'''<table border="1" cellpadding="4" style="border-collapse: collapse; width: 100%;"><tbody>{table_content}</tbody></table>'''

def main(folder_path_json: str, folder_path_html: str):


    with open(f"{folder_path_json}env.json") as file:
        data_env = json.load(file)
        mgmt_ip = data_env.get("mgmt_ip")
        groupe_name = data_env.get("groupe_name")
        precedence = data_env.get("precedence")

    html_h = f'''
    <div class="container">
        <h3>Groups IP </h3>
        <p>IP адрес системы управления: <strong>{mgmt_ip}</strong></p>
        <p>Имя группы: <strong>{groupe_name}</strong></p>
        <p>Приоритет: <strong>{precedence}</strong></p>
    '''


    with open(f"{folder_path_json}groups_ip.json") as file:
        data = json.load(file)
 
    records = []

    for item in data:
        record = {}
        
        record["Name"] = item["group"].get("name", "")
        record["Description"] = item["group"].get("description", "")

        record["Value | Name | Type"] = extract(item["group"].get("items", {}))
 

        records.append(record)

    df = pd.DataFrame(records)

    html = css_style +  html_h  + df.to_html(classes='dataframe', escape=False, index=False) + '</div>'

    with open(f"{folder_path_html}{groupe_name}_groups_ip.html", 'w', encoding='utf-8') as f:
        f.write(html)


# Путь к папкам
# Путь к папкам
folder_path_json = "H:/WORK/json/"
folder_path_html = "H:/WORK/html/"

main(folder_path_json, folder_path_html)