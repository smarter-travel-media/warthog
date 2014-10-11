# -*- coding: utf-8 -*-

import warthog.api


def test_public_exports():
    exports = set([item for item in dir(warthog.api) if not item.startswith('_')])
    declared = set(warthog.api.__all__)
    assert exports == declared, 'Exports and __all__ members should match'
