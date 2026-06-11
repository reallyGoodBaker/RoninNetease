# coding=utf-8
"""Test FieldSchema and initComponentFields."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mocks; mocks.install()
from architect.component.schema import FieldSchema, defineFields, initComponentFields


@defineFields(
    health=FieldSchema(default=100, validator=lambda v: 0 <= v <= 1000),
    name=FieldSchema(default='unnamed'),
)
class TestComp(object):
    pass


class TestFieldSchema(unittest.TestCase):
    def test_default_values_set(self):
        comp = TestComp()
        initComponentFields(comp, TestComp, 'entity-1')
        self.assertEqual(comp.health, 100)
        self.assertEqual(comp.name, 'unnamed')

    def test_existing_values_preserved(self):
        comp = TestComp()
        comp.health = 50
        initComponentFields(comp, TestComp, 'entity-1')
        self.assertEqual(comp.health, 50)

    def test_validator_passes(self):
        comp = TestComp()
        comp.health = 500
        initComponentFields(comp, TestComp, 'entity-1')
        self.assertEqual(comp.health, 500)

    def test_validator_fails(self):
        comp = TestComp()
        comp.health = 2000
        with self.assertRaises(ValueError):
            initComponentFields(comp, TestComp, 'entity-1')

    def test_no_schema_class_unchanged(self):
        class PlainComp(object):
            pass
        comp = PlainComp()
        initComponentFields(comp, PlainComp, 'entity-1')
        self.assertFalse(hasattr(comp, 'health'))


if __name__ == '__main__':
    unittest.main()