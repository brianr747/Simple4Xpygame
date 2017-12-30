"""
real_time_server.py

The RealTimeServer class holds the object that manages the server. It is embedded in a ServerProcess.

Despite the name, there are no communications handled in the class; that is the job of the ServerProcess.

This allows the server code to treat all RealTimeClients equally, whether or not they are embedded in
the server process.
"""
from __future__ import print_function

import clients.real_time_client
from common import NormalTermination
from common.event_queue import EventQueue
from common.exchange import Exchange, Balance
from common.production import Production, GetStandardProductionTemplates

class RealTimeServer(object):
    def __init__(self):
        self.MessagesOut = []
        self.MessagesIn = []
        self.LogData = []

    def SendMessage(self, msg, id_client):
        self.MessagesOut.append((id_client, msg))

    def CreateClient(self, msg):
        """
        Create an embedded client, based on a message.
        The base class always creates a RealTimeClient (which does nothing;)
        subclasses will create appropriate classes.

        :param msg: str
        :return:
        """
        obj = clients.real_time_client.RealTimeClient()
        self.AddClientStub(obj)

    def AddClientStub(self, obj):
        """
        Stub that is overridden by the ServerProcess class.
        :param obj: clients.real_time_client.RealTimeClient
        :return: None
        """
        pass

    def Process(self):
        """
        Base class just terminates the thing...
        :return:
        """
        raise NormalTermination('Dun!')

    def Log(self, msg):
        """
        Logging info
        :param msg:
        :return:
        """
        self.LogData.append(msg)


class RTS_BaseSimulation(RealTimeServer):
    """
    A base simulation class.
    """

    def __init__(self):
        super(RTS_BaseSimulation, self).__init__()
        self.ClientsToCreate = []
        self.T = -1
        self.NumPlayers = 0
        self.PlayerLookup = {}
        self.QuitTime = 1
        self.EventQueue = EventQueue()

    def StartUp(self):
        self.NumPlayers = len(self.ClientsToCreate)
        for client in self.ClientsToCreate:
            self.AddClientStub(client)
        self.EventQueue.InsertEvent(self.QuitTime, 'END_GAME')

    def Process(self):
        """
        Do processing. Only do one thing within a loop.

        :return:
        """
        if len(self.MessagesIn) > 0:
            ID, msg = self.MessagesIn.pop(0)
            self.ProcessMessage(ID, msg)
            return
        event = self.EventQueue.PopEvent(self.T)
        if event is not None:
            self.ProcessEvent(event)
            return
        self.TimeIncrement()

    def ProcessCommand(self, ID, msg):
        """
        Commands are messages preceded by '!'
        :param ID: int
        :param msg: str
        :return:
        """
        if msg == 'JOIN_PLAYER':
            if ID in self.PlayerLookup:
                self.Log('ERROR: Player already joined: {0}'.format(ID))
                return
            if len(self.PlayerLookup) >= self.NumPlayers:
                self.Log('ERROR: Attempting to join with max players {0}'.format(ID))
                return
            player_ID = len(self.PlayerLookup)
            self.PlayerLookup[ID] = player_ID
            self.Log('Player Joined: client {0} as Player {1}'.format(ID, player_ID))
            if player_ID == self.NumPlayers - 1:
                self.EventQueue.InsertEvent(-1, 'START_GAME')
            return
        self.Log('Unhandled command: !' + msg)

    def ProcessMessage(self, ID, msg):
        if msg.startswith('?'):
            self.ProcessQuery(ID, msg[1:])
            return
        if msg.startswith('!'):
            self.ProcessCommand(ID, msg[1:])
            return

        self.Log('Unparsed msg: {0} FROM {1}'.format(msg, ID))

    def ProcessQuery(self, ID, query):
        """
        Handle a query (leading ? is stripped)
        :param query:
        :return:
        """
        query = query.split('|')
        if query[0] == 'T':
            if len(query) == 3 and query[1] == 'REPEAT':
                step = int(query[2])
                event = ('?T\n{0}'.format(ID), 'REPEAT', step, self.T + step)
                self.EventQueue.InsertEvent(self.T + step, event)
            self.SendMessage('=T={0}'.format(self.T), ID)
            return
        self.Log('Unparsed Query: {0} From {1}'.format(query, ID))

    def ProcessEvent(self, event):
        self.Log('EVENT: {0}'.format(event))
        if type(event) is tuple:
            if event[1] == 'REPEAT':
                # We want to repeat the event starting at 'start', with time increment 'step'
                # We preserve the "start" time since we may be skipping time steps in
                # real time mode.
                msg, repeat, step, start = event
                new_event = (msg, 'REPEAT', step, start + step)
                self.EventQueue.InsertEvent(start + step, new_event)
                # Convert to a string message that is parsed.
                event = msg
            else:
                self.Log('Unknown event')
                return
        if event == 'START_GAME':
            self.StartSimulation()
            return
        if event == 'END_GAME':
            self.EndSimulation()
            return
        if event.startswith('?'):
            # It's a data query that was placed as an event.
            msg, ID = event[1:].split('\n')
            ID = int(ID)
            self.ProcessQuery(ID, msg)
            return
        self.Log('Unknown EVENT: ' + event)

    def StartSimulation(self):
        # Once we move T to 0, the simulation starts
        self.Log('STARTING SIMULATION')
        self.T = 0

    def EndSimulation(self):
        self.Log('FINISHED SIMULATION')
        raise NormalTermination

    def TimeIncrement(self):
        """
        End of period processing.
        By default, just increments self.T, if started (T > -1)
        :return:
        """
        if self.T > -1:
            self.T += 1


class RTS_BaseEconomicSimulation(RTS_BaseSimulation):
    def __init__(self):
        super(RTS_BaseEconomicSimulation, self).__init__()
        self.Exchanges = {}
        self.CreationInfo = []
        self.CashBalances = Balance()
        self.Production = Production()
        self.ProductionTemplate = GetStandardProductionTemplates('simplest')

    def CreateExchange(self, name, template_str):
        self.CreationInfo.append('CREATE_EXCHANGE\n{0}\n{1}'.format(name, template_str))

    def StartSimulation(self):
        super(RTS_BaseEconomicSimulation, self).StartSimulation()
        self.Production.ParseTemplate(self.ProductionTemplate)
        for cmd in self.CreationInfo:
            info = cmd.split('\n')
            if info[0] == 'CREATE_EXCHANGE':
                exchange = Exchange(template_str=info[2], cash_balance=self.CashBalances)
                exchange.Name = info[1]
                self.Exchanges[info[1]] = exchange
            if info[0] == 'INIT_BALANCE':
                player_list = range(0, self.NumPlayers+1)
                for exchange in self.Exchanges.values():
                    for commodity in exchange.Commodities.values():
                        for p in player_list:
                            commodity.Balances.SetBalance(p, 100)

    def ProcessQuery(self, ID, query):
        """

        :param ID: int
        :param query: str
        :return:
        """
        info = query.split('|')
        if info[0] == 'W':
            msg = ''
            if len(info) == 1:
                msg = '=W|' + '|'.join(self.Exchanges.keys())
            elif len(info) == 2:
                exchange_name = info[1]
                if exchange_name in self.Exchanges:
                    msg = '=W={0}|{1}'.format(exchange_name,
                                              self.Exchanges[exchange_name].Template)
                else:
                    msg = '*W ERROR: No Exchange Named {0}'.format(exchange_name)
            else:
                msg = '*W ERROR: Unsupporteded Query'
            self.SendMessage(msg, ID)
            return
        if info[0] in ('Q', 'I'):
            if len(info) < 2:
                self.SendMessage('*ERROR: Too short query = '+query, ID)
                return
            exchange_name = info[1]
            if exchange_name in self.Exchanges:
                msg = self.Exchanges[exchange_name].ProcessQuery(query, ID)
            else:
                msg = '*W ERROR: No Exchange Named {0}'.format(exchange_name)
            self.SendMessage(msg, ID)
            return
        if info[0] == 'P':
            self.SendMessage('=P=' + self.ProductionTemplate, ID)
            return
        super(RTS_BaseEconomicSimulation, self).ProcessQuery(ID, query)

    def ProcessCommand(self, ID, msg):
        if msg.startswith('O'):
            info = msg.split('|')
            if len(info) < 2:
                self.SendMessage('Command too short: !' + msg, ID)
                return
            exchange = info[1]
            if exchange not in self.Exchanges:
                self.SendMessage('Non-existent exchange: ' + exchange, ID)
                return
            messages = self.Exchanges[exchange].ProcessOrder(msg, ID)
            for ID_player, m in messages:
                self.SendMessage(m, ID_player)
            return
        if msg.startswith('P'):
            self.ProcessProductionMessage(ID, msg)
            return
        super(RTS_BaseEconomicSimulation, self).ProcessCommand(ID, msg)

    def ProcessEvent(self, event):
        if type(event) == tuple:
            if event[0] == 'PRODUCTION':
                dummy, exchange_name, technique_name, ID, amount = event
                exchange = self.Exchanges[exchange_name]
                technique = self.Production.Techniques[technique_name]
                # Return InProduction
                for k,v in technique.InProduction:
                    exchange.Commodities[k].Balances.ReleaseInProduction(ID, amount*v)
                for k,v in technique.Output:
                    exchange.Commodities[k].Balances[ID] = exchange.Commodities[k].Balances[ID] + (amount*v)
                self.SendMessage('!P|{0}|{1}|{2}'.format(exchange_name, technique_name, amount), ID)
                return
        super(RTS_BaseEconomicSimulation, self).ProcessEvent(event)




    def ProcessProductionMessage(self, ID, msg):
        info = msg.split('|')
        if len(info) < 4:
            self.SendMessage('* ERROR: Bad Production message: ' + msg, ID)
            return
        dummy, exchange_name, technique_name, amount = info[0:4]
        if exchange_name not in self.Exchanges:
            self.SendMessage('* ERROR: Exchange {0} does not exist'.format(exchange_name), ID)
            return
        exchange = self.Exchanges[exchange_name]
        if technique_name not in self.Production.Techniques:
            self.SendMessage('* ERROR: Unknown production technique: {0}'.format(technique_name), ID)
            return
        technique = self.Production[technique_name]
        try:
            amount = int(amount)
        except:
            self.SendMessage('* ERROR: Bad production amount: {0}'.format(amount), ID)
            return
        # Must meet all required inputs.
        requirements = {}
        # The trick is that we could have the same commodity both required and InProduction
        for k,v in technique.Consumed:
            requirements[k] = v
        for k,v in technique.InProduction:
            if k in requirements:
                requirements[k] += v
            else:
                requirements[k] = v
        # Now check
        for k,v in requirements.items():
            if amount*v > exchange.GetInventory(k, ID):
                self.SendMessage('*ERROR: Insufficient {0} FOR PRODUCTION'.format(k), ID)
                return
        # Now, do the work
        for k,v in technique.Consumed:
            exchange.Commodities[k].Balances.Consume(ID, amount*v)
        for k, v in technique.InProduction:
            exchange.Commodities[k].Balances.MoveToInProduction(ID, amount*v)
        self.EventQueue.InsertEvent(self.T + technique.Time, ('PRODUCTION', exchange_name, technique_name, ID, amount))














