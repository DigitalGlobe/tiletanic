from setuptools import setup, find_packages

setup(name='tiletanic',
      version='0.0.0',
      description='Geospatial tiling utilities',
      long_description='ADD README',
      classifiers=[],
      keywords='',
      author='Patrick Young',
      author_email='patrick.young@digitalglobe.com',
      url='https://github.com/digitalglobe/tiletanic',
      license='BSD',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['shapely>=1.5']
      )
