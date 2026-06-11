# coding=utf-8
"""Test Profiler record, snapshot and flush."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from architect.core.profiler import Profiler


class TestProfiler(unittest.TestCase):
    def setUp(self):
        self.profiler = Profiler()

    def test_record_and_flush(self):
        with self.profiler.record('test.a'):
            pass
        snap = self.profiler.flush()
        self.assertIn('test.a', snap)
        self.assertIn('avg_ms', snap['test.a'])
        self.assertIn('max_ms', snap['test.a'])
        self.assertEqual(snap['test.a']['count'], 1)
        self.assertEqual(self.profiler.flush(), {})

    def test_snapshot_does_not_reset(self):
        with self.profiler.record('test.b'):
            pass
        snap1 = self.profiler.snapshot()
        self.assertEqual(snap1['test.b']['count'], 1)
        snap2 = self.profiler.snapshot()
        self.assertEqual(snap2['test.b']['count'], 1)

    def test_disable(self):
        self.profiler.disable()
        with self.profiler.record('test.c'):
            pass
        self.assertEqual(self.profiler.flush(), {})

    def test_enable(self):
        self.profiler.disable()
        self.profiler.enable()
        with self.profiler.record('test.d'):
            pass
        snap = self.profiler.flush()
        self.assertEqual(snap['test.d']['count'], 1)


if __name__ == '__main__':
    unittest.main()