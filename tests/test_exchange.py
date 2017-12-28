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

class TestOrderQueue(TestCase):
    def test_isbetter(self):
        ord1 = Order(is_buy=True, price=10, amount=10, ID_player=1)
        ord2 = Order(is_buy=True, price=20, amount=10, ID_player=1)
        self.assertTrue(ord2.IsBetter(ord1))
        self.assertFalse(ord1.IsBetter(ord2))
        ord3 = Order(is_buy=False, price=10, amount=10, ID_player=1)
        ord4 = Order(is_buy=False, price=20, amount=10, ID_player=1)
        self.assertTrue(ord3.IsBetter(ord4))
        self.assertFalse(ord4.IsBetter(ord3))

    def test_insertfail(self):
        ord = Order(is_buy=True)
        queue = OrderQueue(is_buy=False)
        with self.assertRaises(ValueError):
            queue.InsertOrder(ord)

    def test_insert(self):
        queue = OrderQueue(is_buy=True)
        ord1 = Order(is_buy=True, price=10, amount=5)
        ord2 = Order(is_buy=True, price=10, amount=5)
        ord3 = Order(is_buy=True, price=20, amount=5)
        queue.InsertOrder(ord1)
        queue.InsertOrder(ord2)
        queue.InsertOrder(ord3)
        self.assertEqual([ord3, ord1, ord2], queue.Queue)
        queue = OrderQueue(is_buy=True)
        queue.InsertOrder(ord3)
        queue.InsertOrder(ord2)
        self.assertEqual([ord3, ord2], queue.Queue)
        queue.InsertOrder(ord1)
        self.assertEqual([ord3, ord2, ord1], queue.Queue)

class TestCommodity(TestCase):
    def test_process_order_1(self):
        commodity = Commodity()
        order = Order(is_buy=True, price=10, amount=10)
        commodity.ProcessOrder(order)
        self.assertEqual(1, len(commodity.BuyQueue))
        self.assertEqual(0, len(commodity.SellQueue))
        ord2 = Order(is_buy=False, price=20, amount=10)
        commodity.ProcessOrder(ord2)
        self.assertEqual(1, len(commodity.BuyQueue))
        self.assertEqual(1, len(commodity.SellQueue))

    def test_crossing_1(self):
        # first test: see if we blow out an existing order from the same player
        commodity = Commodity()
        ord_b = Order(is_buy=True, price=10, amount=10, ID_player=1)
        commodity.ProcessOrder(ord_b)
        self.assertEqual(1, len(commodity.BuyQueue))
        ord_s = Order(is_buy=False, price=10, amount=10, ID_player=1)
        commodity.ProcessOrder(ord_s)
        self.assertEqual(0, len(commodity.BuyQueue))
        self.assertEqual(1, len(commodity.SellQueue))

    def test_crossing_2(self):
        # second test: cross two orders completely
        commodity = Commodity()
        ord_b = Order(is_buy=True, price=10, amount=20, ID_player=1)
        commodity.ProcessOrder(ord_b)
        self.assertEqual(1, len(commodity.BuyQueue))
        ord_s = Order(is_buy=False, price=10, amount=20, ID_player=2)
        commodity.ProcessOrder(ord_s)
        self.assertEqual(0, len(commodity.BuyQueue))
        self.assertEqual(0, len(commodity.SellQueue))
        # (buy, sell, amount, price
        self.assertEqual([(1, 2, 20, 10)], commodity.BuyQueue.Events)

    def test_crossing_2(self):
        # second test: fill one order completely, leave the other partially filled
        commodity = Commodity()
        ord_s1 = Order(is_buy=False, price=10, amount=20, ID_player=1)
        commodity.ProcessOrder(ord_s1)
        ord_s2 = Order(is_buy=False, price=12, amount=20, ID_player=2)
        commodity.ProcessOrder(ord_s2)
        self.assertEqual(2, len(commodity.SellQueue))
        ord_b = Order(is_buy=True, price=30, amount=30, ID_player=3)
        commodity.ProcessOrder(ord_b)
        self.assertEqual(0, len(commodity.BuyQueue))
        self.assertEqual(1, len(commodity.SellQueue))
        # (buy, sell, amount, price
        self.assertEqual([(3, 1, 20, 10), (3, 2, 10, 12)], commodity.SellQueue.Events)


