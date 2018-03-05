from setuptools import setup
from setuptools import find_packages


setup(name='estim2b',
      version='0.1',
      description='Unofficial Python API for E-stim 2B',
      author='Fred Hatt',
      author_email='fred.r.hatt@gmail.com',
      url='https://github.com/fredhatt/estim2b',
      license='MIT',
      install_requires=['numpy', 'pyserial'],
      packages=find_packages())
