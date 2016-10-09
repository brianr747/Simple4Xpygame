"""
GUI_ObserverClient.py

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

import pygame

import consoleclient

SCREENSIZE = (1024, 768)
BACKGROUND = (0, 0, 0)


class GUI_ObserverClient(consoleclient.ConsoleObserver):
    def __init__(self):
        super(GUI_ObserverClient, self).__init__()
        self.Font = None
        self.Screen = None

        self.Colors = ((255, 0, 0),
                       (0, 255, 0),
                       (0, 0, 255),
                       (255, 255, 255),
                       (200, 200, 0),
                       (0, 200, 200),
                       )
        self.UnknownColor = (125, 125, 125)

    def main(self):
        pygame.init()
        #        print pygame.display.list_modes(32)
        #        a = raw_input("Hit return")
        self.Screen = pygame.display.set_mode(SCREENSIZE)
        self.Font = pygame.font.SysFont("Courier", 12)
        pygame.display.set_caption("GUI_ObserverClient.py")
        # Have to run this to get the connection set up
        self.Join()
        self.GetStateInfo()
        background = pygame.Surface(self.Screen.get_size())
        background = background.convert()
        background.fill(BACKGROUND)
        self.Screen.blit(background, (0, 0))
        clock = pygame.time.Clock()
        keep_going = True
        cnt = 0
        while keep_going:
            clock.tick()
            cnt += 1
            if cnt % 10 == 0:
                self.CommunicationClient.SendMessage("?STATE")
            if cnt == 100:
                FPS = clock.get_fps()
                print "FPS =", FPS
                cnt = 0
            self.CommunicationClient.DoNetwork()
            # Wait is less accurate than other timers, _BUT_ it actually
            # sleeps the process, so that we keep our CPU usage bounded.
            pygame.time.wait(30)
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keep_going = False
                    # if event.type == pygame.MOUSEBUTTONDOWN:
                    #     if event.button == 1:
                    #         self.HandleLMouseDn(event.pos)
                    #         continue
                    #     elif event.button == 3:
                    #         self.HandleRMouseDn(event.pos)
                    #         continue

            self.Screen.blit(background, (0, 0))
            self.RenderPlanets()
            pygame.display.flip()

    def RenderPlanets(self):
        if self.Font is None:
            return
        msg = self.State + "  Client to observe game. Once started, mouse buttons cycle through players' views. SPACE = view hyperspace"
        label = self.Font.render(msg, 0, (255, 255, 0))
        self.Screen.blit(label, (10, 10))
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            for f in self.FleetList:
                if not f.AtPlanetID == -1:
                    continue
                ID = f.PlayerID
                if ID is None:
                    color = self.UnknownColor
                else:
                    color = self.Colors[ID]
                label = self.Font.render(str(f.Ships), 0, color)
                pos = self.mapxy(f)
                self.Screen.blit(label, pos)
            return
        for p in self.PlanetList:
            ID = p.PlayerID
            if ID is None:
                color = self.UnknownColor
            else:
                color = self.Colors[ID]
            prod = p.Production
            if prod is None:
                prod = ""
            else:
                prod = " [%.0f]" % (prod,)
            ships = ''
            for f in self.FleetList:
                if f.AtPlanetID == p.ID:
                    ships = str(f.Ships)
            msg = p.PlanetCode + prod + ships
            label = self.Font.render(msg, 0, color)
            pos = self.mapxy(p)
            self.Screen.blit(label, pos)
        # for f in self.FleetList:
        #     ID = f.PlayerID
        #     if ID is None:
        #         color = self.UnknownColor
        #     else:
        #         color = self.Colors[ID]
        #     label = self.Font.render(str(f.Ships), 0, color)
        #     pos = self.mapxy(f)
        #     self.Screen.blit(label, pos)
        #     # print pos,str(f.Ships),color

    @staticmethod
    def mapxy(obj):
        scaling = 1.5
        pos = (350 + int(scaling * obj.x), 10 + (350 - int(scaling * obj.y)))
        return pos
