from unittest import TestCase
from common.production import *


class TestProduction(TestCase):
    def test_StandardProductionTemplates(self):
        with self.assertRaises(ValueError):
            GetStandardProductionTemplates('bad')
        out = GetStandardProductionTemplates('test')
        info = out.split('|')
        self.assertEqual(3, len(info))

    def test_ParseTemplate1(self):
        template = GetStandardProductionTemplates('test')
        prod = Production()
        prod.ParseTemplate(template)
        self.assertEqual(3, len(prod.Techniques))
        self.assertIn('P0', prod.Techniques)
        self.assertIn('P1', prod.Techniques)
        self.assertIn('P2', prod.Techniques)
        tech = prod.Techniques['P0']
        self.assertEqual('Goods Production', tech.Description)
        self.assertEqual([], tech.Consumed)
        self.assertEqual([('Capital', 1)], tech.InProduction)
        self.assertEqual([('Goods', 1)], tech.Output)
        self.assertEqual(5, tech.Time)

