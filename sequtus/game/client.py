from __future__ import division

from sequtus.PodSixNet.Connection import connection, ConnectionListener

class Client (ConnectionListener):
    def __init__(self, sim, address, port):
        super(Client, self).__init__()
        self.sim = sim
        self.Connect((address, port))
    
    def quit(self, event=None):
        self.running = False
        connection.Send({'action': 'quit'})
    
    def Network_gamestate(self, data):
        print("gamestate")
    
    def Network_connected(self, data):
        print "connected to the server"
    
    def Network_error(self, data):
        print "error:", data['error'][1]
    
    def Network_disconnected(self, data):
        print "disconnected from the server"
    
    def Network_myaction(data):
        print "myaction:", data
    
    def update(self):
        connection.Pump()
        self.Pump()

