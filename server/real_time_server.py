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
from common.event_queue import EventQueue, Event
from common.exchange import Exchange, Balance, AccountingError
from common.production import Production, GetStandardProductionTemplates
from common.protocols import Protocol, ProtocolError, UnsupportedMessage

class RealTimeServer(object):
    def __init__(self):
        self.MessagesOut = []
        self.MessagesIn = []
        self.LogData = []
        self.Protocol = Protocol()

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
        self.SetHandlers()

    def SetHandlers(self):
        """
        If we change the Protocol, call this before starting to receive messages.
        :return:
        """
        self.Protocol.Handlers['?T'] = self.HandlerQueryT
        self.Protocol.Handlers['!JOIN_PLAYER'] = self.HandlerJoinPlayer

    def StartUp(self):
        self.NumPlayers = len(self.ClientsToCreate)
        for client in self.ClientsToCreate:
            self.AddClientStub(client)
        event = Event(callback=self.EndSimulation, txt='End Simlation')
        self.EventQueue.InsertEvent(self.QuitTime, event)

    def Process(self):
        """
        Do processing. Only do one thing within a loop.

        :return:
        """
        if len(self.MessagesIn) > 0:
            ID, msg = self.MessagesIn.pop(0)
            processed = False
            try:
                self.Protocol.HandleMessage(msg, ID)
                return
            except UnsupportedMessage:
                pass
            except ProtocolError as ex:
                self.SendMessage('ERROR: ' + ex.args[0] + ' in: ' +msg, ID)
                return
            # Fall through to the deprecated function...
            print('Deprecated message type:' + msg)
            self.ProcessMessage(ID, msg)
            return
        event = self.EventQueue.PopEvent(self.T)
        if type(event) == Event:
            event.Evaluate()
            return
        if event is not None:
            self.Log('Non-Event object event: {0}'.format(event))
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
        self.Log('Unhandled command: !' + msg)

    def ProcessMessage(self, ID, msg):
        """
        Deprecated
        :param ID:
        :param msg:
        :return:
        """
        print('Deprecated message: ' + msg)
        if msg.startswith('?'):
            self.ProcessQuery(ID, msg[1:])
            return
        if msg.startswith('!'):
            self.ProcessCommand(ID, msg[1:])
            return

        self.Log('Unparsed msg: {0} FROM {1}'.format(msg, ID))

    def ProcessQuery(self, ID, query):
        """
        Deprecated

        Handle a query (leading ? is stripped)
        :param query:
        :return:
        """
        self.Log('Unparsed Query: {0} From {1}'.format(query, ID))

    def ProcessEvent(self, event):
        """
        Deprecated function; now handled as callbacks in the Event class
        :param event:
        :return:
        """
        self.Log('Unknown EVENT: ' + event)

    def HandlerQueryT(self, ID, repeat, step):
        msg = self.Protocol.BuildMessage('=T', self.T)
        self.SendMessage(msg, ID)
        if repeat:
            event = Event(callback=self.EventSendTime, kwargs={'ID': ID},
                      txt='Send time to {0}'.format(ID), repeat=step, start_repeat=self.T + step)
            # event = ('?T\n{0}'.format(ID), 'REPEAT', step, self.T + step)
            self.EventQueue.InsertEvent(self.T + step, event)

    def HandlerJoinPlayer(self, ID):
        if ID in self.PlayerLookup:
            self.Log('ERROR: Player already joined: {0}'.format(ID))
            raise ProtocolError('Already Joined')
        if len(self.PlayerLookup) >= self.NumPlayers:
            self.Log('ERROR: Attempting to join with max players {0}'.format(ID))
            raise ProtocolError('Error: Already at max players')
        player_ID = len(self.PlayerLookup)
        self.PlayerLookup[ID] = player_ID
        self.Log('Player Joined: client {0} as Player {1}'.format(ID, player_ID))
        if player_ID == self.NumPlayers - 1:
            event = Event(callback=self.EventStartSimulation, txt='START_SIMULATION')
            self.EventQueue.InsertEvent(-1, event)

    def EventSendTime(self, ID):
        """
        Send a time axis message to an ID; calls HandlerQueryT
        :param ID: int
        :return:
        """
        self.HandlerQueryT(ID, repeat=False, step=0)

    def EventStartSimulation(self):
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

    def SetHandlers(self):
        super(RTS_BaseEconomicSimulation, self).SetHandlers()
        self.Protocol.Handlers['?W'] = self.HandlerQueryW
        self.Protocol.Handlers['?W1'] = self.HandlerQueryW1
        self.Protocol.Handlers['!P'] = self.HandlerProduction
        self.Protocol.Handlers['!O'] = self.HandlerOrder
        self.Protocol.Handlers['?Q'] = self.HandlerQueryQ
        self.Protocol.Handlers['?C'] = self.HandlerQueryC
        self.Protocol.Handlers['!O_REMOVE'] = self.HandlerRemoveOrder

    def CreateExchange(self, name, template_str):
        self.CreationInfo.append('CREATE_EXCHANGE\n{0}\n{1}'.format(name, template_str))

    def EventStartSimulation(self):
        super(RTS_BaseEconomicSimulation, self).EventStartSimulation()
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

    def HandlerQueryW(self, ID):
        vals = self.Exchanges.keys()
        msg = self.Protocol.BuildMessage('=W', vals)
        self.SendMessage(msg, ID)

    def HandlerQueryW1(self, ID, exchange):
        if exchange not in self.Exchanges:
            raise ProtocolError('Unknown exchange = ' + exchange)
        msg = self.Protocol.BuildMessage('=W1', exchange, self.Exchanges[exchange].Template.split(';'))
        self.SendMessage(msg, ID)

    def GetExchange(self, exchange):
        """
        Throws a ProtocolError if the exchange does not exist
        :param exchange: str
        :return: Exchange
        """
        if exchange not in self.Exchanges:
            raise ProtocolError('Non-existent exchange: ' + exchange)
        return self.Exchanges[exchange]

    def HandlerOrder(self, ID, exchange, commodity, order_type, amount, price):
        try:
            messages = self.GetExchange(exchange).ProcessOrder(ID, exchange, commodity, order_type, amount, price,
                                                       self.Protocol)
        except AccountingError as ex:
            msg = self.Protocol.BuildMessage('#O_FAIL', ex.args[0])
            self.SendMessage(msg, ID)
            return
        for ID_player, m in messages:
            self.SendMessage(m, ID_player)

    def HandlerQueryQ(self, ID, exchange, commodity, quote_type):
        msg = self.GetExchange(exchange).GetQuote(ID, exchange, commodity, quote_type, self.Protocol)
        self.SendMessage(msg, ID)

    def HandlerQueryC(self, ID):
        msg = self.Protocol.BuildMessage('=C', self.CashBalances[ID], 0)
        self.SendMessage(msg, ID)

    def HandlerRemoveOrder(self, ID, exchange, commodity, remove_type):
        ex = self.GetExchange(exchange)
        ex.RemoveOrders(ID, commodity, remove_type)

    def ProcessQuery(self, ID, query):
        """
        DEPRECATED
        :param ID: int
        :param query: str
        :return:
        """
        info = query.split('|')
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
        super(RTS_BaseEconomicSimulation, self).ProcessCommand(ID, msg)

    def EventProduction(self, exchange_name, technique_name, ID, amount):
        exchange = self.Exchanges[exchange_name]
        technique = self.Production.Techniques[technique_name]
        # Return InProduction
        for k, v in technique.InProduction:
            exchange.Commodities[k].Balances.ReleaseInProduction(ID, amount * v)
        for k, v in technique.Output:
            exchange.Commodities[k].Balances[ID] = exchange.Commodities[k].Balances[ID] + (amount * v)
        msg = self.Protocol.BuildMessage('#P', exchange_name, technique_name, amount)
        self.SendMessage(msg, ID)

    def HandlerProduction(self, ID, exchange_name, technique_name, amount):
        if exchange_name not in self.Exchanges:
            raise ProtocolError('Exchange does not exist: {0}'.format(exchange_name))
        exchange = self.Exchanges[exchange_name]
        if technique_name not in self.Production.Techniques:
            raise ProtocolError('Unknown production technique: {0}'.format(technique_name))
        technique = self.Production[technique_name]
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
                raise ProtocolError('*ERROR: Insufficient {0} FOR PRODUCTION'.format(k))
        # Now, do the work
        for k,v in technique.Consumed:
            exchange.Commodities[k].Balances.Consume(ID, amount*v)
        for k, v in technique.InProduction:
            exchange.Commodities[k].Balances.MoveToInProduction(ID, amount*v)
        event = Event(callback=self.EventProduction)
        event.Args = (exchange_name, technique_name, ID, amount)
        event.Text = 'Production Event From {0}: Exchange={1} Technique={2} Amount={3}'.format(ID,
                                exchange_name, technique_name, amount)
        self.EventQueue.InsertEvent(self.T + technique.Time, event)














