# coding=utf-8
"""Test StateTree search algorithm, context inheritance, and copy."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from architect.fsm.stateTree.common import StateTree, StateNode, nodePathStr


class _TestNode(StateNode):
    """Custom node with controllable canEnter/canExit."""
    def __init__(self, name='unknown', enter=True, exit_=True):
        StateNode.__init__(self, name)
        self._can_enter = enter
        self._can_exit = exit_
        self._entered = False
        self._exited = False
        self._updated = 0

    def canEnter(self, tree):
        return self._can_enter

    def canExit(self, tree):
        return self._can_exit

    def enter(self, previous, tree):
        self._entered = True

    def exit(self, nextNode, tree):
        self._exited = True

    def update(self, tree):
        self._updated += 1


class TestStateTreeSearch(unittest.TestCase):
    def setUp(self):
        self.tree = StateTree('test_entity')

    def test_initial_search_finds_first_leaf(self):
        root = self.tree.getRoot()
        idle = _TestNode('idle')
        walk = _TestNode('walk')
        root.addChildren(idle, walk)

        self.tree.finishTasks()
        self.tree.execute()

        self.assertEqual(self.tree.currentStateName(), 'idle')

    def test_guard_blocks_subtree(self):
        root = self.tree.getRoot()
        ground = _TestNode('ground', enter=False)  # 不可进入
        idle = _TestNode('idle')
        ground.addChildren(idle)
        root.addChildren(ground)

        self.tree.finishTasks()
        self.tree.execute()

        self.assertIsNone(self.tree.currentState())

    def test_can_exit_false_locks_state(self):
        root = self.tree.getRoot()
        locked = _TestNode('locked', exit_=False)  # 不可退出
        other = _TestNode('other')
        root.addChildren(locked, other)

        self.tree.switchNode(locked)
        self.tree.finishTasks()
        self.tree.execute()

        # 仍停留在 locked
        self.assertEqual(self.tree.currentStateName(), 'locked')

    def test_finish_tasks_then_search_next(self):
        root = self.tree.getRoot()
        a = _TestNode('a')
        b = _TestNode('b')
        root.addChildren(a, b)

        self.tree.switchNode(a)
        a._can_enter = False  # a 不再可进入
        a._can_enter = False  # won't be re-entered
        self.tree.finishTasks()
        self.tree.execute()

        self.assertEqual(self.tree.currentStateName(), 'b')

    def test_upward_search_to_sibling_subtree(self):
        root = self.tree.getRoot()
        group_a = _TestNode('group_a', enter=False)  # 跳过
        group_b = _TestNode('group_b')
        leaf_b = _TestNode('leaf_b')
        group_b.addChildren(leaf_b)
        leaf_a = _TestNode('leaf_a')
        group_a.addChildren(leaf_a)
        root.addChildren(group_a, group_b)

        self.tree.switchNode(leaf_a)
        self.tree.finishTasks()
        self.tree.execute()

        self.assertEqual(self.tree.currentStateName(), 'leaf_b')

    def test_enter_exit_hooks_called(self):
        root = self.tree.getRoot()
        a = _TestNode('a')
        b = _TestNode('b')
        root.addChildren(a, b)

        self.tree.switchNode(a)
        self.tree.finishTasks()
        self.tree.execute()

        self.assertTrue(a._exited)
        self.assertTrue(b._entered)

    def test_state_ticks_reset_on_switch(self):
        root = self.tree.getRoot()
        a = _TestNode('a')
        b = _TestNode('b')
        root.addChildren(a, b)

        self.tree.switchNode(a)
        # 手动推进几帧
        for _ in range(5):
            self.tree.execute()
        self.assertEqual(self.tree.stateTicks, 5)

        self.tree.finishTasks()
        self.tree.execute()
        self.assertEqual(self.tree.stateTicks, 0)

    def test_update_called_on_activated_path(self):
        root = self.tree.getRoot()
        parent = _TestNode('parent')
        child = _TestNode('child')
        parent.addChildren(child)
        root.addChildren(parent)

        self.tree.switchNode(child)
        self.tree.execute()

        self.assertGreater(parent._updated, 0)
        self.assertGreater(child._updated, 0)

    def test_search_node_returns_none_when_not_finished(self):
        root = self.tree.getRoot()
        a = _TestNode('a')
        root.addChildren(a)

        self.tree.switchNode(a)
        # 未调用 finishTasks
        result = self.tree.searchNode()
        self.assertIsNone(result)


class TestStateTreeContext(unittest.TestCase):
    def setUp(self):
        self.tree = StateTree('test_entity')

    def test_child_inherits_parent_context(self):
        parent = StateNode('parent')
        parent.setContext('damage', 50)
        child = StateNode('child')
        parent.addChildren(child)

        self.assertEqual(child.getContext('damage'), 50)

    def test_child_override_parent_context(self):
        parent = StateNode('parent')
        parent.setContext('damage', 50)
        child = StateNode('child')
        parent.addChildren(child)
        child.setContext('damage', 100)

        self.assertEqual(child.getContext('damage'), 100)
        self.assertEqual(parent.getContext('damage'), 50)

    def test_context_not_found_returns_none(self):
        node = StateNode('orphan')
        self.assertIsNone(node.getContext('nonexistent'))


class TestStateTreeCopy(unittest.TestCase):
    def setUp(self):
        self.tree = StateTree('test_entity')

    def test_deep_copy_creates_independent_tree(self):
        original = _TestNode('template')
        original.setContext('damage', 50)
        child = _TestNode('child')
        original.addChildren(child)

        clone = original.copy(deep=True)

        self.assertIsNone(clone._parent)
        self.assertEqual(len(clone.children), 1)
        self.assertEqual(clone.children[0].name, 'child')
        self.assertEqual(clone.getContext('damage'), 50)
        self.assertIsNot(clone.children[0], child)

    def test_shallow_copy_no_children(self):
        original = _TestNode('template')
        original.addChildren(_TestNode('child'))

        clone = original.copy(deep=False)

        self.assertEqual(len(clone.children), 0)

    def test_copy_preserves_custom_attributes(self):
        original = _TestNode('custom', enter=False, exit_=False)
        clone = original.copy(deep=True)

        self.assertFalse(clone._can_enter)
        self.assertFalse(clone._can_exit)


class TestFindAllActivatedNodes(unittest.TestCase):
    def setUp(self):
        self.tree = StateTree('test_entity')

    def test_returns_path_from_root_to_leaf(self):
        root = self.tree.getRoot()
        parent = StateNode('parent')
        child = StateNode('child')
        parent.addChildren(child)
        root.addChildren(parent)

        self.tree.switchNode(child)
        nodes = self.tree.findAllActivatedStateNodes()
        names = [n.name for n in nodes]

        self.assertEqual(names, ['root', 'parent', 'child'])


if __name__ == '__main__':
    unittest.main()