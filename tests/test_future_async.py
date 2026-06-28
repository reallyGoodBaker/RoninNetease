# coding=utf-8
"""Test Future, SuspendableTask, and Scheduler."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mocks
mocks.install()

from architect.core.scheduler import Future, Scheduler, SuspendableTask


class TestFutureResolve(unittest.TestCase):
    def test_resolve_calls_done_callback(self):
        results = []
        ftr, resolve, reject = Future.resolvers()
        ftr.done(lambda v: results.append(v))
        resolve(42)
        self.assertEqual(results, [42])

    def test_reject_calls_expected_callback(self):
        errors = []
        ftr, resolve, reject = Future.resolvers()
        ftr.expected(lambda e: errors.append(e))
        reject('fail')
        self.assertEqual(errors, ['fail'])

    def test_done_after_resolve_calls_immediately(self):
        results = []
        ftr, resolve, _ = Future.resolvers()
        resolve('early')
        ftr.done(lambda v: results.append(v))
        self.assertEqual(results, ['early'])

    def test_expected_after_reject_calls_immediately(self):
        errors = []
        ftr, _, reject = Future.resolvers()
        reject(ValueError('bad'))
        ftr.expected(lambda e: errors.append(str(e)))
        self.assertEqual(errors, ['bad'])

    def test_chain_done_expected(self):
        results = []
        errors = []
        ftr, resolve, reject = Future.resolvers()
        ftr.done(lambda v: results.append(v)).expected(lambda e: errors.append(e))
        resolve('chain')
        self.assertEqual(results, ['chain'])
        self.assertEqual(errors, [])

    def test_pending_status(self):
        ftr, _, _ = Future.resolvers()
        self.assertEqual(ftr.status, Future.PENDING)

    def test_fulfilled_status(self):
        ftr, resolve, _ = Future.resolvers()
        resolve(None)
        self.assertEqual(ftr.status, Future.FULFILLED)

    def test_rejected_status(self):
        ftr, _, reject = Future.resolvers()
        reject(None)
        self.assertEqual(ftr.status, Future.REJECTED)

    def test_executor_based_constructor(self):
        results = []
        def executor(resolve, reject):
            resolve('executed')
        ftr = Future(executor)
        ftr.done(lambda v: results.append(v))
        self.assertEqual(results, ['executed'])

    def test_multiple_done_handlers(self):
        calls = []
        ftr, resolve, _ = Future.resolvers()
        ftr.done(lambda v: calls.append('a' + str(v)))
        ftr.done(lambda v: calls.append('b' + str(v)))
        resolve(1)
        self.assertEqual(calls, ['a1', 'b1'])

    def test_multiple_expected_handlers(self):
        errors = []
        ftr, _, reject = Future.resolvers()
        ftr.expected(lambda e: errors.append('x' + str(e)))
        ftr.expected(lambda e: errors.append('y' + str(e)))
        reject('err')
        self.assertEqual(errors, ['xerr', 'yerr'])


class TestSuspendableTask(unittest.TestCase):
    def test_call_once_advances_one_step(self):
        results = []
        def gen_func():
            results.append(1)
            yield
            results.append(2)

        task = SuspendableTask(gen_func)
        self.assertFalse(task.finished)

        task.callOnce()
        self.assertEqual(results, [1])

        task.callOnce()
        self.assertEqual(results, [1, 2])
        self.assertTrue(task.finished)

    def test_call_once_completes_with_single_yield(self):
        """单 yield 生成器需要两次 callOnce：第一次 next()，第二次触发 StopIteration。"""
        def gen_func():
            yield
        task = SuspendableTask(gen_func)
        task.callOnce()
        self.assertFalse(task.finished)
        task.callOnce()
        self.assertTrue(task.finished)


class TestSchedulerBase(unittest.TestCase):
    def setUp(self):
        self.sched = Scheduler()

    def test_add_and_execute_task(self):
        calls = []
        self.sched.addTask('Update', lambda: calls.append(1))
        self.sched.execute('Update')
        self.assertEqual(calls, [1])

    def test_remove_all_tasks(self):
        self.sched.addTask('Update', lambda: None)
        self.sched.removeTask('Update', -1)
        self.assertEqual(len(self.sched._getTaskQueue('Update')), 0)

    def test_initial_skipped_zero(self):
        self.assertEqual(self.sched.getSkippedUpdates(), 0)



if __name__ == '__main__':
    unittest.main()