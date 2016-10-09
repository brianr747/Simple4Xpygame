"""
client1.py

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

import time
import traceback

import pygame

from common import mynetwork
from common.fleet import Fleet
from server.game import Planet

BACKGROUND = (0,0,0)
SCREENSIZE = (800,600)
SCREENSIZE = (1024,768)


class ObserverUIClient(mynetwork.SingleLineMasterClient):
    "Just add some printing"
    def __init__(self):
        super(ObserverUIClient,self).__init__()
        self.State = ""
        self.PlayerNumber = 0
        self.PlanetList = []
        self.FleetList = []
        self.Font = None
        self.Colors = ((255,0,0),
                       (0,255,0),
                       (0,0,255),
                       (255,255,255),
                       (200,200,0),
                       (0,200,200),
                       )
        self.UnknownColor = (125,125,125)
    
    def handler_message(self,msg,FileNo):
        #print "Receieved '%s' from %i" % (msg,FileNo)
        if "STATE" in msg.upper():
            old_state = self.State
            self.State = msg
            if not msg == old_state:
                # All updates needed
                self.sendserver("?PLANETS")
                self.sendserver("?FLEETS") 
            return
        if "PLANETS|" == msg[0:8]:
            #pprint(msg.split("|"))
            self.ParsePlanets(msg)
            return
        if "FLEETS|" == msg[0:7]:
            #pprint(msg.split("|"))
            self.ParseFleets(msg)
            return
        
        mynetwork.SingleLineMasterClient.handler_message(self, msg, FileNo)

    def ParsePlanets(self,msg):
        plist = msg.split("|")
        planetinfo = []
        for p in plist:
            if not ";" in p:
                continue         
            planet = Planet.FromString(p)
            planetinfo.append(planet)
        self.PlanetList = planetinfo

    def ParseFleets(self,msg):
        plist = msg.split("|")
        fleetinfo = []
        for f in plist:
            if not ";" in f:
                continue         
            fleet = Fleet.FromString(f)
            fleetinfo.append(fleet)
        self.FleetList = fleetinfo
            
            


    def mapxy(self,obj):
        scaling = 1.5
        pos = (350 + int(scaling*obj.x),10 + (350 - int(scaling*obj.y)))
        return pos

    def RenderPlanets(self):
        if self.Font is None:
            return
        scaling = 4
        for p in self.PlanetList:
            ID =p.PlayerID
            if ID is None:
                color = self.UnknownColor
            else:
                color = self.Colors[ID]
            label = self.Font.render(p.PlanetCode,0,color)
            pos = self.mapxy(p)
            self.Screen.blit(label,pos)
        scaling = 4
        for f in self.FleetList:
            ID =f.PlayerID
            if ID is None:
                color = self.UnknownColor
            else:
                color = self.Colors[ID]
            label = self.Font.render(str(f.Ships),0,color)
            pos = self.mapxy(f)
            self.Screen.blit(label,pos)
            #print pos,str(f.Ships),color
 
            

    def HandleLMouseDn(self, pos):
        self.PlayerNumber +=1
        self.ChangePlayer()

    def HandleRMouseDn(self, pos):
        self.PlayerNumber -=1
        self.ChangePlayer()

    def ChangePlayer(self):
        self.sendserver("OBSERVE_AS=%i" % (self.PlayerNumber,))
        self.sendserver("?PLANETS")
        self.sendserver("?FLEETS") 
        self.PlanetList = []
        self.FleetList = []
        
        


    def sendmessage(self,FileNo,msg):
        #print "Sent %i '%s'" % (FileNo,msg)
        mynetwork.SingleLineProtocolServer.sendmessage(self, FileNo, msg)

    def main(self):
        pygame.init()
##        print pygame.display.list_modes(32)
##        a = raw_input("Hit return")
##        
        self.Screen = pygame.display.set_mode(SCREENSIZE)
        self.Font = pygame.font.SysFont("Courier",12)
        pygame.display.set_caption("ObserverClient1.py")
        # Have to run this to get the connection set up
        self.network_events() 
        cnt = 0
        self.sendserver("Join-Observer")
        self.sendserver("OBSERVE_AS=%i" % (self.PlayerNumber,))

        
        background = pygame.Surface(self.Screen.get_size())
        background = background.convert()
        background.fill(BACKGROUND)
        self.Screen.blit(background, (0,0))
        clock = pygame.time.Clock()
        keepGoing = True
        SleepTime = 5
        
        cnt = 1
        # Need to initialize this...
        FPS = 20
        msg = self.State + "  Client to observe game. Once started, mouse buttons cycle through players' views."
        label = self.Font.render(msg, 0, (255, 255, 0))
        while keepGoing:
            tick = clock.tick()
            cnt = cnt + 1
            # Run this update roughly once per second
            if cnt > FPS:
                FPS = clock.get_fps()
                cnt = 1
                if FPS > 40:
                    SleepTime += 1
                elif FPS < 20:
                    SleepTime = 2
                elif FPS < 35:
                    SleepTime -= 1
                    # Always yield for at least 2 millisecs...
                    SleepTime = max(2,SleepTime)
                sleep_percent = .1*(SleepTime*FPS)  # 100*(t/(1000/FPS))
                self.sendserver("?STATE")
                msg = self.State + "  Client to observe game. Once started, mouse buttons cycle through players' views."
                label = self.Font.render(msg, 0, (255, 255, 0))
            # Wait is less accurate than other timers, _BUT_ it actually
            # sleeps the process, so that we keep our CPU usage bounded.
            pygame.time.wait(SleepTime)
            self.network_events()

            # Process pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.HandleLMouseDn(event.pos)
                        continue
                    elif event.button == 3:
                        self.HandleRMouseDn(event.pos)
                        continue

            self.Screen.blit(background, (0,0))
            self.Screen.blit(label,(10,10))
            self.RenderPlanets()
            pygame.display.flip()


##                    elif event.button == 4:
##                        ZoomIn(event.pos)
##                    else:
##                        ZoomOut(event.pos)
##            
##            
##            self.Sprites.clear(self.Screen, background)
##            # Update/create sprites.
##            # Do after clear, in case one dies...
##            self.update_sprites()
##
##            self.Sprites.update(RenderRatio)
##            self.Sprites.draw(self.Screen)
##            
##            pygame.display.flip()        
##        
        
if __name__ == '__main__':
    client = ObserverUIClient()
    # Have to run this to get the connection set up
    try:
        client.main()
    except:
        traceback.print_exc()
        time.sleep(5)
    


