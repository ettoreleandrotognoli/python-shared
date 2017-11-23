import unittest
from pyshared.core.shared import make_resource_name


class ResourceNameTest(unittest.TestCase):
    def test_class_instance(self):
        a = object()
        expected = 'object:a'
        result = make_resource_name(a)
        self.assertTrue(result.startswith(expected), '{} don\'t starts with {}'.format(result, expected))
