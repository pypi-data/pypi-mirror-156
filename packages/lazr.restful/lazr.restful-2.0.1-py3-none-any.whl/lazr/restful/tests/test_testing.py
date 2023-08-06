# Copyright 2022 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.restful.
#
# lazr.restful is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.restful is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.restful.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict

from testtools import TestCase

from lazr.restful.testing.webservice import pformat_value


class TestPrettyFormatValue(TestCase):
    """Test `lazr.restful.testing.webservice.pformat_value`."""

    def test_string(self):
        self.assertEqual("'foo'", pformat_value("foo"))

    def test_bytes(self):
        self.assertEqual("b'foo'", pformat_value(b"foo"))

    def test_ordered_dict(self):
        self.assertEqual(
            "{'abc': 'def', 'ghi': 'jkl'}",
            pformat_value(OrderedDict((("abc", "def"), ("ghi", "jkl")))),
        )

    def test_list_of_ordered_dicts(self):
        self.assertEqual(
            "[{'abc': 'def', 'ghi': 'jkl'}]",
            pformat_value([OrderedDict((("abc", "def"), ("ghi", "jkl")))]),
        )
