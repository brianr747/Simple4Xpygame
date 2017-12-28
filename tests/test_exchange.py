from unittest import TestCase
from common.exchange import *

class TestCashBalances(TestCase):
    def test___init__(self):
        c = Balance()
        self.assertEqual(0, len(c.PlayerBalances))

    def test_transfer(self):
        c = Balance()
        c.SetBalance(1, 20)
        c[2] = 30
        c.Transfer(1, 2, 10)
        self.assertEqual(10, c[1])
        self.assertEqual(40, c[2])


class TestExchange(TestCase):
    def test_initialise(self):
        obj = Exchange()
        self.assertEqual(0, len(obj.Commodities))
