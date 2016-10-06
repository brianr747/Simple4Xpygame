
"""
server.py

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


import mynetwork
from pprint import pprint
import socket, traceback, time,select,threading


from Game1 import Game

class GameServer(mynetwork.SingleLineProtocolServer):
    "Game server"
    def __init__(self,numplayers):
        self.NumPlayers = numplayers
        print "Setting up server"
        super(GameServer,self).__init__()
        self.PlayerList = [None,] * numplayers
        self.ObserverList = []
        self.State = "Lobby"
        self.Game = None
        self.PlayerLookup = {}
        self.ObserveAs = {}
        
        
    def main(self):
        print "Main!"
        cnt = 0
        try:
            while True:
                time.sleep(.05)
##                kys = self.WrapperDict.keys()
##                cnt += 1
##                if cnt == 50:
##                    for k in kys:
##                        self.sendmessage(k,"HEARTBEAT:" + self.State)
##                    cnt = 0
                self.network_events()
        except:
            traceback.print_exc()
            time.sleep(20)
        
    def Dump(self,msg):
        pprint("Data dump!")
        pprint(("State",self.State))
        if self.Game is not None:
            self.Game.Dump()
        
        
    def handler_message(self,msg,FileNo):
        "Stub for derived classes"
        if "DUMP" in msg:
            self.Dump(msg)
            return
        if msg == "?STATE":
            self.SendState(FileNo)
            return
        if msg == "?PLAYERS":
            response = [str(x is not None) for x in self.PlayerList]
            response = "PLAYERS," + ",".join(response)
            self.sendmessage(FileNo,response)
            return
        if msg == "Join-Observer":
            self.ObserverList.append(FileNo)
            print self.ObserverList
            return
        if "JOIN" in msg:
            self.AddPlayer(msg,FileNo)
            return
        if "OBSERVE_AS" == msg[0:10]:
            ID = int(msg[11:]) % self.NumPlayers        
            self.ObserveAs[FileNo] = ID
            return
        if self.State == 'Started':
            if msg == "FINISHED":
                try:
                    p_id = self.PlayerLookup[FileNo]
                except:
                    return
                if self.Game.PlayerTurnFinished(p_id):
                    print "Turn finished; broadcast!"
                return
            if msg == "?PLANETS":
                if FileNo in self.ObserveAs:
                    ID = self.ObserveAs[FileNo]
                else:
                    try:
                        ID = self.PlayerLookup[FileNo]
                    except:
                        return
                response= self.Game.GetPlanets(ID)
                self.sendmessage(FileNo,response)
                return
            if msg == "?FLEETS":
                #print "Received ?FLEETS"
                if FileNo in self.ObserveAs:
                    ID = self.ObserveAs[FileNo]
                else:
                    try:
                        ID = self.PlayerLookup[FileNo]
                    except:
                        return
                response= self.Game.GetFleets(ID)
                self.sendmessage(FileNo,response)
                return
            if msg[0:4] == 'MOVE':
                try:
                    ID = self.PlayerLookup[FileNo]
                except:
                    return
                msg = msg.split(";")
                try:
                    fleetID = int(msg[1])
                    planetID = int(msg[2])
                except:
                    self.sendmessage(FileNo,"ERROR;Move Syntax")
                    return
                status = self.Game.OrderMoveFleet(ID,fleetID,planetID)
                if status is not None:
                    self.sendmessage(FileNo,"ERROR;"+status)
                return
            if msg[0:5] == 'SPLIT':
                try:
                    ID = self.PlayerLookup[FileNo]
                except:
                    return
                msg = msg.split(";")
                try:
                    fleetID = int(msg[1])
                    planetID = int(msg[2])
                    ships = int(msg[3])
                except:
                    self.sendmessage(FileNo,"ERROR;Split Syntax")
                    return
                status = self.Game.OrderSplitFleet(ID,fleetID,planetID,ships)
                if status is not None:
                    self.sendmessage(FileNo,"ERROR;"+status)
                return
                    
                    
                
            
        print "Unhandled message:",msg,FileNo

    def SendState(self,FileNo):
        if self.State == "Lobby":
            self.sendmessage(FileNo,"State:Lobby")
            return
        if self.State == "Started":
            self.sendmessage(FileNo,"State:Started:Turn=%i" % (self.Game.Turn,))
            return
        print "Unhandled state message!"
        



    def AddPlayer(self,msg,FileNo):
        msg = msg.split("-")
        playernum = int(msg[1])
        if FileNo in self.PlayerList:
            self.sendmessage(FileNo,"Already connected, loser!")
            return
        if self.PlayerList[playernum] is not None:
            self.sendmessage(FileNo,"FAILURE-ALREADY CONNECTED")
            return
        self.PlayerList[playernum] = FileNo
        self.sendmessage(FileNo,"CONNECTED:%i" % (playernum,))
        self.PlayerLookup[FileNo] = playernum
        if not None in self.PlayerList and self.Game is None:
            self.StartGame()

    def StartGame(self):
        self.State = "Started"
        self.Game = Game()
        self.Game.Build(self.NumPlayers)
        

    def handler_connection(self,FileNo):
        "Stub for derived classes"
        print "Connection",FileNo
        self.PlayerLookup[FileNo] = None

    def handler_disconnect(self,FileNo):
        "Stub for derived classes"
        pprint(("Disconnected",FileNo))
        if FileNo in self.ObserverList:
            self.ObserverList.remove(FileNo)
        pprint("ObserverList")
        pprint(self.ObserverList)
        for i in range(0,len(self.PlayerList)):
            if self.PlayerList[i] == FileNo:
                self.PlayerList[i] = None



if __name__ == '__main__':
##    n = raw_input("Number of players ?> ")
##    n = int(n)
    n = 3
    g = GameServer(n)
    g.main()
        
    
    


