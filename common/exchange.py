"""
exchange.py

Implements an exchange (with multiple commodities).

"""

class AccountingError(ValueError):
    pass

class Balance(object):
    """
    Handle commodity (and cash) balances.
    In addition to the unemcumbered balance, have a separate "held" balance, which is
    inventory that is tied to a sell order. The exchange will reject sell orders that cannot be covered
    by moving the unemcumbered balance to "held".

    Eventually, we will probably add a category for inventory that is tied up in production.
    """
    def __init__(self):
        self.PlayerBalances = {}
        self.HeldBalances = {}
        # Can make this a float if desired.
        self.DefaultZero = 0
        self.EnforcePositive = False

    def SetBalance(self, ID, val):
        self.PlayerBalances[ID] = val

    def __setitem__(self, ID, val):
        self.PlayerBalances[ID] = val

    def __getitem__(self, ID):
        return self.PlayerBalances.get(ID, self.DefaultZero)

    def GetHeld(self, ID):
        return self.HeldBalances.get(ID, self.DefaultZero)

    def MoveHeld(self, ID, amount):
        """

        :param ID: int
        :param amount: int
        :return:
        """
        if amount <= 0:
            return
        if amount > self.__getitem__(ID):
            raise AccountingError('Not enough held items in inventory')
        self.PlayerBalances[ID] -= amount
        init = self.GetHeld(ID)
        self.HeldBalances[ID] = init + amount

    def ReleaseHeld(self, ID, amount):
        if amount <= 0:
            return
        if amount > self.GetHeld(ID):
            raise AccountingError('Attempting to release more items than are held')
        self.HeldBalances[ID] -= amount
        self.PlayerBalances[ID] = self.PlayerBalances.get(ID, self.DefaultZero) + amount

    def ExchangeTransfer(self, ID_from, ID_to, amount):
        """
        Do the exchange operations, transferring from held inventory

        :param ID_from: int
        :param ID_to: int
        :param amount: int
        :return:
        """
        if amount == 0:
            return
        if amount > self.GetHeld(ID_from):
            raise AccountingError('Did not have enough held inventory')
        self.HeldBalances[ID_from] -= amount
        self.PlayerBalances[ID_to] = self.PlayerBalances.get(ID_to, self.DefaultZero) + amount

    def Transfer(self, ID_from, ID_to, amount):
        if amount == 0:
            return
        if amount < 0:
            raise ValueError("Transfer amount must be positive")
        if self.EnforcePositive and (amount > self[ID_from]):
            raise AccountingError('Negative holding after transfer not allowed')
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
                # Need to release held inventory
                # Pop out the existing order; insert an event to release inventory
                self.Events.append((order.ID_Player, order.ID_Player, order.Amount, 0))
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

    def GetInfo(self, option):
        """
        Return order info as a ";"-delimited string
        :return: str
        """
        def formatter(order):
            return "{0},{1},{2}".format(order.Price, order.Amount, order.ID_Player)
        if option == 'ALL':
            out = [formatter(x) for x in self.Queue]
            return ";".join(out)
        if option == 'BEST':
            if len(self.Queue) == 0:
                return 'None@$None'
            best = self.Queue[0].Price
            amount = 0
            for order in self.Queue:
                if not order.Price == best:
                    break
                amount += order.Amount
            return "{0}@${1}".format(amount, best)


class ClientPricingInformation(object):
    """
    ClientPricingInformation: Holds commodity pricing information for clients.
    Not used by server [unless we want to track changes...]
    """
    def __init__(self):
        self.BestBid = None
        self.BestOffer = None
        self.BestBidSize = None
        self.BestOfferSize = None

class Commodity(object):
    def __init__(self, name=''):
        self.Name = name
        self.Balances = Balance()
        self.Balances.EnforcePositive = True
        self.BuyQueue = OrderQueue(is_buy=True)
        self.SellQueue = OrderQueue(is_buy=False)
        self.ClientPricingInformation = ClientPricingInformation()

    def GetInfo(self, option):
        return 'BUY;{0}|SELL;{1}'.format(self.BuyQueue.GetInfo(option), self.SellQueue.GetInfo(option))


    def ProcessOrder(self, order):
        """
        Process order, returning a list of transactions of the form:
        [(buyer_ID, seller_ID, amount, unit_price), ...]
        :param order: Order
        :return: list
        """
        # If the amount is zero, do not waste time.
        if order.Amount <= 0:
            return []
        if order.IsBuy:
            cross_queue = self.SellQueue
            queue = self.BuyQueue
        else:
            # We need to hold inventory before we start processing.
            ID = order.ID_Player
            self.Balances.MoveHeld(ID,order.Amount)
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
        # Inventory query
        if info[0] == 'I':
            # Give the entire inventory for a player.
            out = []
            if len(info) < 2:
                return '* ERROR: too short inventory query'
            for c in self.Commodities:
                commodity = self.Commodities[c]
                amount = commodity.Balances[query_ID]
                held = commodity.Balances.GetHeld(query_ID)
                if not (amount, held) == (0, 0):
                    out.append('{0};{1};{2}'.format(c, amount, held))
            msg = '=I|{0}|{1}'.format(info[1], '|'.join(out))
            return msg
        if len(info) < 3:
            return '* ERROR: Unknown query format'
        commodity_name = info[2]
        if commodity_name not in self.Commodities:
            return '* ERROR: Unknown commodity: ' + commodity_name
        commodity = self.Commodities[commodity_name]
        if len(info) > 3:
            option = info[3]
        else:
            option = 'ALL'
        out = '=Q|{0}|{1}|{2}'.format(info[1], info[2], commodity.GetInfo(option))
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
        try:
            events = commodity.ProcessOrder(order)
        except AccountingError as ex:
            msg = ex.args[0]
            return [(order_ID, msg)]
        out = []
        for buy, sell, amount, price in events:
            if buy == sell:
                # Event of transfer between the same player = release inventory from "held"
                commodity.Balances.ReleaseHeld(buy, amount)
                continue
            try:
                # If the "held" information is coherent, this should not fail.
                commodity.Balances.ExchangeTransfer(sell, buy, amount)
            except AccountingError:
                raise ValueError('Transfer failed; Held information might be incoherent')
            self.CashBalance.Transfer(buy, sell, amount*price)
            out.append((buy, '=BOUGHT|{0}|{1}|{2}|{3}'.format(exchange, commodity_name, amount, price)))
            out.append((sell, '=SOLD|{0}|{1}|{2}|{3}'.format(exchange, commodity_name, amount, price)))
        return out





