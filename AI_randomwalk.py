"""
AIRandomWalk1.py

The "random walk" AI. Possibly the worst AI (that makes legitimate moves).

"""


import time,traceback
import random
import math

from BaseAI1 import BaseAI1


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
        
