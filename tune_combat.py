import combat1

from Game1 import Fleet
from combat1 import Combat



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
        combat = Combat(seed,[f1,f2])
        combat.HitLevel=400
        combat.RunCombat(run_one_step=False)
        out = combat.OutFleets[0]
        
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





