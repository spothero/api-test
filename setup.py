import os
from setuptools import find_packages, setup

# with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
#     README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='api-test',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    # license='BSD License',  # example license
    description='App to test rest framework apis.',
    # long_description=README,
    # url='https://www.example.com/',
    author='Ashley Kasza',
    author_email='ashley@spothero.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)