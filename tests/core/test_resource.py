import unittest
from pyshared.core.resource import WrappedResource


class WrapperResourceTest(unittest.TestCase):
    def test_instance_check(self):
        a = str()
        w = WrappedResource(a, str)
        self.assertTrue(isinstance(a, str))
        self.assertTrue(isinstance(w, str))
