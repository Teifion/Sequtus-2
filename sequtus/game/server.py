from __future__ import division

import time
import socket
import multiprocessing

from sequtus.PodSixNet.Channel import Channel
from sequtus.PodSixNet.Server import Server

# class representing a sigle connection with a client
# this can also represent a player
class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        
        # points of the player
        self.points = 0
        self.player_id = 0
    
    def Network(self, data):
        print("Server: %s" % str(data))
    
    def Network_quit(self, data=None):
        self._server.running = False
    
    def Network_move(self, data):
        x, y = int(data['x']), int(data['y'])
        
        self._server.make_move(self.player_id, x, y)
    
    def Network_player_number(self, data):
        print("Recieved player number")

class SequtusServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        
        # Game state
        self.state = [-1 for x in range(9)]
        self.turn = 0
        
        self.users = {} # maps user names to Chat instances
        
        self.timeout = 0
        self.running = True
        
        self.players = []
        
        self._next_update = time.time()
        self._update_delay = 1/30
        
        self.address, self.port = kwargs['localaddr']
        print('Server started at {} at port {}'.format(self.address, str(self.port)))
    
    # function called on every connection
    def Connected(self, player, addr):
        print("Player connected at {}, using port {}".format(addr[0], addr[1]))
        
        # add player to the list
        player.player_id = len(self.players)
        self.players.append(player)
        
        # send to the player their number
        player.Send({'action': 'player_number', 'number': len(self.players)-1})
    
    # this send to all clients the same data
    def send_to_all(self, data):
        [p.Send(data) for p in self.players]
    
    def loop(self, conn):
        """conn is used to send the server information
        from the parent process"""
        
        conn.send("setup complete")
        conn.send(self.address)
        conn.send(self.port)
        
        while self.running:
            self.update(conn)
    
    def update(self, conn):
        if time.time() < self._next_update:
            return
        
        # Update server connection
        self.Pump()
        
        # Check parent process connection
        while conn.poll():
            data = conn.recv()
            cmd, kwargs = data
            
            if cmd == "quit":
                self.running = False
            
            else:
                print("No handler for {}:{}".format(cmd, str(kwargs)))
        
        # What is happening today?
        """SERVER LOGIC GOES HERE"""
        
        self._next_update = time.time() + self._update_delay


def new_server(connection):
    address = socket.gethostbyname(socket.gethostname())
    
    myserver = SequtusServer(localaddr=(address, 31500))
    myserver.loop(connection)

def run_server():
    parent_conn, child_conn = multiprocessing.Pipe()
    
    server_proc = multiprocessing.Process(
        target=new_server,
        args=(child_conn, )
    )
    server_proc.start()
    
    d = parent_conn.recv()
    
    if d != "setup complete":
        parent_conn.send(["quit", {}])
        raise Exception("Unexpected value from parent_conn: {}".format(d))
    
    address = parent_conn.recv()
    port = parent_conn.recv()
    
    return address, port, parent_conn, server_proc


