"""
production.py

Handles production function management.

Within a simulation, there are a list of production techniques that can be chosen from.

Until we have have a labour market, each technique is fixed, and creates new commodities from
existing commodities, and with a fixed time interval to conpletion.

Before production, must all have all the requirement commodities in inventory.

Requirements (inputs) are of two types.
- Consumed: the input commodities disappear (immediately).
- InProduction: The commodities are marked as "InProduction", and they are no longer accessible. They are freed
up when the production process is finished. They will still incur maintenance costs.

Since capital that is InProduction is not accessible, we cannot immediately deal with a firm that is overextended.
Liquidation will have to occur after the production process is finished.

Each technique has a completion time; the finish is marked by an event.

The server will implement the actual rules. This class takes the production techniques that are saved as
strings, and parses them to get the information. The server will relay the production string information to the
clients.

For now, we will relay on fixed production functions that are saved within this file. Later on, the production
functions will be text data that are more easily changed.


Template string format:
'{technique #1}|{technique #2}|...'

Each technique is specified by:
'consumed;InProduction;outputs;Time;Name'
where Name = the full name of the technique,
and for nosumed,InProduction, and outputs, they are given by:
'NxCOMMODITY1,MxCOMMODITY2, ...'

"""


class Technique(object):
    def __init__(self):
        self.Consumed = []
        self.InProduction = []
        self.Output = []
        self.Description = ''
        self.Time = 0


class Production(object):
    def __init__(self):
        self.Template = ''
        self.Techniques = {}

    def __getitem__(self, item):
        """
        Get the technique; throws a KeyError if non-existent
        :param item: str
        :return: Technique
        """
        return self.Techniques[item]

    def ParseTemplate(self, template):
        """

        :param template: str
        :return:
        """
        self.Techniques = {}
        info = template.split('|')
        cnt = 0
        for row in info:
            name = 'P{0}'.format(cnt)
            cnt += 1
            tech = Technique()
            self.Techniques[name] = tech
            consumed, inproduction, output, t, desc = row.split(';')
            tech.Description = desc
            tech.Time = int(t)
            tech.Consumed = self.ParseCommodityList(consumed)
            tech.InProduction = self.ParseCommodityList(inproduction)
            tech.Output = self.ParseCommodityList(output)

    def ParseCommodityList(self, txt):
        if len(txt) == 0:
            return []
        info = txt.split(',')
        out = []
        for entry in info:
            pos = entry.find('x')
            amount = int(entry[0:pos])
            out.append((entry[(pos+1):], amount))
        return out


def GetStandardProductionTemplates(name):
    if name == 'test':
        # Do not change this; used in unit tests.
        out = [
            ';1xCapital;1xGoods;5;Goods Production',
            '5xGoods;2xCapital;1xCapital;20;Capital Production',
            '1xCapital;;3xGoods;5;Scrap Capital'
        ]
        return '|'.join(out)
    if name == 'simplest':
        # Do not change this; used in unit tests.
        out = [
            ';1xCapital;1xGoods;5;Goods Production',
            '5xGoods;2xCapital;1xCapital;20;Capital Production',
            '1xCapital;;3xGoods;5;Scrap Capital'
        ]
        return '|'.join(out)
    raise ValueError('Unknown Template')




