import unittest

from common.combat import Combat
from common.fleet import Fleet


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
