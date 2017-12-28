"""
exchange.py

Implements an exchange (with multiple commodities).

"""


class Balance(object):
    def __init__(self):
        self.PlayerBalances = {}
        # Can make this a float if desired.
        self.DefaultZero = 0
        self.EnforcePositive = False

    def SetBalance(self, ID, val):
        self.PlayerBalances[ID] = val

    def __setitem__(self, ID, val):
        self.PlayerBalances[ID] = val

    def __getitem__(self, ID):
        if ID not in self.PlayerBalances:
            return self.DefaultZero
        else:
            return self.PlayerBalances[ID]

    def Transfer(self, ID_from, ID_to, amount):
        if amount == 0:
            return
        if amount < 0:
            raise ValueError("Transfer amount must be positive")
        if self.EnforcePositive and (amount > self[ID_from]):
            raise ValueError('Negative holding after transfer not allowed')
        self.PlayerBalances[ID_from] = self[ID_from] - amount
        self.PlayerBalances[ID_to] = self[ID_to] + amount

class Order(object):
    def __init__(self, is_buy=True, price=0, amount=0, ID_player=-1):
        self.IsBuy = is_buy
        self.Price = price
        self.Amount = amount
        self.ID_Player = ID_player

    def IsBetter(self, other):
        """
        Is this a better order?
        Note that ties do not count as "better", so the relationship is not transitive...
        :param other: Order
        :return:
        """
        if self.IsBuy:
            return self.Price > other.Price
        else:
            return self.Price < other.Price

    def CanCross(self, other):
        """
        Can these two orders transact against each other?
        (No sanity checks.)
        :param other: Order
        :return:
        """
        if self.IsBuy:
            return self.Price >= other.Price
        else:
            return self.Price <= other.Price


class OrderQueue(object):
    """
    A queue of either buy or sell orders
    """
    def __init__(self, is_buy=True):
        self.IsBuy = is_buy
        self.Queue = []
        self.Events = []

    def __len__(self):
        return len(self.Queue)

    def CrossOrder(self, order):
        """
        Run an order against the queue, generating events to be processed.
        If the order is filled, returns None, otherwise returns the order with the amount reduced
        by any fills.
        Note: if the ID_player matches an order it is matched against, we pop that order out, and keep
        going.
        :param order: Order
        :return: Order
        """
        # We could delete this check for efficiency
        if self.IsBuy == order.IsBuy:
            raise ValueError('Crossed against incorrect queue!')
        self.Events = []
        while len(self.Queue) > 0:
            other = self.Queue[0]
            if not order.CanCross(other):
                break
            if other.ID_Player == order.ID_Player:
                # Pop out the existing order; no transaction ('event') takes place
                self.Queue.pop(0)
                continue
            # We got a transaction!
            amount = min(order.Amount, other.Amount)
            # Event = (buyer, seller, amount, unit_price)
            if self.IsBuy:
                self.Events.append((other.ID_Player, order.ID_Player, amount, other.Price))
            else:
                self.Events.append((order.ID_Player, other.ID_Player, amount, other.Price))
            other.Amount -= amount
            # Existing order is cleared
            if other.Amount == 0:
                self.Queue.pop(0)
            order.Amount -= amount
            # Check whether we filled the order completely
            if order.Amount == 0:
                return None
        if order.Amount > 0:
            return order
        else:
            return None

    def InsertOrder(self, order):
        """
        Insert a new order. Assumes that we have crossed transactions first
        :param order: Order
        :return:
        """
        if not self.IsBuy == order.IsBuy:
            raise ValueError('Order Mismatch')
        for pos in range(0, len(self.Queue)):
            if order.IsBetter(self.Queue[pos]):
                self.Queue.insert(pos, order)
                return
        self.Queue.append(order)


class Commodity(object):
    def __init__(self, name=''):
        self.Name = name
        self.Balances = Balance()
        self.Balances.EnforcePositive = True
        self.BuyQueue = OrderQueue(is_buy=True)
        self.SellQueue = OrderQueue(is_buy=False)


    def GetInfo(self):
        return '{0}|{1}'.format(len(self.BuyQueue), len(self.SellQueue))

    def ProcessOrder(self, order):
        """
        Process order, returning a list of transactions of the form:
        [(buyer_ID, seller_ID, amount, unit_price), ...]
        :param order: Order
        :return: list
        """
        if order.IsBuy:
            cross_queue = self.SellQueue
            queue = self.BuyQueue
        else:
            cross_queue = self.BuyQueue
            queue = self.SellQueue
        order = cross_queue.CrossOrder(order)
        # Process events...
        if order is not None:
            queue.InsertOrder(order)
        return cross_queue.Events


class Exchange(object):
    def __init__(self, template_str='', cash_balance=None):
        """
        Create an exchange
        :param template_str: str
        :param cash_balance: Balance
        """
        self.Template = template_str
        self.Commodities = {}
        self.CashBalance = Balance()
        self.Name = 'Exchange'
        if cash_balance is not None:
            self.CashBalance = cash_balance
        if not template_str == '':
            self.ParseTemplate(template_str=template_str)

    def ParseTemplate(self, template_str):
        """
        Reset the commodity list based on a template string
        :param template_str: str
        :return:
        """
        self.Commodities = {}
        self.Template = template_str
        c_list = template_str.split('|')
        for c in c_list:
            c = c.strip()
            if len(c) > 0:
                self.Commodities[c] = Commodity(c)

    def ProcessQuery(self, query_str, query_ID):
        """
        Query format:
        '?Q|Exchange|Commodity'
        (Currently does not care about the ID of the query agent.
        :param query_str: str
        :param query_ID: int
        :return: str
        """
        info = query_str.split('|')
        if not len(info) == 3:
            return '* ERROR: Unknown query format'
        commodity_name = info[2]
        if commodity_name not in self.Commodities:
            return '* ERROR: Unknown commodity: ' + commodity_name
        commodity = self.Commodities[commodity_name]
        out = '=Q|{0}|{1}|{2}'.format(info[1], info[2], commodity.GetInfo())
        return out



    def ProcessOrder(self, order_str, order_ID):
        """
        Process a buy/sell order that comes in as a string.
        Returns a list of messages to be relayed
         [ (ID_player, message), ...]

         Format:
         '!|<Exchange>|<commodity>|<B/S>|amount|price'
        :param order_str: str
        :return: list
        """
        info = order_str.split('|')
        if not len(info) == 6:
            return [(order_ID, '* ERROR: Bad exchange order')]
        dummy1, exchange, commodity_name, buy_sell, amount, price = info
        if commodity_name not in self.Commodities:
            return [(order_ID, '* ERROR: Unknown commodity: ' + commodity_name)]
        if buy_sell not in ('B', 'S'):
            return [(order_ID, '* ERROR: NOT B or S: ' + buy_sell)]
        is_buy = buy_sell == 'B'
        try:
            amount = int(amount)
            price = int(price)
        except:
            return [(order_ID, '* ERROR: Invalid amount or price')]
        order = Order(is_buy, amount=amount, price=price, ID_player=order_ID)
        commodity = self.Commodities[commodity_name]
        events = commodity.ProcessOrder(order)
        out = []
        for buy, sell, amount, price in events:
            commodity.Balances.Transfer(sell, buy, amount)
            self.CashBalance.Transfer(buy, sell, amount*price)
            out.append((buy, '=BOUGHT|{0}|{1}|{2}|{3}'.format(exchange, commodity_name, amount, price)))
            out.append((sell, '=SOLD|{0}|{1}|{2}|{3}'.format(exchange, commodity_name, amount, price)))
        return out





