from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='nigeria',
  version='0.0.1',
  description='An API for nigeria',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Odeyemi Increase Ayobami',
  author_email='odeyemiincrease@yahoo.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Africa, Nigeria', 
  packages=find_packages(),
  install_requires=[''] 
)