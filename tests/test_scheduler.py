# coding=utf-8
"""Test Scheduler.getSkippedUpdates()."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mocks; mocks.install()
from architect.core.scheduler import Scheduler


class TestSchedulerSkipped(unittest.TestCase):
    def setUp(self):
        self.sched = Scheduler()

    def test_initial_zero(self):
        self.assertEqual(self.sched.getSkippedUpdates(), 0)

    def test_increment_on_reentry(self):
        calls = []

        def reentrant():
            calls.append(1)
            self.sched.executeSequence()

        self.sched.addTask('Update', reentrant)
        self.sched.executeSequence()
        self.assertGreater(self.sched.getSkippedUpdates(), 0)


if __name__ == '__main__':
    unittest.main()