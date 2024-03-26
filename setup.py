#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
from setuptools import setup


name = 'djangorestframework-datatables'
package = 'rest_framework_datatables'
description = (
    'Seamless integration between Django REST framework and '
    'Datatables (https://datatables.net)'
)
url = 'https://github.com/izimobil/django-rest-framework-datatables'
author = 'David Jean Louis'
author_email = 'izimobil@gmail.com'
license = 'MIT'


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, '__init__.py')) as fh:
        return re.search(
            "^__version__ = ['\"]([^'\"]+)['\"]",
            fh.read(),
            re.MULTILINE
        ).group(1)
    init_py = open(os.path.join(package, '__init__.py')).read()


def get_long_description():
    """
    Return rst formatted readme and changelog.
    """
    ret = []
    with open('README.rst') as fh:
        ret.append(fh.read())
    try:
        with open('docs/changelog.rst') as fh:
            ret.append(fh.read())
    except IOError:
        pass
    return '\n\n'.join(ret)


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


version = get_version(package)

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(version))
    print("  git push --tags")
    sys.exit()


setup(
    name=name,
    version=version,
    url=url,
    license=license,
    description=description,
    long_description=get_long_description(),
    author=author,
    author_email=author_email,
    packages=[
        'rest_framework_datatables',
        'rest_framework_datatables.django_filters'
    ],
    install_requires=[
        'djangorestframework>=3.14.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
