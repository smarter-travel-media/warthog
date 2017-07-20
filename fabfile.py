# -*- coding: utf-8 -*-

from fabric.api import (
    hide,
    lcd,
    local,
    quiet,
    task,
    warn_only)


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
def lint():
    with warn_only():
        local('pylint --rcfile .pylintrc warthog')


@task
def coverage():
    with quiet():
        local('coverage run --source warthog ./.env/bin/py.test test')

    with hide('running'):
        local("coverage report  --omit 'warthog/packages*' --show-missing")


@task
def push():
    local('git push origin')


@task
def push_tags():
    local('git push --tags origin')


@task
def pypi():
    local('python setup.py sdist bdist_wheel')
    local('twine upload dist/*')
