# coding=utf-8
"""Test CommandBus register, execute and unregister."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from architect.core.bus import CommandBus


class TestCommandBus(unittest.TestCase):
    def setUp(self):
        self.bus = CommandBus()

    def test_register_and_execute(self):
        calls = []
        self.bus.register('spawn', lambda name: calls.append(name))
        self.bus.execute('spawn', 'npc')
        self.assertEqual(calls, ['npc'])

    def test_unregister(self):
        calls = []
        unreg = self.bus.register('spawn', lambda: calls.append(1))
        unreg()
        self.bus.execute('spawn')
        self.assertEqual(calls, [])

    def test_multiple_handlers(self):
        results = []
        self.bus.register('test', lambda: results.append('a'))
        self.bus.register('test', lambda: results.append('b'))
        self.bus.execute('test')
        self.assertEqual(results, ['a', 'b'])

    def test_has_command(self):
        self.assertFalse(self.bus.hasCommand('test'))
        unreg = self.bus.register('test', lambda: None)
        self.assertTrue(self.bus.hasCommand('test'))
        unreg()
        self.assertFalse(self.bus.hasCommand('test'))

    def test_clear_command(self):
        self.bus.register('test', lambda: None)
        self.bus.clearCommand('test')
        self.assertFalse(self.bus.hasCommand('test'))

    def test_clear_all(self):
        self.bus.register('a', lambda: None)
        self.bus.register('b', lambda: None)
        self.bus.clearAll()
        self.assertEqual(len(self.bus._handlers), 0)


if __name__ == '__main__':
    unittest.main()