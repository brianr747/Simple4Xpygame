"""
Game1.py

"""

from pprint import pprint
import random
import math

import utils
import combat1
from Galaxy import Galaxy
from Fleet1 import Fleet
from Planet import Planet


# class Planet:
#     def __init__(self, ID, planetcode):
#         self.ID = ID
#         self.PlanetCode = planetcode
#         self.x = None
#         self.y = None
#         self.PlayerID = None
#         self.Production = float(random.randint(5, 100)) / 10.
#
#     def ToString(self, visibility="None"):
#         s = "ID=%i;PlanetCode=%s;x=%.1f;y=%.1f" % (self.ID, self.PlanetCode, self.x, self.y)
#         if visibility == "None":
#             return s
#         s = s + ";PlayerID=%s" % (str(self.PlayerID),)
#         if visibility == "Planet":
#             return s
#         assert (visibility == 'Ship')
#         s = s + ";Production=%.1f" % (self.Production,)
#         return s
#
#     # static method
#     @staticmethod
#     def MergeDataStrings(new_s, old_s):
#         new = new_s.split(";")
#         old = old_s.split(";")
#         if len(old) > len(new):
#             M = len(new)
#             out = new + old[M:]
#         else:
#             out = new
#         return ";".join(out)
#
#     @staticmethod
#     def FromString(s):
#         self = Planet(-1, "-1")
#         info = s.split(";")
#         for i in info:
#             if not "=" in i:
#                 continue
#             (name, val) = i.split("=")
#             if name in ('x', 'y', 'PlayerID', 'ID'):
#                 setattr(self, name, int(float(val)))
#                 continue
#             setattr(self, name, val)
#         return self


class Player:
    def __init__(self, ID, name):
        self.ID = ID
        self.Name = name
        self.SensorRangeShip = 50.
        self.ShipRange = utils.getglobals()["ShipRange"]
        self.ShipSpeed = 25.
        self.SensorRangePlanet = 100.
        self.ControlledPlanets = []
        self.VisiblePlanets = {}
        self.PreviouslyVisiblePlanets = {}
        self.VisibleFleets = []

    def Dump(self):
        pprint("Player")
        for i in dir(self):
            if "__" in i:
                continue
            if str(type(getattr(self, i))) == "<type 'instancemethod'>":
                continue
            if str(type(getattr(self, i))) == "<type 'instance'>":
                getattr(self, i).Dump()
                continue
            pprint((i, getattr(self, i)))


# class Galaxy:
#     def __init__(self, seed, numplanets, neutralplayer):
#         self.Seed = seed
#         self.NumPlanets = numplanets
#         self.PlanetList = []
#         self.GalaxySize = 200
#         self.Distances = {}
#         self.NeutralPlayer = neutralplayer
#         self.PopulateGalaxy()
#         self.CalculateDistances()
#
#     def Dump(self):
#         pprint("Galaxy---------------------")
#         pprint("Planet Listing")
#         for p in self.PlanetList:
#             pprint((p.PlanetCode, p.x, p.y))
#         M = self.GalaxySize / 10
#         for y in xrange(M, -(M + 1), -1):
#             lline = ""
#             for x in xrange(-M, M + 1):
#                 tmp = "."
#                 for p in self.PlanetList:
#                     if (x == int(p.x / 10)) and (y == int(p.y / 10)):
#                         tmp = p.PlanetCode
#                 lline = lline + tmp
#             print lline
#         pprint("End Galaxy----------------")
#
#     def PopulateGalaxy(self):
#         random.seed(self.Seed)
#         for i in xrange(0, self.NumPlanets):
#             pcode = planetcodes[i]
#             p = Planet(i, pcode)
#             p.PlayerID = self.NeutralPlayer
#             self.NumTries = 0
#             (x, y) = self.FindGoodPos()
#             p.x = x
#             p.y = y
#             self.PlanetList.append(p)
#
#     def FindGoodPos(self):
#         M = int(math.floor(self.GalaxySize / 2))
#         x = float(random.randint(-M, M) + random.randint(-M, M))
#         y = float(random.randint(-M, M) + random.randint(-M, M))
#         if self.NumTries == 1000:
#             raise Exception("Cannot Find a planet position!")
#         closest = float(10 * self.GalaxySize)
#         for p in self.PlanetList:
#             d = math.sqrt(float(pow(x - p.x, 2) + pow(y - p.y, 2)))
#             if d < closest:
#                 closest = d
#         if closest < 30.:
#             self.NumTries = self.NumTries + 1
#             return self.FindGoodPos()
#         return (x, y)
#
#     def FindClosest(self, x, y):
#         pos = None
#         closest = 10 * float(self.GalaxySize)
#         for i in range(0, len(self.PlanetList)):
#             planet = self.PlanetList[i]
#             dist = math.sqrt(pow(x - float(planet.x), 2) + pow(y - float(planet.y), 2))
#             if dist < closest:
#                 closest = dist
#                 pos = i
#         return pos
#
#     def PlacePlayers(self, numplayers):
#         # Place players on a circle
#         random.seed(self.Seed)
#         radius = float(self.GalaxySize) * .7
#         init_angle = math.radians(random.randint(0, 359))
#         for id_player in range(0, numplayers):
#             offset = init_angle + id_player * (2 * math.pi) / float(numplayers)
#             # Find target location
#             targ_x = radius * math.cos(offset)
#             targ_y = radius * math.sin(offset)
#             print "Target x,y", targ_x, targ_y
#             id_planet = self.FindClosest(targ_x, targ_y)
#             planet = self.PlanetList[id_planet]
#             planet.PlayerID = id_player
#             planet.Production = 12.
#             print planet.PlanetCode
#
#     def CalculateDistances(self):
#         for id_1 in range(0, self.NumPlanets):
#             for id_2 in range(id_1, self.NumPlanets):
#                 p1 = self.PlanetList[id_1]
#                 p2 = self.PlanetList[id_2]
#                 dist = math.sqrt(pow(float(p1.x - p2.x), 2) + pow(float(p1.y - p2.y), 2))
#                 self.Distances[(id_1, id_2)] = dist
#                 self.Distances[(id_2, id_1)] = dist


class Game:
    def __init__(self):
        self.Turn = 0
        self.NumPlayers = None
        random.seed()
        self.Seed = random.randint(0, 2000)
        self.PlayerFinished = []
        self.FleetList = []

    def Build(self, numplayers):
        self.NumPlayers = numplayers
        self.Galaxy = Galaxy(self.Seed, numplanets=52, neutralplayer=numplayers)
        self.Galaxy.PlacePlayers(self.NumPlayers)
        self.PlayerList = []
        for i in range(0, self.NumPlayers):
            name = "Player%i" % (i,)
            player = Player(i, name)
            self.PlayerList.append(player)
        self.PlayerFinished = [False, ] * numplayers
        self.DetermineVisibility()

    def Dump(self):
        pprint("Dumping Game State")
        for i in dir(self):
            if "__" in i:
                continue
            if i == "PlayerList":
                for p in self.PlayerList:
                    p.Dump()
                continue
            if i == "FleetList":
                pprint("FleetList")
                for f in self.FleetList:
                    pprint(f.ToString())
                continue
            if str(type(getattr(self, i))) == "<type 'instancemethod'>":
                continue
            if str(type(getattr(self, i))) == "<type 'instance'>":
                getattr(self, i).Dump()
                continue
            pprint((i, getattr(self, i)))

    def DetermineVisibility(self):
        for player in self.PlayerList:
            p_id = player.ID
            player.ControlledPlanets = []
            player.VisibleFleets = []
            # First: populate the empire
            for planet in self.Galaxy.PlanetList:
                if planet.PlayerID == p_id:
                    player.ControlledPlanets.append(planet.ID)
            # Now, see if visible
            player.VisiblePlanets = {}
            for planet in self.Galaxy.PlanetList:
                if planet.PlayerID == p_id:
                    player.VisiblePlanets[planet.ID] = (planet.ToString('Planet'), 0.)
                    continue
                # Otherwise, find range
                closest = 100000000.
                for other in player.ControlledPlanets:
                    d = self.Galaxy.Distances[(planet.ID, other)]
                    if d < closest:
                        closest = d
                if closest <= player.SensorRangeShip:
                    player.VisiblePlanets[planet.ID] = (planet.ToString('Ship'), closest)
                elif closest <= player.SensorRangePlanet:
                    player.VisiblePlanets[planet.ID] = (planet.ToString('Planet'), closest)
            for planetID in player.VisiblePlanets.keys():
                new_str = player.VisiblePlanets[planetID][0]
                if player.PreviouslyVisiblePlanets.has_key(planetID):
                    old_str = player.PreviouslyVisiblePlanets[planetID]

                    new_str = Planet.MergeDataStrings(new_str, old_str)

                    player.PreviouslyVisiblePlanets[planetID] = new_str
                else:
                    # Was not already an entry; copy latest
                    player.PreviouslyVisiblePlanets[planetID] = new_str
            # Now, do fleets
            for f in self.FleetList:
                if p_id == f.PlayerID:
                    # You always see your own fleets - duh...
                    player.VisibleFleets.append(f.ToString())
                    continue
                # Assumption: Fleet detection is shorter (or equal) to planet detection!
                # Deal with ships at planets
                if f.AtPlanetID == -1:
                    # In space!
                    # For now, fleets in hyperspace are invisible
                    continue
                if f.AtPlanetID not in player.VisiblePlanets:
                    # Cannot be seen!
                    continue
                # Are we in ship sensor range?
                (planet_str, dist) = player.VisiblePlanets[f.AtPlanetID]
                if dist <= player.SensorRangeShip:
                    player.VisibleFleets.append(f.ToString())

    def GetPlanets(self, player_id):
        out = self.PlayerList[player_id].VisiblePlanets.values()
        out = [x[0] + ";" + str(x[1]) for x in out]
        out = "PLANETS|" + "|".join(out)
        return out

    def GetFleets(self, player_id):
        #####
        out = self.PlayerList[player_id].VisibleFleets
        out = "FLEETS|" + "|".join(out)
        return out

    def PlayerTurnFinished(self, p_id):
        "Returns True if all players are finished"
        self.PlayerFinished[p_id] = True
        if False in self.PlayerFinished:
            return False
        self.EndOfTurn()
        return True

    def FindFleetsAtPlanet(self, planetID, playerID=None):
        out = []
        for f in self.FleetList:
            if f.AtPlanetID == planetID:
                if playerID is not None:
                    if not f.PlayerID == playerID:
                        continue
                out.append(f)
        return out

    def Production(self):
        for p in self.Galaxy.PlanetList:
            # ignore fractional production for now
            prod = int(p.Production)
            if p.PlayerID == self.NumPlayers:
                prod = int(prod / 4)
            if prod == 0:
                continue
            f_list = self.FindFleetsAtPlanet(p.ID, p.PlayerID)
            if len(f_list) == 0:
                # Create a new fleet
                f = Fleet()
                f.Ships = prod
                f.AtPlanetID = p.ID
                f.PlayerID = p.PlayerID
                f.x = p.x
                f.y = p.y
                self.FleetList.append(f)
            else:
                f_list[0].Ships += prod

    def OrderMoveFleet(self, playerID, fleetID, target_planet):
        "returns stringif error; none otherwise"
        pos = -1
        for i in range(0, len(self.FleetList)):
            if fleetID == self.FleetList[i].ID:
                pos = i
                break
        if pos == -1:
            return "No fleet with that ID"
        fleet = self.FleetList[pos]
        if fleet.PlayerID <> playerID:
            return "Not your fleet!"
        if fleet.AtPlanetID == -1:
            return "Fleet in space"
        if self.Galaxy.Distances[(fleet.AtPlanetID, target_planet)] > self.PlayerList[playerID].ShipRange:
            return "Planet out of range"
        fleet.AtPlanetID = -1
        fleet.TargetID = target_planet
        return None

    def OrderSplitFleet(self, playerID, fleetID, target_planet, numships):
        "returns stringif error; none otherwise"
        if numships < 0:
            return "-ve ships in split"
        if numships == 0:
            # Do nothing
            return None
        pos = -1
        for i in range(0, len(self.FleetList)):
            if fleetID == self.FleetList[i].ID:
                pos = i
                break
        if pos == -1:
            return "No fleet with that ID"
        fleet = self.FleetList[pos]
        if fleet.PlayerID <> playerID:
            return "Not your fleet!"
        if fleet.AtPlanetID == -1:
            return "Fleet in space"
        if self.Galaxy.Distances[(fleet.AtPlanetID, target_planet)] > self.PlayerList[playerID].ShipRange:
            return "Planet out of range"
        if numships > fleet.Ships:
            return "Too many ships in SPLIT"
        new_f = Fleet()
        new_f.Ships = numships
        new_f.AtPlanetID = -1
        new_f.TargetID = target_planet
        new_f.PlayerID = fleet.PlayerID
        new_f.x = fleet.x
        new_f.y = fleet.y
        self.FleetList.append(new_f)

        fleet.Ships -= numships
        return None

    def MoveFleets(self):
        for f in self.FleetList:
            if f.AtPlanetID <> -1:
                continue
            targ_planet = self.Galaxy.PlanetList[f.TargetID]
            dist = utils.calcdist(targ_planet, f)
            speed = self.PlayerList[f.PlayerID].ShipSpeed
            if dist <= speed:
                # f_list = self.FindFleetsAtPlanet(targ_planet.ID,f.PlayerID)
                f.x = targ_planet.x
                f.y = targ_planet.y
                f.AtPlanetID = targ_planet.ID
                f.TargetID = -1
                # Do merge as part of combat...
            ##                if len(f_list) > 0:
            ##                    # Merge fleet!
            ##                    f_list[0].Ships += f.Ships
            ##                    f.Ships = 0
            else:
                delta_x = float(targ_planet.x - f.x)
                delta_y = float(targ_planet.y - f.y)
                tot = utils.calcdist(f, targ_planet)
                # Unit vector = delta/(tot)
                # movement = speed*unit vector
                f.x += speed * delta_x / tot
                f.y += speed * delta_y / tot

    @staticmethod
    def MergeFleets(f1, f2):
        f1.Ships += f2.Ships
        f2.Ships = 0

    def CullEmptyFleets(self):
        for f in self.FleetList:
            if f.Ships == 0:
                self.FleetList.remove(f)

    def Combat(self):
        for p in self.Galaxy.PlanetList:
            planet_ID = p.ID
            loc_fleets = self.FindFleetsAtPlanet(planet_ID)
            # First, merge same player fleets
            for f1 in loc_fleets:
                for f2 in loc_fleets:
                    if f1 == f2:
                        continue
                    if f1.PlayerID == f2.PlayerID:
                        self.MergeFleets(f1, f2)
            self.CullEmptyFleets()
            loc_fleets = self.FindFleetsAtPlanet(planet_ID)
            if len(loc_fleets) == 0:
                # No fleets, nothing can happen
                continue
            if len(loc_fleets) == 1:
                # Could have a conquest, if there were no ships there
                if not (p.PlayerID == loc_fleets[0].PlayerID):
                    print "Conquered:", p.PlanetCode, "by", loc_fleets[0].PlayerID
                    p.PlayerID = loc_fleets[0].PlayerID
                continue
            seed = random.randint(0, 10000)
            ##            print "Combat!"
            ##            print "Before:"
            ##            for f in loc_fleets:
            ##                print f.ToString()
            combat = combat1.Combat(seed, loc_fleets)
            combat.RunCombat(run_one_step=False)
            ##            print "After"
            ##            for f in loc_fleets:
            ##                print f.ToString()
            self.CullEmptyFleets()
            # Conquest
            loc_fleets = self.FindFleetsAtPlanet(planet_ID)
            if len(loc_fleets) == 1:
                if not (p.PlayerID == loc_fleets[0].PlayerID):
                    print "Conquered:", p.PlanetCode, "by", loc_fleets[0].PlayerID
                    p.PlayerID = loc_fleets[0].PlayerID

    def EndOfTurn(self):
        self.Production()
        # TODO:
        self.MoveFleets()
        self.Combat()
        self.DetermineVisibility()

        # End step processing
        self.Turn = self.Turn + 1
        self.PlayerFinished = [False, ] * self.NumPlayers


if __name__ == '__main__':
    pprint("Hello, run from main1.py!")
