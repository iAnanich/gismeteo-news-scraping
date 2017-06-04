# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '0.1',
    packages     = find_packages(),
    data_files   = [('sc200327', ['sc200327/client-secret.json'])],
    entry_points = {'scrapy': ['settings = sc200327.settings']},
)
