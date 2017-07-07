# Automatically created by: shub deploy

from setuptools import setup, find_packages


PROJECT_DIRECTORY_NAME = 'scrapy_climate'


setup(
    name='project',
    version='0.1',
    packages=find_packages(),
    scripts=['bin/prepare_worksheet.py'],
    data_files=[(PROJECT_DIRECTORY_NAME, [PROJECT_DIRECTORY_NAME+'/client-secret.json',
                                    PROJECT_DIRECTORY_NAME+'/options.json'])],
    entry_points={'scrapy': ['settings = {}.settings'.format(PROJECT_DIRECTORY_NAME)]},
)
