#!/usr/bin/env python

from setuptools import setup, find_packages
my_packages = find_packages()

setup(
    name="flask_jsonapi_trivial",
    version=open("VERSION").read(),
    url="http://github.com/subsect/flask_jsonapi_trivial/",
    license="CC BY-NC-SA 4.0",
    author="austinjp",
    author_email="austin.plunkett+pypi@gmail.com",
    description="Provides Flask with *very basic* JSONAPI.org compliance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=my_packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[ _ for _ in open("requirements.txt").read().split("\n") if _ ],
    python_requires="~=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
