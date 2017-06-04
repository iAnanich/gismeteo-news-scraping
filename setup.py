# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '0.1',
    packages     = find_packages(),
    data_files=[('gismeteo', ['gismeteo/client-secret.json'])],
    entry_points={'scrapy': ['settings = gismeteo.settings']},
)
