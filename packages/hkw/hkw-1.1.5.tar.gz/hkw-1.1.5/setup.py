#from distutils.core import setup
from setuptools import setup, find_packages
from setuptools import find_namespace_packages
setup(name='hkw',
      version='1.1.5',
      description = 'hkwarray.',
      author='hkw',
      author_email='kkhwer@gmail.com',
      packages=find_namespace_packages(where='src'),
      package_dir = {"": "src"},
      include_package_data=True,
      )


