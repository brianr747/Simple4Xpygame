
"""
tune_combat.py


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

import combat

from game import Fleet
from combat import Combat



def CreateFleet1():
    f = Fleet(ID=1)
    f.PlayerID=1
    f.Ships = 10
    f.IsDefending=False
    return f
def CreateFleet2():
    f = Fleet(ID=2)
    f.PlayerID=2
    f.Ships = 20
    f.IsDefending=False
    return f




def main():
    print "IN"
    distrib = [0,]*21
    for seed in range(0,1000):
        f1 = CreateFleet1()
        f2 = CreateFleet2()
        batlle = Combat(seed,[f1,f2])
        battle.HitLevel=400
        battle.RunCombat(run_one_step=False)
        out = battle.OutFleets[0]
        
        #print out.PlayerID,out.Ships
        if out.PlayerID == 1:
            distrib[0] += 1
        else:
            distrib[out.Ships] += 1
    idx = range(0,21)
    print "*" * 20
    for (i,val) in zip(idx,distrib):
        print i,val
        
        
        




if __name__ == '__main__':
    main()





