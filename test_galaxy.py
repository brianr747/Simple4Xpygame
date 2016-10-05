from unittest import TestCase

import galaxy
from planet import Planet


class TestGalaxy(TestCase):
    "Testing class. Under construction."

    @staticmethod
    def CreateGalaxy():
        g = galaxy.Galaxy(100, numplanets=3, neutralplayer=3)
        planets = ['ID=0;x=150;y=12', 'ID=1;x=55;y=5.5',
                   'ID=2;x=2;y=3', 'ID=3;x=170;y=0', 'ID=4;x=10;y=3']
        planets = [Planet.FromString(x) for x in planets]
        g.PlanetList = planets
        return g

    def test_Dump(self):
        # self.fail()
        pass

    def test_PopulateGalaxy(self):
        pass
        # self.fail()

    def test_FindGoodPos(self):
        pass
        # self.fail()

    def test_FindClosest(self):
        pass
        # self.fail()

    def test_PlacePlayers(self):
        pass
        # self.fail()

    def test_CalculateDistances(self):
        pass
        # self.fail()

    def test_FindClosestToCore(self):
        obj = TestGalaxy.CreateGalaxy()
        obj.FindClosestToCentre()
        self.assertEqual(obj.Core, [obj.PlanetList[2]])

    def test_ConnectAllStars(self):
        obj = TestGalaxy.CreateGalaxy()
        obj.ConnectAllStars(init_only=True)
        self.assertEqual(obj.Core,[obj.PlanetList[2]])

    def test_RunOneStepOfConnection(self):
        obj = TestGalaxy.CreateGalaxy()
        obj.ConnectAllStars(init_only=True)
        self.assertEqual(obj.Core,[obj.PlanetList[2]])
        obj.RunOneStepOfConnection()
        IDs = [p.ID for p in obj.Core]
        self.assertEqual(IDs, [2, 4])
        obj.RunOneStepOfConnection()
        IDs = [p.ID for p in obj.Core]
        # pick up a planet
        self.assertEqual(IDs, [2, 4, 1])
        obj.RunOneStepOfConnection()
        IDs = [p.ID for p in obj.Core]
        self.assertEqual(IDs, [2, 4, 1])




