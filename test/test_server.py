import sys
sys.path.append("..")
from serveroop import UDP_server_side as server

server=server("localhost",8888)
server.run()
