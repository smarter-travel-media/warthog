# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import warthog


AUTHOR = 'Smarter Travel',
EMAIL = ''
DESCRIPTION = 'Simple client for A10 load balancers'

REQUIREMENTS = [
    'requests'
]

setup(
    name='warthog',
    version=warthog.__version__,
    author=AUTHOR,
    description=DESCRIPTION,
    author_email=EMAIL,
    install_requires=REQUIREMENTS,
    zip_safe=True,
    packages=find_packages())
