# coding=utf-8
"""测试 Marker 实体生命周期事件。"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mocks; mocks.install()
from architect.component.core import Marker


class TestMarkerEntityLifecycle(unittest.TestCase):
    def setUp(self):
        self.marker = Marker()
        self.created = []
        self.destroyed = []

    def test_emit_on_first_mark(self):
        self.marker.onEntityCreated.on(lambda eid: self.created.append(eid))
        self.marker.mark('entity-1')
        self.assertEqual(self.created, ['entity-1'])

    def test_no_emit_on_second_mark(self):
        self.marker.mark('entity-1')
        self.marker.onEntityCreated.on(lambda eid: self.created.append(eid))
        self.marker.mark('entity-1')
        self.assertEqual(self.created, [])

    def test_emit_on_last_unmark(self):
        self.marker.mark('entity-1')
        self.marker.mark('entity-1')
        self.marker.onEntityDestroyed.on(lambda eid: self.destroyed.append(eid))
        self.marker.unmark('entity-1')
        self.assertEqual(self.destroyed, [])
        self.marker.unmark('entity-1')
        self.assertEqual(self.destroyed, ['entity-1'])

    def test_no_emit_on_intermediate_unmark(self):
        self.marker.mark('entity-1')
        self.marker.mark('entity-1')
        self.marker.onEntityDestroyed.on(lambda eid: self.destroyed.append(eid))
        self.marker.unmark('entity-1')
        self.assertEqual(self.destroyed, [])


if __name__ == '__main__':
    unittest.main()