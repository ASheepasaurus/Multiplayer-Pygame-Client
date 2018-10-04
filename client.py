import pygame
import socket
import _thread as thread
import atexit
import pickle
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("172.16.192.170", 1782))
pygame.init()
pygame.font.init()
        
class State:
    def __init__(self):
        self.player = [(255,255,0),(0,0),"A Sheep"]
        self.players = []
        self.velocity_x = 0
        self.velocity_y = 0

class Renderer:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000,600))
        self.font = pygame.font.SysFont("Comic Sans MS", 15)

    def render(self):
        self.screen.fill((255,255,255))

        for player in state.players:
            pygame.draw.rect(self.screen,player[1],player[0])
            self.screen.blit(self.font.render(player[2],False,(0,0,0)),(player[0].left-len(player[2])*2.5,player[0].top-20))


renderer = Renderer()
state = State()

def exit_handler():
    global client
    client.close()
atexit.register(exit_handler)

def print_data(client):
    while True:
        data = client.recv(4096)
        try:
            state.players = pickle.loads(data)
        except pickle.UnpicklingError:
            print("Unpickling Error")
        

def input_getter():
##    state.player[0].left += state.velocity_x
##    state.player[0].top += state.velocity_y
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_d:
                state.velocity_x += 1

            if event.key == pygame.K_a:
                state.velocity_x -= 1

            if event.key == pygame.K_s:
                state.velocity_y += 1

            if event.key == pygame.K_w:
                state.velocity_y -= 1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                state.velocity_x -= 1

            if event.key == pygame.K_a:
                state.velocity_x += 1

            if event.key == pygame.K_s:
                state.velocity_y -= 1

            if event.key == pygame.K_w:
                state.velocity_y += 1

    state.player[1] = (state.velocity_x,state.velocity_y)
                
    client.send(pickle.dumps(state.player))            

thread.start_new_thread(print_data,(client,))


while True:
    renderer.render()
    input_getter()
    pygame.display.flip()
