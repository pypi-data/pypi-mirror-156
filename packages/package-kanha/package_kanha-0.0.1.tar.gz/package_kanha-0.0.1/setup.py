from setuptools import setup, find_packages



classifiers = [
    'Development Status :: 5 - Production/Stable',
'Intended Audience :: Education',
'Operating System :: Microsoft :: Windows :: Windows 10',
'License :: OSI Approved :: MIT License',
'Programming Language :: Python :: 3.9'
]

setup(


name= 'package_kanha',
version= '0.0.1',

description= 'This is very basic calculator',
Long_description=open('readme.txt').read() + '\n\n' + open('changeslog.txt').read(),
url='',


author= 'kanhaiya kumar',
author_email='kanhaiya20@iitk.ac.in',

License= 'MIT',
classifiers= classifiers,
keywords ='calculator',
packages=find_packages(),
install_requires=['']
 )