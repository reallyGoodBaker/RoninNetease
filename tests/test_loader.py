# coding=utf-8
"""Test plugin dependency topological ordering."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FakeHost(object):
    def __init__(self, name, deps=None):
        self.name = name
        self.dependencies = deps or {}


class TestTopologicalOrder(unittest.TestCase):
    def setUp(self):
        from architect.core.loader import _topologicalOrder
        self._topologicalOrder = _topologicalOrder

    def test_no_dependencies(self):
        reg = {'a': FakeHost('a'), 'b': FakeHost('b')}
        result = self._topologicalOrder(reg)
        names = [n for n, _ in result]
        self.assertEqual(set(names), {'a', 'b'})

    def test_dependency_before_dependent(self):
        reg = {
            'a': FakeHost('a'),
            'b': FakeHost('b', {'a': '>=1.0'}),
        }
        result = self._topologicalOrder(reg)
        names = [n for n, _ in result]
        self.assertLess(names.index('a'), names.index('b'))

    def test_circular_dependency_safe(self):
        reg = {
            'a': FakeHost('a', {'b': '>=1.0'}),
            'b': FakeHost('b', {'a': '>=1.0'}),
        }
        try:
            result = self._topologicalOrder(reg)
            names = [n for n, _ in result]
            self.assertEqual(set(names), {'a', 'b'})
        except RecursionError:
            self.fail('topologicalOrder caused RecursionError')

    def test_missing_dependency(self):
        reg = {
            'a': FakeHost('a', {'nonexistent': '>=1.0'}),
            'b': FakeHost('b'),
        }
        result = self._topologicalOrder(reg)
        names = [n for n, _ in result]
        self.assertEqual(set(names), {'a', 'b'})


if __name__ == '__main__':
    unittest.main()