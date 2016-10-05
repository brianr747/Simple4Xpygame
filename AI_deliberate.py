"""
AIDeliberate1.py

The "deliberate" AI.Probably the base for all AI's

"""


import time,traceback
import random
import math

from BaseAI1 import BaseAI1


class AIDeliberate1(BaseAI1):
    def CalculateTurn(self):
        print "Starting",self.GameTurn
        self.CalcDistances()
        self.CalculateInRange()
        self.CalcShipsAtPlanet()
        
       # Create the "high priority planets" for where to send ships
       # Start out with border planets
        prioritylist = []
        for p in self.PlanetInfoParsed:
            if p.PlayerID <> self.PlayerID:
                continue
            (enemy,friendly) = self.InRange[p.ID]
            if len(enemy) > 0:
                prioritylist.append(p.ID)              
        # If there are no enemies in range, cannot do anything!
        if len(prioritylist) == 0:
            return
        fleetlist = []
        for f in self.FleetInfoParsed:
            if not f.PlayerID == self.PlayerID:
                continue
            if f.AtPlanetID == -1:
                # In space!
                continue
            fleetlist.append(f)
        # First, determine attacks
        removelist = []
        for f in fleetlist:
            if f.AtPlanetID not in prioritylist:
                continue
            removelist.append(f)
            (enemy,friendly) = self.InRange[f.AtPlanetID]
            enemyships = [p.Ships for p in enemy]
            if max(enemyships) > 1.5*f.Ships:
                # Freeze the fleet!
                continue
            if max(enemyships) < .5*f.Ships:
                # Weaklings! Attack the closest!
                num_move = min(max(enemyships)*2+2,f.Ships) # Always send 2 ships..
                dist = [self.Distances[(f.AtPlanetID,p.ID)] for p in enemy]
                mmin = min(dist)
                for pos in range(0,len(dist)):
                    if dist[pos] == mmin:
                        msg = "SPLIT;%i;%i;%i" % (f.ID,enemy[pos].ID,num_move)
                        print msg
                        self.sendserver(msg)
                        break
                continue
            # No raids, for now
            pass
        for f in removelist:
            fleetlist.remove(f)
        # Now, just move towards prioritylist
        while len(fleetlist) > 0:
            new_adds = []
            for f in fleetlist:
                (enemy,friendly) = self.InRange[f.AtPlanetID]
                assert(len(enemy)==0)
                for p in friendly:
                    if p.ID in prioritylist:
                        msg = "MOVE;%i;%i" % (f.ID,p.ID)
                        self.sendserver(msg)
                        fleetlist.remove(f)
                        # The current planet becomes a priority for the next round
                        new_adds.append(f.AtPlanetID)
                        break
            if len(new_adds) >0:
                prioritylist += new_adds
            else:
                # Somehow, fleets are cut off from the front.
                # we ran a cycle, and not able to add to the priority list
                break
        return
            
                        
                
                
            
            
                        
            
            
            
        
##        for f in self.FleetInfoParsed:
##            print "fleet",f.AtPlanetID,f.Ships
##        for p in self.PlanetInfoParsed:
##            print p.ID
##        x = raw_input()
 
                
                

if __name__ == '__main__':
    client = AIDeliberate1()
    client.main()
        
