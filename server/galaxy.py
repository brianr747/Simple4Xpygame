"""
galaxy.py


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

import math
import random
from pprint import pprint

from common import utils
from common.planet import Planet

planetcodes = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


class Galaxy:
    def __init__(self, seed, numplanets, neutralplayer):
        self.Seed = seed
        self.NumPlanets = numplanets
        self.PlanetList = []
        self.GalaxySize = 200
        self.Distances = {}
        self.NeutralPlayer = neutralplayer
        self.PopulateGalaxy()
        self.NumTries = 0
        self.Core = []
        self.ConnectAllStars()
        # Only calculate the distances after ConnectAllStars(), since they can be moved.
        self.CalculateDistances()

    def Dump(self):
        pprint("Galaxy---------------------")
        pprint("Planet Listing")
        for p in self.PlanetList:
            pprint((p.PlanetCode, p.x, p.y))
        M = self.GalaxySize / 10
        for y in xrange(M, -(M + 1), -1):
            lline = ""
            for x in xrange(-M, M + 1):
                tmp = "."
                for p in self.PlanetList:
                    if (x == int(p.x / 10)) and (y == int(p.y / 10)):
                        tmp = p.PlanetCode
                        if p not in self.Core:
                            tmp = "?"
                lline = lline + tmp
            print lline
        pprint("End Galaxy----------------")

    def PopulateGalaxy(self):
        random.seed(self.Seed)
        for i in xrange(0, self.NumPlanets):
            pcode = planetcodes[i]
            p = Planet(i, pcode)
            p.PlayerID = self.NeutralPlayer
            self.NumTries = 0
            (x, y) = self.FindGoodPos()
            p.x = x
            p.y = y
            self.PlanetList.append(p)

    def FindGoodPos(self):
        M = int(math.floor(self.GalaxySize / 2))
        x = float(random.randint(-M, M) + random.randint(-M, M))
        y = float(random.randint(-M, M) + random.randint(-M, M))
        if self.NumTries == 1000:
            raise Exception("Cannot Find a planet position!")
        closest = float(10 * self.GalaxySize)
        for p in self.PlanetList:
            d = math.sqrt(float(pow(x - p.x, 2) + pow(y - p.y, 2)))
            if d < closest:
                closest = d
        if closest < 30.:
            self.NumTries += 1
            return self.FindGoodPos()
        return x, y

    def FindClosest(self, x, y):
        pos = None
        closest = 10 * float(self.GalaxySize)
        for i in range(0, len(self.PlanetList)):
            planet = self.PlanetList[i]
            dist = math.sqrt(pow(x - float(planet.x), 2) + pow(y - float(planet.y), 2))
            if dist < closest:
                closest = dist
                pos = i
        return pos

    def PlacePlayers(self, numplayers):
        # Place players on a circle
        random.seed(self.Seed)
        radius = float(self.GalaxySize) * .7
        init_angle = math.radians(random.randint(0, 359))
        for id_player in range(0, numplayers):
            offset = init_angle + id_player * (2 * math.pi) / float(numplayers)
            # Find target location
            targ_x = radius * math.cos(offset)
            targ_y = radius * math.sin(offset)
            print "Target x,y", targ_x, targ_y
            id_planet = self.FindClosest(targ_x, targ_y)
            planet = self.PlanetList[id_planet]
            planet.PlayerID = id_player
            planet.Production = 12.
            print planet.PlanetCode

    def CalculateDistances(self):
        for id_1 in range(0, self.NumPlanets):
            for id_2 in range(id_1, self.NumPlanets):
                p1 = self.PlanetList[id_1]
                p2 = self.PlanetList[id_2]
                dist = math.sqrt(pow(float(p1.x - p2.x), 2) + pow(float(p1.y - p2.y), 2))
                self.Distances[(id_1, id_2)] = dist
                self.Distances[(id_2, id_1)] = dist

    def ConnectAllStars(self, init_only=False):
        """Make sure all stars are connected to the core"""
        # The original start distribution allows stars to be disconnected from the rest, stranding players.
        # Fix this by forcing all stars to be within standard jump range of a system in the "core"; such
        # a planet is also in the core.
        # First step: add
        self.FindClosestToCentre()
        if len(self.Core) == 0 or self.Core[0] is None:
            # Empty galaxy?
            return
        self.NonCore = self.PlanetList[:]
        self.NonCore.remove(self.Core[0])
        if init_only:
            return
        while len(self.NonCore) > 0:
            # If we reach this point, we only have planets that cannot reach the core
            self.RunOneStepOfConnection()

    def RunOneStepOfConnection(self):
        """
        Connection algorithm.
        Break out this single step for testing
        """
        shiprange = utils.getglobals()["ShipRange"]
        if len(self.NonCore) == 0:
            return
        # first: look to see if we can connect to core without moving planets
        moved = []
        for p in self.NonCore:
            for core_p in self.Core:
                if utils.CalcDist(p, core_p) <= shiprange:
                    moved.append(p)
                    self.Core.append(p)
                    break
        # Did we move any planets? If so, ready for another pass
        if len(moved) > 0:
            for p in moved:
                self.NonCore.remove(p)
            return
        # Only move one planet at a time
        closest = 1000.* shiprange
        closestinfo = (None,None)
        for p_out in self.NonCore:
            for p_in in self.Core:
                dist = utils.CalcDist(p_out, p_in)
                if dist < closest:
                    closestinfo = (p_out, p_in)
                    closest = dist
        p_out, p_in = closestinfo
        # Need to move p_out
        # Calculate the unit vector that points from p_in to p_out, then multiply
        # that vector by the shiprange. Putting p_out at the end of that vector ensures
        # that it is in range.
        unit_x = (p_out.x - p_in.x)/closest
        unit_y = (p_out.y - p_in.y)/closest
        delta = .95 * shiprange # Multiply by .95 so that we have wiggle room for rounding
        p_out.x = round(p_in.x + delta * unit_x,1)
        p_out.y = round(p_in.y + delta * unit_y,1)
        assert(utils.CalcDist(p_in, p_out) < shiprange)
        self.Core.append(p_out)
        self.NonCore.remove(p_out)


    def FindClosestToCentre(self):
        self.Core = []
        shortest_dist = 10. * self.GalaxySize
        closest = None
        centre = Planet.FromString('x=0.;y=0.')
        distances = [utils.CalcDist(p, centre) for p in self.PlanetList]
        for i in range(0, len(distances)):
            if distances[i] < shortest_dist:
                shortest_dist = distances[i]
                closest = self.PlanetList[i]
        self.Core = [closest, ]
