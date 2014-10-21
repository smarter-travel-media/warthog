# -*- coding: utf-8 -*-

import pytest
import warthog.api
import warthog.exceptions


@pytest.fixture
def exports():
    return set([item for item in dir(warthog.api) if not item.startswith('_')])


def test_public_exports(exports):
    declared = set(warthog.api.__all__)
    assert exports == declared, 'Exports and __all__ members should match'


def test_all_exceptions_imported(exports):
    errors = set([item for item in dir(warthog.exceptions) if item.endswith('Error') or item.endswith('Warning')])
    intersection = errors.intersection(exports)

    assert intersection == errors, "All available errors should be in warthog.api"

