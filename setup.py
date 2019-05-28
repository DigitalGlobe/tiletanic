import sys
from setuptools import setup, find_packages

open_kwds = {}
if sys.version_info > (3,):
    open_kwds['encoding'] = 'utf-8'

with open('README.rst', **open_kwds) as f:
    readme = f.read()

setup(name='tiletanic',
      version='1.0.0',
      description='Geospatial tiling utilities',
      long_description=readme,
      classifiers=[
          'Programming Language :: Python :: 3.6',
      ],
      keywords='',
      author='Patrick Young',
      author_email='patrick.young@digitalglobe.com',
      url='https://github.com/digitalglobe/tiletanic',
      license='MIT',
      packages=find_packages(exclude=['tests', 'docs']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['click',
                        'geojson',
                        'shapely>=1.5',
                        'fiona>=1.8.6',
      ],
      entry_points='''
         [console_scripts]
         tiletanic=tiletanic.cli:cli
      '''
      )
