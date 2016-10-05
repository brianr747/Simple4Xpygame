#!/usr/bin/env python

"""
mynetwork.py:  Network client/server module.
"""

# stdlib imports
import socket, traceback, time,select,threading
from pprint import pprint



host = ''                               # Bind to all interfaces
port = 51423

class Disconnection(ValueError):
    pass



class MySocketWrapper(object):
    "Adds some state information to the socket object"
    def __init__(self,insocket):
        self.InputBuffer = ""
        self.OutputBuffer = ""
        self.Socket = insocket
        self.FileNo = insocket.fileno()
 

    def getdata(self):
        "Get data; assumes select() was called"
        try:
            newdata = self.Socket.recv(4096)
            if len(newdata) == 0:
                raise Disconnection
        except:
            raise Disconnection
        self.InputBuffer += newdata

    def senddata(self):
        "sends data; assumes select was called"
        if len(self.OutputBuffer) == 0:
            return
        try:
            bytes_sent = self.Socket.send(self.OutputBuffer)
        except:
            print traceback.print_exc()
            raise Disconnection
        self.OutputBuffer = self.OutputBuffer[bytes_sent:]


        


def connect(host='localhost',port=51423,family=socket.AF_INET,ttype=socket.SOCK_STREAM):
    Socket = socket.socket(family,ttype)
    Socket.connect((host,port))
    mysock = MySocketWrapper(Socket)
    return mysock
   

class MyServer(object):
    """
    Low level server object. There should be a class object that contains
    this one to implement the actual communication protocol.
    """
    def __init__(self,host='',port=51423,dontlisten = False):
        """
        The dontlisten option is the only strange one. If True, does
        not listen to new connections. (Useless for a server...)
        """
        self.NewClientList = []
        self.WrapperDict = {}
        self.SocketList = []
        self.Lock = threading.Lock()

        # Why have no listening: clients will derive from this class, and won't
        # listen for connections...
        if dontlisten:
            self.listensock = None
            return
        self.listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listensocket.bind((host, port))
        self.listensocket.listen(1)
        # Lock to ensure that NewClientList is protected from threading
        # madness
        t = threading.Thread(target=self.listenfunc,name="ListenThread")
        t.setDaemon(1)
        t.start()

    def listenfunc(self):
        "This thread adds new clients"
        while True:
            try:
                (clientsock,clientaddr) = self.listensocket.accept()
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc()
            print "New connection from ", clientsock.getpeername()
            mysocket = MySocketWrapper(clientsock)
            self.Lock.acquire()
            try:
                self.NewClientList.append(mysocket)
            finally:
                self.Lock.release()

    def connection_handler(self,FileNo):
        pass
    
    def process_events(self):
        event_list = []
        self.Lock.acquire()
        try:
            while len(self.NewClientList) >0:
                mysock = self.NewClientList.pop()
                FileNo = mysock.FileNo
                self.WrapperDict[FileNo] = mysock
                self.SocketList.append(mysock.Socket)
                self.connection_handler(FileNo)
                event_list.append(("connection",FileNo))
        finally:
            self.Lock.release()
        # NOTE: Can't run select on all empty lists.
        if len(self.SocketList) > 0:
            # Check inputs
            infds, outfds, errfds = select.select(self.SocketList, [], [], 0.0)
            if len(infds)>0:
                for s in infds:
                    try:
                        fn = s.fileno()
                        self.WrapperDict[fn].getdata()
                        event_list.append(("read",fn))
                    except Disconnection:
                        retval = self.disconnect(fn)
                        if not retval == 'NOEVENT':
                            event_list.append(("disconnect",fn))
        if len(self.SocketList) > 0:
            # Check outputs
            infds, outfds, errfds = select.select([],self.SocketList, [], 0.0)
            if len(outfds)>0:
                for s in outfds:
                    try:
                        fn = s.fileno()
                        # NOTE: We do not send an event; since the writing
                        # was ordered by the program, it will not do
                        # anything in reaction to an event.
                        # (The only reason would be to log the traffic.)
                        self.WrapperDict[fn].senddata()
                    except Disconnection:
                        self.disconnect(fn)
                        event_list.append(("disconnect",fn))
        return event_list

    def disconnect(self,FileNo):
        """
        This removes the socket object and the wrapper.
        If the wrapper still had information in its buffers,
        too bad, so sad.
        """
        print "Disconnect ",FileNo
        del self.WrapperDict[FileNo]
        i = 0
        while True:
            if i >= len(self.SocketList):
                raise ValueError("No such socket")
            if self.SocketList[i].fileno() == FileNo:
                break
            i += 1
        del self.SocketList[i]

    def senddata(self,FileNo,data):
        self.WrapperDict[FileNo].OutputBuffer += data

    def broadcast(self,data):
        for wrapper in self.WrapperDict.values():
            wrapper.OutputBuffer += data


class SingleLineProtocolServer(MyServer):
    "Adds the protocol to the server"
    def sendmessage(self,FileNo,message):
        if len(message) == 0:
            return
        if not message[-1] == '\n':
            message += '\n'
        self.senddata(FileNo,message)
        #print "SENT MESSAGE>"+message

    def broadcast(self,message):
        #print "BROADCAST>"+message
        if not message[-1] == '\n':
            message += '\n'
        MyServer.broadcast(self,message)

    def process_events(self):
        "This function is being deprecated..."
        events = MyServer.process_events(self)
        # Since we are changing the list, can't iterate
        i = 0
        message_list = []
        while i < len(events):
            e = events[i]
            if e[0] == "read":
                fn = e[1]
                del events[i]
                pos = self.WrapperDict[fn].InputBuffer.rfind('\n')
                if pos == -1:
                    # No endline; ignore
                    continue
                # This probably should be done with regexp...
                msgs = self.WrapperDict[fn].InputBuffer[0:(pos+1)]
                self.WrapperDict[fn].InputBuffer = self.WrapperDict[fn].InputBuffer[(pos+1):]
                msgs = msgs.split('\n')
                # The last member of the split is an empty string; ignore.
                for m in msgs[0:-1]:
                    message_list.append(('message',(fn,m))) 
            else:
                i += 1
        events += message_list
        return events

    def network_events(self):
        """
        Replacement for process_events. Returns nothing, just calls handler functions.
        """
        events = MyServer.process_events(self)
        for (etype,FileNo) in events:
            if etype == 'read':
                wrapper = self.WrapperDict[FileNo]
                pos = wrapper.InputBuffer.rfind('\n')
                if pos == -1:
                    # No endline; incomplete. Ignore
                    continue
                messages = wrapper.InputBuffer[0:(pos+1)]
                # Remove string to be parsed from buffer
                wrapper.InputBuffer = wrapper.InputBuffer[(pos+1):]
                messages = messages.split('\n')
                # The last member is empty; ignore.
                for msg in messages[0:-1]:
                    self.handler_message(msg,FileNo)
            elif etype == 'connection':
                self.handler_connection(FileNo)
            elif etype == 'disconnect':
                self.handler_disconnect(FileNo)
            else:
                raise NotImplementedError("Unrecognized network event")
            
    def handler_message(self,msg,FileNo):
        "Stub for derived classes"
        pass

    def handler_connection(self,FileNo):
        "Stub for derived classes"
        pass

    def handler_disconnect(self,FileNo):
        "Stub for derived classes"
        pass
        
        

hidden_port = 51424

class NoServerError(StandardError):
    pass

class SingleLineMasterClient(SingleLineProtocolServer):
    def __init__(self,serverhost='localhost',serverport=51423):
        # Bind to the localhost loopback host only; use a different
        # port than the server.
        MyServer.__init__(self,host='localhost',port=hidden_port,dontlisten = False)
        try:
            serv = connect(host=serverhost,port=serverport,family=socket.AF_INET,ttype=socket.SOCK_STREAM)
        except:
            raise NoServerError
        self.server_fileno = serv.FileNo
        self.Lock.acquire()
        try:
            self.NewClientList.append(serv)
        finally:
            self.Lock.release()
    def sendserver(self,msg):
        "If we wanr to send a message to the server, the slave clients do not need to know"
        self.sendmessage(self.server_fileno,msg)

    def process_events(self,events = None):
        "Deprecated"
        if events is None:
            events = SingleLineProtocolServer.process_events(self)
        # Since we are changing the list, can't iterate
        i = 0
        message_list = []
        while i < len(events):
            e = events[i]
            if e[0] == "message":
                fn,msg = e[1]
                if fn == self.server_fileno:
                    # Pass on the server message to all slaves
                    fn_list = self.WrapperDict.keys()
                    fn_list.remove(fn)
                    for f in fn_list:
                        self.sendmessage(f,msg)
                else:
                    # Received message from client; relay to server.
                    # Delete from our event list; not aimed for a client.
                    #fn,msg = e[1]
                    self.sendserver(msg)
                    # Option#1: Eliminate the message
                    #del events[i]
                    # i -= 1
                    # Option #2: Replace with an event saying we relayed.
                    events[i] = ("relay",e[1])
            elif e[0] == 'disconnect':
                if e[1] == self.server_fileno:
                    raise NoServerError
            i += 1
        events += message_list
        return events

    def handler_disconnect(self,FileNo):
        "Blow up if we lose our server connection"
        if FileNo == self.server_fileno:
            raise NoServerError

    def handler_message(self,msg,FileNo):
        """
        Relay messages from our slave clients to the server,
        pass server messages to clients
        """
        if FileNo == self.server_fileno:
            # Pass message on to all clients
            for fn in self.WrapperDict.keys():
                if fn == self.server_fileno:
                    continue
                else:
                    self.sendmessage(fn,msg)
            self.handler_server_message(msg)
        else:
            # Received from client, relay
            self.sendserver(msg)

    def handler_server_message(self,msg):
        "Stub for derived classes; should only override this method"
        pass
        
            
    
    
        

class SingleLineSlaveClient(SingleLineProtocolServer):
    def __init__(self):
        MyServer.__init__(self,host='localhost',port=hidden_port,dontlisten = True)
        try:
            serv = connect('localhost',hidden_port,family=socket.AF_INET,ttype=socket.SOCK_STREAM)
        except:
            traceback.print_exc()
            a = raw_input("Hit return")
            raise NoServerError
        self.server_fileno = serv.FileNo
        self.Lock.acquire()
        try:        
            self.NewClientList.append(serv)
        finally:
            self.Lock.release()        
            
    def sendserver(self,msg):
        "If we want to send a message to the server, goes to master client."
        self.sendmessage(self.server_fileno,msg)

    def process_events(self,events = None):
        "If events are passed in, do not create the base messages"
        if events is None:
            events = SingleLineProtocolServer.process_events(self)
        for evnt in events:
            if evnt[0] == 'disconnect':
                raise NoServerError
        return events

    def handler_disconnect(self,FileNo):
        "Lost our connection; blow!"
        raise NoServerError

    def handler_message(self,msg,FileNo):
        "Pass on to the server message handler"
        self.handler_server_message(msg)

    def handler_server_message(self,msg):
        "Stub for derived classes"
        pass
            
     
        

if __name__ == '__main__':
    server = SingleLineProtocolServer()
    #print dir(server)
    cnt = 0

    try:
        while True:
            time.sleep(.05)
            kys = server.WrapperDict.keys()
            cnt += 1
            if cnt == 50:
                for k in kys:
                    server.senddata(k,"HEARTBEAT\n")
                cnt = 0
            x =server.process_events()
            if len(x) > 0:
                pprint(x)
    except:
        traceback.print_exc()
    a = raw_input("hit any key>")


        


##s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
##s.bind((host, port))
##s.listen(1)
##
##while 1:
##    try:
##        clientsock, clientaddr = s.accept()
##    except KeyboardInterrupt:
##        raise
##    except:
##        traceback.print_exc()
##        continue
##
##    raise "blam"
##    # Process the connection
##
##    try:
##        print "Got connection from", clientsock.getpeername()
##        while 1:
##            infds, outfds, errfds = select.select([clientsock], [clientsock], [clientsock], 0.0)
##            if len(outfds):           
##                try:
##                    clientsock.sendall(time.asctime() + "\n")
##                except:
##                    break
##            if len(infds):
##                data = clientsock.recv(4096)
##                if not len(data):
##                    print "BYE!"
##                    break
##                print "-" *20
##                print data
##                print "-"*20
##                print len(data)
##            if len(errfds):
##                raise "BOOM!"
##            time.sleep(.1)
##    except (KeyboardInterrupt, SystemExit):
##        raise
##    except:
##        traceback.print_exc()
##
##    # Close the connection
##
##    try:
##        clientsock.close()
##    except KeyboardInterrupt:
##        raise
##    except:
##        traceback.print_exc()

