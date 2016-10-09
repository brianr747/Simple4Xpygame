"""
fleet.py

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


class Fleet:
    Global_ID = 0
    def __init__(self,ID=None):
        if ID is None:
            # TODO: Validate that ID is unused? Only matters for serialisation, I think
            ID = Fleet.Global_ID
            Fleet.Global_ID += 1
        self.ID = ID
        # Eventually, will need to create ship classes
        self.Ships = 0
        # AtPlanetID = -1 -> In space!
        self.AtPlanetID = -1
        self.PlayerID = -1
        self.TargetID = -1
        self.x = None
        self.y = None
        self.IsDefending=False
    def ChangeShips(self,change):
        self.Ships += change
        assert(self.Ships >= 0)
    def GetPower(self):
        return self.Ships
    def ToString(self):
        return "ID=%i;Ships=%i;AtPlanetID=%i;PlayerID=%i;x=%.1f;y=%.1f;IsDefending=%s;TargetID=%i" % (self.ID,self.Ships,self.AtPlanetID,self.PlayerID,self.x,self.y,str(self.IsDefending),self.TargetID)
    @staticmethod
    def FromString(s):
        self = Fleet(-1)
        info = s.split(";")
        for i in info:
            if not "=" in i:
                continue
            (name,val) = i.split("=")
            if name in ('x','y'):
                try:
                    val = float(val)
                except:
                    pass                
            if name in ('ID','Ships','AtPlanetID','PlayerID','TargetID'):
                try:
                    val = int(val)
                except:
                    pass
            elif name == 'IsDefending':
                val = bool(val)
            setattr(self,name,val)
        return self
