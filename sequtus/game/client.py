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
    
    def Network(self, data):
        # print("Client: %s" % str(data))
        pass
    
    def Network_other(self, data):
        raise Exception("")
    
    def Network_player_number(self, data):
        self.sim.player = data['number']
    
    def Network_error(self, data):
        raise Exception("%s, source: %s" % (data['error'], data['source']))
    
    def update(self):
        connection.Pump()
        self.Pump()

