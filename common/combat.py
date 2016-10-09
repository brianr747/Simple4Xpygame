

"""
combat.py

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
import unittest


class Ship(object):
    def __init__(self,ID):
        self.ID = ID
        self.Initiative = 0
        self.IsDestroyed = False
    

class Combat(object):
    def __init__(self,seed,fleetlist):
        self.Seed = seed
        self.FleetList = fleetlist
        self.ShipList = []
        self.OutFleets = []
        self.Events = []
        self.Round=-1
        random.seed(seed)
        self.HitLevel = 400

    def SetUpShips(self):
        assert(self.Round==-1)
        return
##        ID = 0
##        self.ShipList = []
##        for f in self.FleetList:
##            l = []
##            for i in range(0,f.Ships):
##                s = Ship(ID)
##                ID += 1
##                l.append(s)
##            self.ShipList.append(l)
##        self.Round = 0
                

##    def CullDeadShips(self):            
##        for l in self.ShipList:
##            for s in l:
##                if s.IsDestroyed:
##                    l.remove(s)
                    
    def RunCombat(self,run_one_step=True):
        self.Events = []
        if self.Round == -1:
            random.seed(self.Seed)
            self.SetUpShips()
            self.Round = 0        
            if run_one_step:
                return
            else:
                self.RunCombat(run_one_step=False)
        self.CullDeadFleets()
        if len(self.FleetList) < 2:
            self.OutFleets = self.FleetList
            return
        self.Round += 1
        # determine targeting
        targeting = []
        for idx in range(0,len(self.FleetList)):
            wgts = self.DetermineWeights(idx)
            targeting.append(wgts)
        # All fleets fire; ships destroyed after firing
        for firing in range(0,len(self.FleetList)):
            wgts = targeting[firing]
            for target in range(0,len(self.FleetList)):
                firepower = wgts[target]
                if firepower < 1:
                    continue
                rolled = self.GenerateRandoms(firepower,1000)
                hits = [x > self.HitLevel for x in rolled]
                damage = sum(hits)
                if damage > self.FleetList[target].Ships:
                    damage = self.FleetList[target].Ships
                if run_one_step == True:
                    ev = ('fire',firing,target,firepower,damage)
                    self.Events.append(ev)                    
                if damage > 0:
                    self.FleetList[target].Ships -= damage
        if not run_one_step:
            self.RunCombat(run_one_step=False)
                
                
    def CullDeadFleets(self):
        for f in self.FleetList:
            if f.Ships < 1:
                self.FleetList.remove(f)
                                

    def DetermineWeights(self,idx):
        wgts = [float(x.Ships) for x in self.FleetList]
        wgts[idx] = 0.
        s = sum(wgts)
        if s > 0.:
            wgts = [x/s for x in wgts]
        firepower = self.FleetList[idx].Ships
        wgts = [int(float(firepower)*x) for x in wgts]
        if sum(wgts) <> firepower:
            if idx == 0:
                targ = 1
            else:
                targ = 0
            wgts[targ] += firepower - sum(wgts)
            assert(sum(wgts) == firepower)
        return wgts
           
        
    def GenerateRandoms(self,N,limit=1000):
        # OK, non-grammatical
        x = [None,] * N
        for i in range(0,N):
            x[i] = random.randint(0,limit)
        return x


##    def test_cull(self):
##        f1 = self.CreateFleet1()
##        f2 =self.CreateFleet2() 
##        obj = Combat(112,[f1,f2])
##        obj.RunCombat(run_one_step=True)
##        self.assertEqual(f1.Ships,len(obj.ShipList[0]))
##        self.assertEqual(f2.Ships,len(obj.ShipList[1]))
##        obj.CullDeadShips()
##        self.assertEqual(f1.Ships,len(obj.ShipList[0]))
##        self.assertEqual(f2.Ships,len(obj.ShipList[1]))
##        # Initial ID
##        self.assertEqual(obj.ShipList[0][0].ID,0)
##        self.assertEqual(obj.ShipList[1][1].ID,11)
##        self.assertEqual(obj.ShipList[1][3].ID,13)        
##        # Kill some ships
##        obj.ShipList[0][0].IsDestroyed = True
##        obj.ShipList[1][1].IsDestroyed = True
##        obj.ShipList[1][3].IsDestroyed = True
##        obj.CullDeadShips()
##        self.assertEqual(f1.Ships - 1,len(obj.ShipList[0]))
##        self.assertEqual(f2.Ships - 2,len(obj.ShipList[1]))
##        # ID's shift, to fill gaps
##        self.assertEqual(obj.ShipList[0][0].ID,1)
##        self.assertEqual(obj.ShipList[1][1].ID,12) # 1 greater
##        self.assertEqual(obj.ShipList[1][3].ID,15) # 2 greater
        
        
        
        
        







if __name__ == '__main__':
    unittest.main()





