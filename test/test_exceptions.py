# -*- coding: utf-8 -*-

import warthog.exceptions


class TestWarthogError(object):
    def test_str(self):
        err = warthog.exceptions.WarthogError('Oh no!', api_msg='Something bad', api_code=1234)
        str_err = str(err)

        assert 'Oh no!' in str_err, 'Did not see expected message in error'
        assert 'Something bad' in str_err, 'Did not see expected API message in error'
        assert '1234' in str_err, 'Did not see expected API code in error'

    def test_repr(self):
        err = warthog.exceptions.WarthogError('Oh no!', api_msg='Something bad', api_code=1234)
        repr_err = repr(err)

        assert 'WarthogError("Oh no!", api_msg="Something bad", api_code=1234)' == repr_err, \
            'Did not get expected repr of exception'