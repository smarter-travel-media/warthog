# -*- coding: utf-8 -*-

from fabric.api import (
    lcd,
    local,
    task)


@task
def clean():
    local('rm -rf wheelhouse')
    local('rm -rf dist')
    local('rm -rf build')

    with lcd('doc'):
        local('make clean')


@task
def docs():
    with lcd('doc'):
        local('make html')


@task
def push():
    local('git push origin')


@task
def push_tags():
    local('git push --tags origin')


@task
def pypi():
    # local('python setup.py register sdist upload')
    pass