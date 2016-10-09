"""
client_manual.py


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

from common import mynetwork


class ObserverClientManual(mynetwork.SingleLineMasterClient):
    "Just add some printing"
    def handler_message(self,msg,FileNo):
        print "Receieved '%s' from %i" % (msg,FileNo)
        mynetwork.SingleLineMasterClient.handler_message(self, msg, FileNo)

    def sendmessage(self,FileNo,msg):
        print "Sent %i '%s'" % (FileNo,msg)
        mynetwork.SingleLineProtocolServer.sendmessage(self, FileNo, msg)
        
if __name__ == '__main__':
    client = ObserverClientManual()
    # Have to run this to get the connection set up
    client.network_events() 
    cnt = 0
    client.sendserver("Join-Observer")
    try:
        while True:
            time.sleep(.07)
            option = raw_input("Info? > ")
            client.sendserver("DUMP")
            client.network_events()               
    except:
        traceback.print_exc()
        time.sleep(5)
    


