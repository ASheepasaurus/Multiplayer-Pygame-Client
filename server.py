import pygame
import socket
import _thread as thread
import hashlib
import atexit
import pickle
import random

pygame.init()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Hosting server at ", socket.gethostbyname(socket.gethostname()))
server.bind((socket.gethostbyname(socket.gethostname()), 1782))
server.listen(2)

class State:
    def __init__(self):
        self.connections = {}
        self.player_data = {}
        self.connection_to_id = {}
        self.id_to_connection = {}
        self.available_connections = [1,2,3,4,5,6,7,8]
        self.used_connections = []
        self.player_locations = []
        self.pickled_data = None
        self.id = -1
        self.id_it = 1
        self.game_speed = 0.05
        self.gamemode = "dark"

state = State()

def remove_user(sock,players):
    print(sock.getpeername()[0], "has disconnected")
    state.available_connections.append(state.connection_to_id[sock])
    state.used_connections.remove(state.connection_to_id[sock])
    state.player_data.pop(state.connection_to_id[sock])
    state.id_to_connection.pop(state.connection_to_id[sock])
    state.connection_to_id.pop(sock)
    players.pop(sock)
    sock.shutdown(2)
    sock.close()

def main_thread():
    while True:
        state.player_locations = list(state.player_data.values())
        for player_no in range(len(state.player_locations)):
##          Sets the players velocity = -1,0 or 1 * the game speed depending on if the user is moving left,right or stationary, the same for the y 
            state.player_locations[player_no][2]  = ((state.player_locations[player_no][2][0] and (1,-1)[state.player_locations[player_no][2][0] < 0]) * state.game_speed , (state.player_locations[player_no][2][1] and (1,-1)[state.player_locations[player_no][2][1] < 0])* state.game_speed ) 
##          Sets the players location = (it's x location plus the x velocity, it's y location plus it's y velocity)
            state.player_locations[player_no][0] = (state.player_locations[player_no][0][0]+state.player_locations[player_no][2][0], state.player_locations[player_no][0][1]+state.player_locations[player_no][2][1])

            if state.player_locations[player_no][0][0] <0:
                state.player_locations[player_no][0] = (0,state.player_locations[player_no][0][1])

            elif state.player_locations[player_no][0][0] > 1180:
                state.player_locations[player_no][0] = (1180,state.player_locations[player_no][0][1])

            if state.player_locations[player_no][0][1] < 0:
                state.player_locations[player_no][0] = (state.player_locations[player_no][0][0],0)

            elif state.player_locations[player_no][0][1] > 580:
                state.player_locations[player_no][0] = (state.player_locations[player_no][0][0],580)
                
            state.player_locations[player_no] = [state.player_locations[player_no][0],state.player_locations[player_no][1],state.player_locations[player_no][3],state.player_locations[player_no][4],state.player_locations[player_no][6]]

        if len(state.used_connections) != 0:
##          When no player is it, picks a random one to be it          
            if state.id_it in state.available_connections:
                state.id_it = state.used_connections[random.randint(0,len(state.used_connections)-1)]
                
##      Detects when tug player collides with another, if the other player hasn't been tug recently, it passes it on
        for player in state.player_locations:
            if player[3] == player[4]:
                for player_2 in state.player_locations:
                    if player_2[3] != player_2[4]:
                        if pygame.Rect(player[0][0],player[0][1],20,20).colliderect(pygame.Rect(player_2[0][0],player_2[0][1],20,20)) and state.player_data[player_2[4]][5] == 0:                            
                            state.id_it = player_2[4]
                            state.player_data[player[4]][5] = 5000
                        break
                break
            
##      Decreases the time until a player can be tug again
        for player in state.player_data:
            if state.player_data[player][5] != 0:
                state.player_data[player][5] -= 1
                
        try:
            for clientsocket in state.connections:
                try:
                    state.pickled_data = "^&^*".encode() + pickle.dumps(state.player_locations,protocol = pickle.HIGHEST_PROTOCOL) + "£".encode()
                    clientsocket.send(state.pickled_data)
                    
                except ConnectionResetError or OSError or ConnectionAbortedError:
                    pass
                
        except RuntimeError or OSError:
            pass

def handle_client(clientsocket,_id, addr, players):
    while True:
        try:
            data = clientsocket.recv(4096)
            try:
                player = pickle.loads(data)
                
            except pickle.UnpicklingError:
                print("unpickling error")

            try:                                                       
                state.player_data[_id] = [state.player_data[_id][0],player[0],player[1],player[2],state.id_it,state.player_data[_id][5],_id]

            except KeyError:
                state.player_data[_id] = [(590,290),player[0],player[1],player[2],state.id_it,0,_id]
                
        except ConnectionResetError:
            remove_user(clientsocket,state.connections)
            break

thread.start_new_thread(main_thread, ())

while True:
    if len(state.available_connections) != 0:
        try:
            connection, address = server.accept()
            print("Connection from", address)
            state.connections[connection] = state.connections

            try:
                state.id = state.available_connections[random.randint(0,len(state.available_connections))]
                thread.start_new_thread(handle_client, (connection, state.id, address, state.connections))
                state.available_connections.remove(state.id)
                state.used_connections.append(state.id)
                state.connection_to_id[connection] = state.id
                state.id_to_connection[state.id] = connection
                
               
            except:
                print("error")
                
            connection.send(str(state.id).encode())
                
        except KeyboardInterrupt:
            server.close()
        
server.close()
