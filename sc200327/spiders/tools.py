import sys
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


def get_arguments() -> dict:
    arguments = sys.argv
    dictionary = {}
    for i in range(len(arguments)):
        if arguments[i] == '-a':
            args = arguments[i+1].split('=')
            dictionary[args[0]] = args[1]
    return dictionary
