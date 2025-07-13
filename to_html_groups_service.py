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
        if 'service' in obj:
            protocol = obj['service'].get('protocol', '')
            name = obj['service'].get('name', '')
            # ICMP
            if protocol == 'SERVICE_PROTOCOL_ICMP':
                row = (
                    '<tr>'
                    '<td><strong> </strong></td>'
                    '<td><strong> </strong></td>'
                    f'<td>{name}</td>'
                    '<td><i>ICMP</i></td>'
                    '</tr>'
                )
                rows.append(row)
            else:
                # SRC PORTS
                src_port = ""
                for i in obj['service'].get('srcPorts', []):
                    if 'singlePort' in i:
                        src_port += f"{i['singlePort']['port']}<br>"
                    elif 'portRange' in i:
                        pr = i['portRange']
                        src_port += f"{pr.get('from', '')}-{pr.get('to', '')}<br>"
                # DST PORTS
                dst_port = ""
                for i in obj['service'].get('dstPorts', []):
                    if 'singlePort' in i:
                        dst_port += f"{i['singlePort']['port']}<br>"
                    elif 'portRange' in i:
                        pr = i['portRange']
                        dst_port += f"{pr.get('from', '')}-{pr.get('to', '')}<br>"
                protocol_str = protocol.replace("SERVICE_PROTOCOL_", "")
                row = (
                    '<tr>'
                    f'<td><strong>{src_port}</strong></td>'
                    f'<td><strong>{dst_port}</strong></td>'
                    f'<td>{name}</td>'
                    f'<td><i>{protocol_str}</i></td>'
                    '</tr>'
                )
                rows.append(row)

        elif 'serviceGroup' in obj:
            group_name = obj['serviceGroup'].get('name', '')
            group_items = obj['serviceGroup'].get('items', [])
            # Вложенная таблица для группы
            nested_table = extract(group_items)
            row = (
                '<tr>'
                f'<td colspan="4">'
                f'<div style="margin:8px 0;"><b>Группа: {group_name}</b></div>{nested_table}'
                '</td>'
                '</tr>'
            )
            rows.append(row)
        else:
            print('ERR: item unknown')

    table_content = ''.join(rows)
    return f'''<table border="1" cellpadding="4" style="border-collapse: collapse; width: 100%;"><tbody>{table_content}</tbody></table>'''

def main(folder_path_json: str, folder_path_html: str):
    with open(f"{folder_path_json}groups_service.json") as file:
        data = json.load(file)
 

    with open(f"{folder_path_json}env.json") as file:
        data_env = json.load(file)
        mgmt_ip = data_env.get("mgmt_ip")
        groupe_name = data_env.get("groupe_name")
        precedence = data_env.get("precedence")

    html_h = f'''
    <div class="container">
        <h3>Service Groups</h3>
        <p>IP адрес системы управления: <strong>{mgmt_ip}</strong></p>
        <p>Имя группы: <strong>{groupe_name}</strong></p>
        <p>Приоритет: <strong>{precedence}</strong></p>
    '''

    records = []

    for item in data:
        record = {}
        
        record["Name"] = item["serviceGroup"].get("name", "")
        record["Description"] = item["serviceGroup"].get("description", "")

        record["SRC | DST | Name | Type"] = extract(item["serviceGroup"].get("items", {}))
 

        records.append(record)

    df = pd.DataFrame(records)

    html = css_style +  html_h + df.to_html(classes='dataframe', escape=False, index=False) + '</div>'

    with open(f"{folder_path_html}{groupe_name}_groups_service.html", 'w', encoding='utf-8') as f:
        f.write(html)


# Путь к папкам
# Путь к папкам
folder_path_json = "H:/WORK/json/"
folder_path_html = "H:/WORK/html/"

main(folder_path_json, folder_path_html)
