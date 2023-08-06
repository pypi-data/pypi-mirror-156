from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='forcer',
  version='0.0.1',
  description='A library to use Brute Force methods',
  long_description=open('README.md', encoding='utf-8').read() + '\n\n' + open('CHANGELOG.txt', encoding='utf-8').read(),
  url='https://github.com/ju-dev-16',  
  author='Jahid Uddin',
  author_email='jahidudd65@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='brute force passwords dictionary ssh login', 
  packages=find_packages(),
  install_requires=['bs4', 'paramiko'] 
)