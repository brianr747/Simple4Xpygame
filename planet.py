
"""
planet.py


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

class Planet:
    def __init__(self, ID, planetcode):
        self.ID = ID
        self.PlanetCode = planetcode
        self.x = None
        self.y = None
        self.PlayerID = None
        self.Production = float(random.randint(5, 100)) / 10.

    def ToString(self, visibility="None"):
        s = "ID=%i;PlanetCode=%s;x=%.1f;y=%.1f" % (self.ID, self.PlanetCode, self.x, self.y)
        if visibility == "None":
            return s
        s = s + ";PlayerID=%s" % (str(self.PlayerID),)
        if visibility == "Planet":
            return s
        assert (visibility == 'Ship')
        s = s + ";Production=%.1f" % (self.Production,)
        return s

    # static method
    @staticmethod
    def MergeDataStrings(new_s, old_s):
        new = new_s.split(";")
        old = old_s.split(";")
        if len(old) > len(new):
            M = len(new)
            out = new + old[M:]
        else:
            out = new
        return ";".join(out)

    @staticmethod
    def FromString(s):
        self = Planet(-1, "-1")
        info = s.split(";")
        for i in info:
            if not "=" in i:
                continue
            (name, val) = i.split("=")
            if name in ('x', 'y', 'PlayerID', 'ID'):
                setattr(self, name, int(float(val)))
                continue
            setattr(self, name, val)
        return self


# class Player:
#     def __init__(self, ID, name):
#         self.ID = ID
#         self.Name = name
#         self.SensorRangeShip = 50.
#         self.ShipRange = 50.
#         self.ShipSpeed = 25.
#         self.SensorRangePlanet = 100.
#         self.ControlledPlanets = []
#         self.VisiblePlanets = {}
#         self.PreviouslyVisiblePlanets = {}
#         self.VisibleFleets = []
#
#     def Dump(self):
#         pprint("Player")
#         for i in dir(self):
#             if "__" in i:
#                 continue
#             if str(type(getattr(self, i))) == "<type 'instancemethod'>":
#                 continue
#             if str(type(getattr(self, i))) == "<type 'instance'>":
#                 getattr(self, i).Dump()
#                 continue
#             pprint((i, getattr(self, i)))
