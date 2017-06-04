import csv

import requests as r


def fetch_latest_job(fields: str, project: str, spider: str, key: str) -> list:
    url = 'https://app.scrapinghub.com/api/items.csv?' \
          'project={project}&spider={spider}&include_headers=1&fields={fields}&apikey={key}' \
          .format(project=project, key=key, spider=spider, fields=fields)
    with r.Session() as s:
        response = s.get(url)
        decoded_content = response.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        table = list(cr)
    return table


def clear(string: str) -> str:
    return string.replace('\xa0', ' ')


def clear_text(item) -> str:
    string = clear(str(item))
    return string.replace('\n', '')


def convert_list_to_string(lst: list, separator: str, handler=str) -> str:
    if len(lst) == 0:
        return ''
    string = handler(lst[0])
    for item in lst[1:]:
        string += separator + handler(item)
    return string
