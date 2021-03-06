"""
consoleclient.py

This implements a player client, but with a console interface for the human playing.
This allows us to test new game commands, without requiring a graphical interface.

The player can use a graphical observer client to aid play.


Copyright 2016 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
from pprint import pprint

import networkclient
from common.planet import Planet
from common.fleet import Fleet


class MessageError(ValueError):
    pass


class ConsoleClient(object):
    def __init__(self):
        "Set up without communicating to server"
        # Use the MockClient to help code lookup, but it does not connect
        self.CommunicationClient = networkclient.MockNetworkClient()
        self.State = 'Starting'
        self.DoMock = False
        self.LastTurn = -1
        self.GameTurn = -2
        self.GameState = '?'
        self.PlanetList = []
        self.FleetList = []
        self.IsObserver = False

    def Join(self):
        if self.State != 'Starting':
            raise ValueError('Already joined!')
        if self.DoMock:
            self.CommunicationClient = networkclient.MockNetworkClient()
        else:
            self.CommunicationClient = networkclient.NetworkClient()
        self.CommunicationClient.MessageHandler = self.MessageHandlerBase
        self.CommunicationClient.IsObserver = self.IsObserver
        self.CommunicationClient.Join()
        for i in range(0, 10):
            self.CommunicationClient.DoNetwork()
            if self.CommunicationClient.State == 'In Game':
                self.State = self.CommunicationClient.State
                return
            time.sleep(.1)
        self.State = self.CommunicationClient.State
        raise ValueError('Attempt to connect to server timed out.')

    def GetStateInfo(self):
        self.CommunicationClient.SendMessage("?STATE")
        self.CommunicationClient.SendMessage("?PLANETS")
        self.CommunicationClient.SendMessage("?FLEETS")

    def MessageHandlerBase(self, msg):
        if msg.lower().startswith("state"):
            msg = msg.split(":")
            self.GameState = msg[1]
            if len(msg) < 3:
                return
            turn = msg[2].split("=")
            assert(turn[0].lower() == 'turn')
            self.GameTurn = int(turn[1])
            if self.GameTurn > self.LastTurn:
                self.PlanetList = []
                self.FleetList = []
                self.LastTurn = self.GameTurn
                self.CommunicationClient.SendMessage("?PLANETS")
                self.CommunicationClient.SendMessage("?FLEETS")
            return
        if msg.startswith("PLANETS|"):
            if msg[-1] == '|':
                # if we have a trailing |, kill it!
                msg = msg[:-1]
            msg = msg.split("|")
            msg.pop(0)
            self.PlanetList = [Planet.FromString(s) for s in msg]
            return
        if msg.startswith("FLEETS|"):
            if msg[-1] == '|':
                # if we have a trailing |, kill it!
                msg = msg[:-1]
            msg = msg.split("|")
            msg.pop(0)
            self.FleetList = [Fleet.FromString(s) for s in msg]
            return
        self.MessageHandler(msg)

    def MessageHandler(self, msg):
        """Override in derived classes"""
        pprint("Unhandled message: " + msg)

    def PrintState(self):
        print "State:", self.State, "Game State:", self.GameState, "GameTurn:", self.GameTurn, "LastTurn:", self.LastTurn

    def PrintPlanets(self):
        pprint('Planet Dump')
        for p in self.PlanetList:
            msg  = "[Player_%02i] %02i %s %.1f,%.1f" % (p.PlayerID, p.ID, p.PlanetCode, p.x, p.y)
            pprint(msg)

    def PrintFleets(self):
        pprint('Fleet Dump')
        for p in self.FleetList:
            pprint(p.ToString())


    def main(self):
        self.Join()
        self.GetStateInfo()
        while True:
            self.CommunicationClient.SendMessage('?STATE')
            self.CommunicationClient.DoNetwork()
            self.PrintState()
            opt = raw_input("Option? [?=help]> ")
            opt = opt.strip()
            if opt == '?':
                print """
 Options:
 q = quit
 p = print planet list
 f = print fleet list
 d = done turn
 [empty string] = do nothing; process any network messages.
 Otherwise -> string sent to server as is.
"""
                continue
            if opt.lower() == 'q':
                break
            if opt.lower() == 'p':
                self.PrintPlanets()
                continue
            if opt.lower() == 'f':
                self.PrintFleets()
                continue
            if opt.lower() == 'd':
                self.CommunicationClient.SendMessage('FINISHED')
                self.CommunicationClient.DoNetwork()
                continue
            if opt.startswith('m '):
                try:
                    self.DoMove(opt)
                except ValueError:
                    print 'Invalid command'
                self.CommunicationClient.SendMessage('?FLEETS')
                continue
            self.CommunicationClient.SendMessage(opt)

    def FindPlanetFromCode(self, code):
        for p in self.PlanetList:
            if code == p.PlanetCode:
                return p
        raise KeyError('No matching planet')

    def FindFleetAtPlanet(self,p):
        for f in self.FleetList:
            if f.AtPlanetID == p.ID:
                return f
        raise KeyError('No fleet at planet')


    def DoMove(self,msg):
        msg = msg.strip()
        msg = msg.split(" ")
        if len(msg) < 3:
            raise ValueError('Bad format')
        src = msg[1]
        dest = msg[2]
        try:
            p_src = self.FindPlanetFromCode(src)
            fleet = self.FindFleetAtPlanet(p_src)
        except KeyError:
            raise ValueError('Not a known source planet; or no fleet')
        try:
            p_dest = self.FindPlanetFromCode(dest)
        except KeyError:
            raise ValueError('Not a known dest planet')
        msg = "MOVE;%i;%i" % (fleet.ID, p_dest.ID)
        print msg
        self.CommunicationClient.SendMessage(msg)
        self.CommunicationClient.DoNetwork()


class ConsoleObserver(ConsoleClient):
    def __init__(self):
        super(ConsoleObserver, self).__init__()
        self.IsObserver = True








