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
        if self.EnforcePositive and (amount > self.PlayerBalances[ID_from]):
            raise ValueError('Negative holding after transfer not allowed')
        self.PlayerBalances[ID_from] = self[ID_from] - amount
        self.PlayerBalances[ID_to] = self[ID_to] + amount


class Commodity(object):
    def __init__(self, name=''):
        self.Name = name
        self.Balances = Balance()
        self.Balances.EnforcePositive = True


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
        if cash_balance is not None:
            self.CashBalance = cash_balance

    def ParseTemplate(self, template_str):
        """
        Reset the commodity list based on a template string
        :param template_str: str
        :return:
        """
        self.Commodities = {}
        c_list = template_str.split('|')
        for c in c_list:
            c = c.strip()
            if len(c) > 0:
                self.Commodities[c] = Commodity(c)



