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
from pprint import pprint
import random
from planet import Planet

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
        self.CalculateDistances()
        self.NumTries = 0
        self.Core = []

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

    def connectallstars(self):
        "Make sure all stars are connected to the core"
        pass
