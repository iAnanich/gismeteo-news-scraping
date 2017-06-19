import csv
import json
import time
import requests as r
from datetime import timedelta


def _parse_json_responce(url: str):
    with r.Session() as s:
        response = s.get(url)
        decoded_content = response.content.decode('utf-8')
        return [json.loads(d) for d in decoded_content.splitlines()]


def _fetch_job_keys_from_week(project_id: str, spider_name: str, key: str):
    week_ago = int((time.time() - timedelta(weeks=1).total_seconds()) * 10**3)  # miliseconds
    url_jobs = 'https://storage.scrapinghub.com/jobq/{project}/list?' \
               'startts={time}&spider={spider}&state={state}&apikey={key}'.format \
               (time=week_ago, spider=spider_name, project=project_id, state='finished', key=key)
    return [job['key'] for job in _parse_json_responce(url_jobs)]


def fetch_indexes_from_week(project_id: str, spider_name: str, key: str):
    for job_key in _fetch_job_keys_from_week(project_id, spider_name, key):
        url = 'https://storage.scrapinghub.com/items/{job_key}?' \
              'format=json&apikey={key}'.format(job_key=job_key, key=key)
        for item in _parse_json_responce(url)[0]:
            index = item.get('index', None)
            if index is not None:
                yield index


def convert_list_to_string(lst: list, separator: str, handler=str) -> str:
    if len(lst) == 0:
        return ''
    string = handler(lst[0])
    for item in lst[1:]:
        string += separator + handler(item)
    return string
