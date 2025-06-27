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
            
            if 'SERVICE_PROTOCOL_ICMP' in obj['service']['protocol']:
                name = obj['service'].get('name', '')
                row = (
                    '<tr>'
                    f'<td><strong> </strong></td>'
                    f'<td><strong> </strong></td>'
                    f'<td>{name}</td>'
                    f'<td><i>ICMP</i></td>'
                    '</tr>'
                )
                rows.append(row)

            else:
                # Обработка srcPorts
                if len(obj['service']['srcPorts']) > 0:
                    src_port = ""
                    if 'singlePort' in obj['service']['srcPorts'][0]:
                        for i in obj['service']['srcPorts']:
                            src_port = f"{src_port}" + f"{i['singlePort']['port']}<br>"
                    elif 'portRange' in obj['service']['srcPorts'][0]:
                        for i in obj['service']['srcPorts']:
                            src_t = f"{i['portRange']}".replace('}', '').replace("'", '').replace("{", '')
                            src_port = f"{src_port}" + f"{src_t}<br>"
                    else:
                        print('ERR: srcPorts type unknown')
                    
                else:
                    src_port = ""
                    
                # Обработка dstPorts
                if len(obj['service']['dstPorts']) > 0:
                    dst_port = ""
                    #if 'singlePort' in obj['service']['dstPorts'][0]:
                    for i in obj['service']['dstPorts']:
                        if 'singlePort' in i:
                            dst_port = f"{dst_port}" + f"{i['singlePort']['port']}<br>"
                        elif 'portRange' in i:
                            dst_t = f"{i['portRange']}".replace('}', '').replace("'", '').replace("{", '')
                            dst_port = f"{dst_port}" + f"{src_port}" + f"{dst_t}<br>"
                    # elif 'portRange' in obj['service']['dstPorts'][0]:
                    #     for i in obj['service']['dstPorts']:
                    #         dst_t = f"{i['portRange']}".replace('}', '').replace("'", '').replace("{", '')
                    #         dst_port = f"{src_port}" + f"{dst_t}<br>"
                        else:
                            print('ERR: dstPorts type unknown')

                name = obj['service'].get('name', '')
                protocol = obj['service'].get('protocol', '').replace("SERVICE_PROTOCOL_", "")
                row = (
                    '<tr>'
                    f'<td><strong>{src_port}</strong></td>'
                    f'<td><strong>{dst_port}</strong></td>'
                    f'<td>{name}</td>'
                    f'<td><i>{protocol}</i></td>'
                    '</tr>'
                )
                rows.append(row)


                      

        elif 'serviceGroup' in obj:
                name = obj['serviceGroup'].get('name', '')
                row = (
                    '<tr>'
                    f'<td><strong></strong></td>'
                    f'<td><strong></strong></td>'
                    f'<td>{name}</td>'
                    f'<td><i>Group</i></td>'
                    '</tr>' )
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
folder_path_json = "C:/Users/Desktop/pt-Rules-to-HTML-main/json/"
folder_path_html = "C:/Users/Desktop/pt-Rules-to-HTML-main/html/"

main(folder_path_json, folder_path_html)
