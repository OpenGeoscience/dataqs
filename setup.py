import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='dataqs',
    version='0.1',
    packages=['dataqs'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple GeoNode app to download, process, and import '
                'spatial data into PostGIS.',
    long_description=README,
    url='http://www.example.com/',
    author='Matt Bertrand ',
    author_email='matt@epidemico.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'psycopg2',
        'requests',
        'celery',
        'geopy',
        'fiona',
        'unicodecsv',
        'shapely',
        'pymongo',
        'numpy',
        'rasterio==0.31.0',
        'gdal==1.11.2'
    ]
)
