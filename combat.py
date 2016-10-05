

"""
combat1.py
"""

import random
import unittest
from pprint import pprint

from Fleet1 import Fleet



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
        
        
        














class TestCombat(unittest.TestCase):
    def CreateFleet1(self):
        f = Fleet(ID=1)
        f.PlayerID=1
        f.Ships = 10
        f.IsDefending=False
        return f
    def CreateFleet2(self):
        f = Fleet(ID=2)
        f.PlayerID=2
        f.Ships = 20
        f.IsDefending=False
        return f
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
    def test_ctor(self):
        obj = Combat(112,[])
        self.assertEqual(obj.Seed,112)
        self.assertEqual(obj.FleetList,[])
    def test_empty(self):
        obj = Combat(112,[])
        obj.RunCombat()
        self.assertEqual(obj.Seed,112)
        self.assertEqual(obj.FleetList,[])
        self.assertEqual(obj.OutFleets,[])
    def test_randoms(self):
        # Make sure we always get the same output!
        obj = Combat(112,[])
        out = obj.GenerateRandoms(5,1000)
        self.assertEqual(out,[481, 666, 620, 700, 903])
        # No re-seed
        out = obj.GenerateRandoms(5,1000)
        self.assertEqual(out,[752, 162, 221, 455, 390])        
        # re-seed in RunCombat; same results
        obj.RunCombat()
        out = obj.GenerateRandoms(5,1000)
        self.assertEqual(out,[481, 666, 620, 700, 903])

    def test_weights(self):
        f1 = self.CreateFleet1()
        f2 =self.CreateFleet2()
        f3 = self.CreateFleet2()
        obj = Combat(112,[f1,f2,f3])
        self.assertEqual(obj.DetermineWeights(0),[0,5,5])
        self.assertEqual(obj.DetermineWeights(1),[7,0,13])
        self.assertEqual(obj.DetermineWeights(2),[7,13,0])

    def test_combat3(self):
        f1 = self.CreateFleet1()
        f2 =self.CreateFleet2()
        f3 = self.CreateFleet2()
        obj = Combat(112,[f1,f2,f3])
        obj.HitLevel = 700
        # Set up
        obj.RunCombat(run_one_step=True)
        # Round one
        obj.RunCombat(run_one_step=True)
        # Numbr of ships - damage from events
        self.assertEqual(obj.FleetList[0].Ships,10-3-1)
        self.assertEqual(obj.FleetList[1].Ships,20-1-2)
        self.assertEqual(obj.FleetList[2].Ships,20-1-3)
        
    def test_combat2(self):
        f1 = self.CreateFleet1()
        f2 =self.CreateFleet2()
        obj = Combat(112,[f1,f2])
        obj.HitLevel = 700
        # Set up
        obj.RunCombat(run_one_step=True)
        # Round one
        obj.RunCombat(run_one_step=True)
        # Fleet 0 -> 1; 10 firepower, 2 hits
        self.assertEqual(obj.Events[0],('fire',0,1,10,2))
        # fleet 1 -> 0, 20 firepower, 6 hits (blam!)
        self.assertEqual(obj.Events[1],('fire',1,0,20,6))
        # Numbr of ships - damage from events
        self.assertEqual(obj.FleetList[0].Ships,10-6)
        self.assertEqual(obj.FleetList[1].Ships,20-2)

    def test_cullfleet(self):
        f1 = self.CreateFleet1()
        f2 =self.CreateFleet2()
        f2.Ships = 0
        obj = Combat(112,[f1,f2])
        # Set up
        obj.RunCombat(run_one_step=True)
        obj.RunCombat(run_one_step=True)
        self.assertEqual(obj.OutFleets,[f1,])
        
    def test_combat2_full(self):
        f1 = self.CreateFleet1()
        f2 =self.CreateFleet2()
        obj = Combat(112,[f1,f2])
        obj.HitLevel = 700
        # Set up
        obj.RunCombat(run_one_step=True)
        # Round one
        obj.RunCombat(run_one_step=True)
        # Fleet 0 -> 1; 10 firepower, 2 hits
        self.assertEqual(obj.Events[0],('fire',0,1,10,2))
        # fleet 1 -> 0, 20 firepower, 6 hits (blam!)
        self.assertEqual(obj.Events[1],('fire',1,0,20,6))
        # Numbr of ships - damage from events
        self.assertEqual(obj.FleetList[0].Ships,10-6)
        self.assertEqual(obj.FleetList[1].Ships,20-2)
        #----------- Next round
        obj.RunCombat(run_one_step=True)
        # Fleet 0 -> 1; 4 firepower, 0 hits
        self.assertEqual(obj.Events[0],('fire',0,1,4,0))
        # fleet 1 -> 0, 18 firepower, 3 hits (blam!)
        self.assertEqual(obj.Events[1],('fire',1,0,18,3))
        # Numbr of ships - damage from events
        self.assertEqual(obj.FleetList[0].Ships,4-3)
        self.assertEqual(obj.FleetList[1].Ships,18-0)    
        #---------- Next round
        obj.RunCombat(run_one_step=True)
        # Fleet 0 -> 1; 1 firepower, 0 hits
        self.assertEqual(obj.Events[0],('fire',0,1,1,0))
        # fleet 1 -> 0, 18 firepower, 1 hits (blam!)
        self.assertEqual(obj.Events[1],('fire',1,0,18,1))
        # Numbr of ships - damage from events
        self.assertEqual(obj.FleetList[0].Ships,1-1)
        self.assertEqual(obj.FleetList[1].Ships,18-0)
        obj.RunCombat(run_one_step=True)
        self.assertEqual(obj.Round,3)
        self.assertEqual(obj.OutFleets,[f2,])

    def test_end2end(self):
        f1 = self.CreateFleet1()
        f2 =self.CreateFleet2()
        obj = Combat(112,[f1,f2])
        obj.HitLevel = 700
        obj.RunCombat(run_one_step=False)
        self.assertEqual(obj.Round,3)
        self.assertEqual(obj.OutFleets,[f2,])
        # Same result as previous
        self.assertEqual(obj.OutFleets[0].Ships,18)
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





