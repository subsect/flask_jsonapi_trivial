#!/usr/bin/env python

from setuptools import setup, find_packages
my_packages = find_packages()

setup(
    name='Flask-JSONAPI-trivial',
    version='0.2.0',
    url='http://github.com/subsect/flask-jsonapi-trivial/',
    license='CC BY-NC-SA 4.0',
    author='Austin Plunkett',
    author_email='austin.plunkett+flask@gmail.com',
    description='Provides Flask with *very basic* JSONAPI.org compliance',
    long_description=open("README.md").read(),
    # py_modules=['flask_jsonapi_trivial'],
    packages=my_packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'python-jose[cryptography]'
        'Werkzeug'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
