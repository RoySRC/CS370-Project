'''
    This file is responsible for starting the server
'''

from server import Server

server = Server('192.168.1.10', 8989)
server.start()