#from distutils.core import setup
from setuptools import setup, find_packages
from setuptools import find_namespace_packages
setup(name='hkw',
      version='1.2.4',
      description = 'hkwarray.',
      author='hkw',
      author_email='kkhwer@gmail.com',
      packages=find_namespace_packages(where='src'),
      package_dir = {"": "src"},
	package_data={
		"hkw.rdata_": ["*.*"],
	}
	
      )


