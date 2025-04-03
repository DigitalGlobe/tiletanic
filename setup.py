import sys
from setuptools import setup, find_packages

open_kwds = {}
if sys.version_info > (3,):
    open_kwds['encoding'] = 'utf-8'

with open('README.rst', **open_kwds) as f:
    readme = f.read()

setup(name='tiletanic',
      version='1.1.0',
      description='Geospatial tiling utilities',
      long_description=readme,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
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
                        'shapely>=1.6'],
      entry_points='''
         [console_scripts]
         tiletanic=tiletanic.cli:cli
      '''
      )
