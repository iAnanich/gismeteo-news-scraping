from scrapinghub import ScrapinghubClient

from .args import options

import time
import datetime


class CloudInterface:

    def __init__(self):
        self.client = ScrapinghubClient(options.api_key)
        self.project = self.client.get_project(options.current_project_id)
        self.spider = self._get_current_spider()

    def _get_current_spider(self):
        for spider_dict in self.project.spiders.list():
            spider = self.project.spiders.get(spider_dict['id'])
            if spider.key.split('/')[1] == options.current_spider_id:
                return spider
        else:
            raise RuntimeError('No spider found.')

    def _fetch_week_jobs(self):
        delta_seconds = datetime.timedelta(weeks=1).total_seconds() + 60 * 60
        week_ago = int((time.time() - delta_seconds) * (10 ** 3))
        for job_summary in self.spider.jobs.iter(startts=week_ago,
                                                 state='finished',
                                                 jobmeta=['key']):
            yield self.project.jobs.get(job_summary['key'])

    def fetch_week_items(self):
        for job in self._fetch_week_jobs():
            yield from job.items.iter()

    def fetch_week_indexes(self):
        for item in self.fetch_week_items():
            yield item['index']
