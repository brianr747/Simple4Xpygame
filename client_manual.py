"""
client1.py
"""


import time,traceback

import mynetwork

class ObserverClientManual(mynetwork.SingleLineMasterClient):
    "Just add some printing"
    def handler_message(self,msg,FileNo):
        print "Receieved '%s' from %i" % (msg,FileNo)
        mynetwork.SingleLineMasterClient.handler_message(self,msg,FileNo)

    def sendmessage(self,FileNo,msg):
        print "Sent %i '%s'" % (FileNo,msg)
        mynetwork.SingleLineProtocolServer.sendmessage(self,FileNo,msg)
        
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
    


