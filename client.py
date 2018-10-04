import pygame
import socket
import _thread as thread
import atexit
import pickle

pygame.init()
pygame.font.init()


class Button:
    def __init__(self,m,r,c,t,co,v):
        self.main_menu = m
        self.rect = r
        self.colour = c
        self.text = t
        self.command = co
        self.visible = v
        self.hovering = False

    def render(self):
        if not self.hovering:
            pygame.draw.rect(renderer.screen,self.colour,self.rect)
            pygame.draw.rect(renderer.screen,(0,0,0),self.rect,1)
            renderer.screen.blit(renderer.font.render(self.text,False,(0,0,0)),(self.rect))
        else:
            print("hovering")

class State:
    def __init__(self):
        self.player = [(),(),""]
        self.players = []
        self.buttons = []
        self.velocity_x = 0
        self.velocity_y = 0
        self.connecting_stage = 0
        self.main_menu = True
        self.player_name = ""
        self.inputting_name = False
        self.ip = "192.168.1.73"

##  Starts the connection process  
    def begin_connect(self):
        for button in self.buttons:
            if button.main_menu:
                button.visible = not button.visible
        state.inputting_name = True
        self.connecting_stage += 1

    def next_connection_step(self):
        if self.connecting_stage == 1:
            state.inputting_name = False
            self.main_menu = False
            self.player = [(255,255,0),(0,0),self.player_name]
           
            for button in self.buttons:
                if button.main_menu:
                    button.visible = False
                    
            self.connect_to_server()
        
        

    def create_buttons(self):
        self.connect_button = Button(True,pygame.Rect(590,270,60,20),(0,200,255),"Connect",self.begin_connect,True)
        self.next_button = Button(True,pygame.Rect(590,270,60,20),(0,100,255),"Next",self.next_connection_step,False)
        self.buttons.append(self.next_button)
        self.buttons.append(self.connect_button)

## Connects to the server
    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ##self.client.connect(("172.16.192.170", 1782))
        self.client.connect((state.ip, 1782))
        thread.start_new_thread(print_data,(self.client,))
        
class Renderer:
    def __init__(self):
        self.screen = pygame.display.set_mode((1200,600))
        self.font = pygame.font.SysFont("Comic Sans MS", 15)

    def render(self):
        self.screen.fill((255,255,255))

        if not state.main_menu:
            for player in state.players:
                pygame.draw.rect(self.screen,player[1],player[0])
                self.screen.blit(self.font.render(player[2],False,(0,0,0)),(player[0].left-len(player[2])*2.5,player[0].top-20))

        for button in state.buttons:
            if button.visible:
                button.render()

        if state.inputting_name:
            self.screen.blit(self.font.render("Name: " + state.player_name,False,(0,0,0)),(560,200))


renderer = Renderer()
state = State()
state.create_buttons()

def exit_handler():
    state.client.close()
    
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

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in state.buttons:
                if state.main_menu and button.main_menu and button.visible:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        button.command()
                
                
        
        if event.type == pygame.KEYDOWN:
            if state.inputting_name:
##  Detects if backspace is pressed,if it is it deletes the last character    
                if event.key == 8 and len(state.player_name) != 0:
                   state.player_name = state.player_name[:-1]
## Detects if the player enters a character
                elif event.key >= 97 and event.key <=122:
                    state.player_name = state.player_name + pygame.key.name(event.key)
##Checks if the player enters a space
                elif event.key == 32:
                    state.player_name = state.player_name + " "
                
            if not state.main_menu:
                if event.key == pygame.K_d:
                    state.velocity_x += 1

                if event.key == pygame.K_a:
                    state.velocity_x -= 1

                if event.key == pygame.K_s:
                    state.velocity_y += 1

                if event.key == pygame.K_w:
                    state.velocity_y -= 1

        if event.type == pygame.KEYUP:
            if not state.main_menu:
                if event.key == pygame.K_d:
                    state.velocity_x -= 1

                if event.key == pygame.K_a:
                    state.velocity_x += 1

                if event.key == pygame.K_s:
                    state.velocity_y -= 1

                if event.key == pygame.K_w:
                    state.velocity_y += 1

    state.player[1] = (state.velocity_x,state.velocity_y)

    if not state.main_menu:
        state.client.send(pickle.dumps(state.player))            

while True:
    renderer.render()
    input_getter()
    pygame.display.flip()
