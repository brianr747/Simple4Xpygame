"""
AIRandomWalk1.py

The "random walk" AI. Possibly the worst AI (that makes legitimate moves).

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

import random

from clients.baseAI import BaseAI1


class RandomWalk1(BaseAI1):
    def CalculateTurn(self):
        print "Starting",self.GameTurn
        self.CalcDistances()
##        for f in self.FleetInfoParsed:
##            print "fleet",f.AtPlanetID,f.Ships
##        for p in self.PlanetInfoParsed:
##            print p.ID
##        x = raw_input()
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
                

if __name__ == '__main__':
    client = RandomWalk1()
    client.main()
        
