import pygame
import socket
import _thread as thread
import hashlib
import atexit
import pickle

pygame.init()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Hosting server at ", socket.gethostbyname(socket.gethostname()))
server.bind((socket.gethostbyname(socket.gethostname()), 1782))
server.listen(2)

class State:
    def __init__(self):
        self.connections = {}
        self.connection_no = 1
        self.player_data = {}
        self.player_locations = []
        self.pickled_data = None

state = State()

def remove_user(sock,players):
    state.player_data.pop(sock)
    players.pop(sock)
    sock.shutdown(2)
    sock.close()

def main_thread():
    while True:
        state.player_locations = list(state.player_data.values())
        for player_no in range(len(state.player_locations)):
            state.player_locations[player_no][0] = (state.player_locations[player_no][0][0]+state.player_locations[player_no][2][0], state.player_locations[player_no][0][1]+state.player_locations[player_no][2][1])
            state.player_locations[player_no] = [state.player_locations[player_no][0],state.player_locations[player_no][1],state.player_locations[player_no][3]]            

        try:
            for clientsocket in state.connections:
                try:
                    state.pickled_data = pickle.dumps(state.player_locations,protocol = pickle.HIGHEST_PROTOCOL)+"^&^".encode()
                    clientsocket.send(state.pickled_data)
                except ConnectionResetError or OSError:
                    pass
        except RuntimeError:
            pass
            
def handle_client(clientsocket, addr, players):
    while True:
        try:
            data = clientsocket.recv(4096)
            try:
                player = pickle.loads(data)
                
            except pickle.UnpicklingError:
                print("unpickling error")

            try:
                state.player_data[clientsocket] = [state.player_data[clientsocket][0],player[0],player[1],player[2]]
            except KeyError:
                state.player_data[clientsocket] = [(590,290),player[0],player[1],player[2]]
                
        except ConnectionResetError:
            remove_user(clientsocket,state.connections)
            break

##        clientsocket.send(pickle.dumps(state.player_locations))

thread.start_new_thread(main_thread, ())

while True:
    try:
        connection, address = server.accept()
        print("Connection from", address)
        state.connections[connection] = state.connections,state.connection_no
##        connection.send(("Connected "+str(state.connections[connection][1])).encode())
        try:
            thread.start_new_thread(handle_client, (connection, address, state.connections))
            state.connection_no+=1
        except:
            pass

    except KeyboardInterrupt:
        server.close()
        
server.close()
