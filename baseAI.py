"""
BaseAI1.py
Virtual base class for Version 1 AI

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


import time,traceback
import random
import math

import mynetwork
import Game1
import utils


class BaseAI1(mynetwork.SingleLineMasterClient):
    "Base for AI class, Version 1 of game"

    def __init__(self):
        super(BaseAI1,self).__init__()
        self.PlayerID = None
        self.State = "JOINING"
        self.GameState = None
        self.GameTurn = -1
        self.LastProcessed = -1
        self.FleetInfo = None
        self.PlanetInfo = None
        self.ShipRange = 50.  # TODO: Remove hardcoding 
        self.MyPlanets = []
        self.EnemyPlanets = []
        self.InRange = {}
        
        
    def handler_message(self,msg,FileNo):
        #print "Receieved '%s' from %i" % (msg,FileNo)
        if self.State == "JOINING":
            if "PLAYERS," in msg:
                msg = msg.split(",")
                msg.pop(0)
                player_connected = [x == "True" for x in msg]
                #print player_connected
                if False not in player_connected:
                    raise ValueError("Too many players")
                response = ""
                for i in range(0,len(player_connected)):
                    if player_connected[i] == False:
                        response = "JOIN-%i" % (i,)
                        break
                self.sendserver(response)
                print response
            if "CONNECTED" in msg:
                msg = msg.split(":")
                self.PlayerID = int(msg[1])
                self.State = "CONNECTED"
            return
        if "STATE" in msg.upper():
            old_state = self.GameState
            self.GameState = msg
            if not msg == old_state:              
                if not "STARTED" in msg.upper():
                    return
                msg = msg.split(":")
                info = msg[2]
                #print info
                assert(info[0:5].upper() == "TURN=")
                self.GameTurn = int(info[5:])
                # Wait  to make sure that buffers are cleared
                time.sleep(.1)
                self.FleetInfo = None
                self.PlanetInfo = None
                self.sendserver("?PLANETS")
                self.sendserver("?FLEETS")
                time.sleep(.1)
            return
        if "PLANETS" in msg.upper():
            info = msg.split("|")

            self.PlanetInfo = info[1:]
            if self.PlanetInfo==[""]:
                # Presumably, the player is dead...
                self.PlanetInfo = []                        
            return
        if "FLEETS" in msg.upper():
            info = msg.split("|")
            self.FleetInfo = info[1:]
            if self.FleetInfo == [""]:
                # No fleets on first turn (at least) - trailing "|" creates an empty string...
                self.FleetInfo = []
            return
                                  
        print "Unhandled msg",msg
        #mynetwork.SingleLineMasterClient.handler_message(self,msg,FileNo)

    def sendmessage(self,FileNo,msg):
        #print "Sent %i '%s'" % (FileNo,msg)
        mynetwork.SingleLineProtocolServer.sendmessage(self,FileNo,msg)

    def InitCalculateTurn(self):
        "Does initial set up"
        if self.FleetInfo is None:
            return
        if self.PlanetInfo is None:
            return
        #print "processing!"
        self.PlanetInfoParsed = [Game1.Planet.FromString(x) for x in self.PlanetInfo]
        self.FleetInfoParsed =[Game1.Fleet.FromString(x) for x in self.FleetInfo]
        self.MyPlanets = []
        self.EnemyPlanets = []
        for p in self.PlanetInfoParsed:
            if p.PlayerID == self.PlayerID:
                self.MyPlanets.append(p)
            else:
                self.EnemyPlanets.append(p)
        self.CalculateTurn()
        # Need to always do this, so do it here
        self.sendserver("FINISHED")
        self.LastProcessed = self.GameTurn

    def CalculateTurn(self):
        raise NotImplementedError("Must override this method in subclasses!")
        

    def CalcDistances(self):
        self.Distances = {}
        for p1 in self.PlanetInfoParsed:
            for p2 in self.PlanetInfoParsed:
                dist = math.sqrt(float(pow(p1.x - p2.x,2)) +float(pow(p1.y - p2.y,2)))
                self.Distances[(p1.ID,p2.ID)] = dist
        return

    def CalculateInRange(self):
        self.InRange = {}
        for p1 in self.PlanetInfoParsed:
            if p1.PlayerID <> self.PlayerID:
                continue
            friendly = []
            enemy = []
            for p2 in self.PlanetInfoParsed:
                if p1 == p2:
                    continue
                if self.Distances[(p1.ID,p2.ID)] < self.ShipRange:
                    if p2.PlayerID == self.PlayerID:
                        friendly.append(p2)
                    else:
                        enemy.append(p2)
            self.InRange[p1.ID] = (enemy,friendly)
    def CalcShipsAtPlanet(self):
        for p in self.PlanetInfoParsed:
            p.Ships = 0
            for f in self.FleetInfoParsed:
                if f.AtPlanetID == p.ID:
                    # Insert new field - yay for Python!
                    p.Ships = f.Ships
            

    def OldCode(self):
        "Random old code..."
        planetlist = [p.ID for p in self.PlanetInfoParsed]
        for f in self.FleetInfoParsed:
            if not f.PlayerID == self.PlayerID:
                continue
            if f.AtPlanetID == -1:
                # In space!
                continue
            ID = f.ID
            inrange = []
            targ_ID = None
            for p in self.EnemyPlanets:
                if self.Distances[(p.ID,f.AtPlanetID)] < self.ShipRange:
                    inrange.append(p)
            if len(inrange) > 0:
                pos = random.randint(0,len(inrange)-1)
                targ_ID = inrange[pos].ID
            else:
                inrange = []
                for p in self.MyPlanets:
                    if self.Distances[(p.ID,f.AtPlanetID)] < self.ShipRange:
                        inrange.append(p)
                if len(inrange) > 0:
                    pos = random.randint(0,len(inrange)-1)
                    targ_ID = inrange[pos].ID             
            if targ_ID is not None:
                msg = "MOVE;%i;%i" % (ID,targ_ID)
                self.sendserver(msg)
                print msg
        #a = raw_input("Hit return to continue> ")
        
        self.sendserver("FINISHED")
        self.LastProcessed = self.GameTurn
        
        
            
                

    def main(self):
        # Have to run this to get the connection set up
        self.State = "JOINING"
        self.network_events() 
        cnt = 0
        self.sendserver("?PLAYERS")     
        try:
            while True:
                time.sleep(.1)
                self.sendserver("?STATE")
                self.network_events()
                if self.LastProcessed < self.GameTurn:
                    self.InitCalculateTurn()
        except:
            traceback.print_exc()
            time.sleep(20)        
        
##if __name__ == '__main__':
##    client = AIMasterClient()
##    client.main()

    


