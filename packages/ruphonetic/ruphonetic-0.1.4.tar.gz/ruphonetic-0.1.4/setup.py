from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='ruphonetic',
  version='0.1.4',
  description='Russian Phonetic Analysis Module',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='', 
  author='Igor Furkalo',
  author_email='igor.furkalo@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='quantanalysis', 
  packages=find_packages(),
  install_requires=['spacy==3.3.0', 'matplotlib==3.5.2'] 
)





