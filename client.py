import pygame
import socket
import _thread as thread
import atexit
import pickle
import math

pygame.init()
pygame.font.init()

class Slider:
    def __init__(self,r,cp):
        self.rect = r
        self.start= self.rect.center[0]
        self.finish = self.start+254
        self.colour_position = cp
        self.colour = (0,0,0)

    def on_hold(self):
        if pygame.mouse.get_pos()[0] > self.start and pygame.mouse.get_pos()[0] <= self.finish:
            self.rect.center = (pygame.mouse.get_pos()[0],self.rect.center[1])

        elif pygame.mouse.get_pos()[0] > self.finish:
            self.rect.center = (self.finish,self.rect.center[1])

        else:
            self.rect.center = (self.start,self.rect.center[1])

        if self.colour_position == 0:
            self.colour = (self.rect.center[0]-497,0,0)

        elif self.colour_position == 1:
            self.colour = (0,self.rect.center[0]-497,0)

        elif self.colour_position == 2:
            self.colour = (0,0,self.rect.center[0]-497)

        state.colour = (state.sliders[0].rect.center[0]-497,state.sliders[1].rect.center[0]-497,state.sliders[2].rect.center[0]-497)

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
            renderer.screen.blit(renderer.font.render(self.text,False,(255-self.colour[0],255-self.colour[1],255-self.colour[2])),(self.rect.center[0]-len(self.text)*4,self.rect.top,self.rect.width,self.rect.height))

        else:
            pygame.draw.rect(renderer.screen,(255-self.colour[0],255-self.colour[1],255-self.colour[2]),self.rect)
            pygame.draw.rect(renderer.screen,(0,0,0),self.rect,1)
            renderer.screen.blit(renderer.font.render(self.text,False,self.colour),(self.rect.center[0]-len(self.text)*4,self.rect.top,self.rect.width,self.rect.height)
)
class State:
    def __init__(self):
        self.player = [(),(),""]
        self.players = []
        self.buttons = []
        self.sliders = []
        self.connecting_stage = 0
        self.main_menu = True
        self.player_name = ""
        self.inputting_name = False
        self.inputting_ip = False
        self.selecting_colour = False
        self.ip = ""
        self.default_ip = "192.168.1.73"
        self.colour = (0,0,0)
        self.slider_selected = -1
        self.total_colour_rect = pygame.Rect(640,150,20,20)
        self.message = ""
        self.typing_bar = ""
        self.typing = False
        self.player_message = ""
        self.message_timer = 0
        self.id_it = 0
        self.inputs = [0,0]
        self.player_id = -1
        self.player_it = False
        self.gamemode = "dark"
        self.screen_colour = (255,255,255)
        self.player_location = (0,0)
        self.temp_player = None

##  Starts the connection process  
    def begin_connect(self):
        for button in self.buttons:
            if button.main_menu:
                button.visible = not button.visible
        state.inputting_name = True
        self.player = [(255,0,0),(0,0),self.player_name]

    def next_connection_step(self):
        self.connecting_stage += 1
        if self.connecting_stage == 1:
            self.inputting_name = False
            self.inputting_ip = True
            
                    
        if self.connecting_stage == 2:
            self.inputting_ip = False
            self.selecting_colour = True

        if self.connecting_stage == 3:
            self.selecting_colour = False
            self.main_menu = False
            self.player = [self.colour,self.inputs,self.player_name]
            for button in self.buttons:
                if button.main_menu:
                    button.visible = False
                    
            self.connect_to_server()
        
        

    def create_buttons(self):
        self.connect_button = Button(True,pygame.Rect(590,270,60,20),(0,200,255),"Connect",self.begin_connect,True)
        self.next_button = Button(True,pygame.Rect(590,270,60,20),(0,100,255),"Next",self.next_connection_step,False)
        self.buttons.append(self.next_button)
        self.buttons.append(self.connect_button)

        self.red_slider = Slider(pygame.Rect(488,180,20,20),0)
        self.green_slider = Slider(pygame.Rect(488,210,20,20),1)
        self.blue_slider = Slider(pygame.Rect(488,240,20,20),2)
        self.sliders.append(self.red_slider)
        self.sliders.append(self.green_slider)
        self.sliders.append(self.blue_slider)

## Connects to the server
    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ##self.client.connect(("172.16.192.170", 1782))
        if state.ip.count(".") == 3:            
            self.client.connect((state.ip, 1782))
            thread.start_new_thread(print_data,(self.client,))

        else:
            self.client.connect((state.default_ip, 1782))
            thread.start_new_thread(print_data,(self.client,))

        try:
            self.player_id = int(self.client.recv(1).decode())
            
        except:
            print("Error on recieving ID: Please reconnect")
            pygame.quit()
            
        print("Connected")
        
        
class Renderer:
    def __init__(self):
        self.screen = pygame.display.set_mode((1200,600))
        self.font = pygame.font.SysFont("Comic Sans MS", 15)

    def render(self):
        self.screen.fill((state.screen_colour))

        if not state.main_menu:
            for player in state.players:
                if player[4] == state.player_id:
                    state.player_location = player[0]
                    break

            if state.gamemode == "dark":
                if not state.player_it:
                    pygame.draw.circle(self.screen,(255,255,255),(int(state.player_location[0]+10),int(state.player_location[1]+10)),100)
            
            for player in state.players:
                if state.gamemode == "dark":
                    if math.sqrt((player[0][0]-state.player_location[0])**2+(player[0][1]-state.player_location[1])**2) <= 100:
                        pygame.draw.rect(self.screen,player[1],pygame.Rect(player[0][0],player[0][1],20,20))
                        pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(player[0][0],player[0][1],20,20),1)
                        if player[0][1] < 20:
                            self.screen.blit(self.font.render(player[2],False,(0,0,0)),(player[0][0]-len(player[2])*2.5,player[0][1]+20))
                            if player[4] == state.id_it:
                                self.screen.blit(self.font.render("It",False,(255,0,0)),(player[0][0]+2,player[0][1]+33))
                                
                        else:
                            self.screen.blit(self.font.render(player[2],False,(0,0,0)),(player[0][0]-len(player[2])*2.5,player[0][1]-20))
                            if player[4] == state.id_it:
                                self.screen.blit(self.font.render("It",False,(255,0,0)),(player[0][0]+2,player[0][1]-33))
                    
                if state.gamemode == "light" or state.player_it:
                    pygame.draw.rect(self.screen,player[1],pygame.Rect(player[0][0],player[0][1],20,20))
                    pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(player[0][0],player[0][1],20,20),1)
                    if player[0][1] < 20:
                        self.screen.blit(self.font.render(player[2],False,(0,0,0)),(player[0][0]-len(player[2])*2.5,player[0][1]+20))
                        if player[4] == state.id_it:
                            self.screen.blit(self.font.render("It",False,(255,0,0)),(player[0][0]+2,player[0][1]+33))
                            
                    else:
                        self.screen.blit(self.font.render(player[2],False,(0,0,0)),(player[0][0]-len(player[2])*2.5,player[0][1]-20))
                        if player[4] == state.id_it:
                            self.screen.blit(self.font.render("It",False,(255,0,0)),(player[0][0]+2,player[0][1]-33))

        

        for button in state.buttons:
            if button.visible:
                button.render()

        if state.inputting_name:
            self.screen.blit(self.font.render("Name: " + state.player_name + "|",False,(0,0,0)),(560,200))

        elif state.inputting_ip:
            self.screen.blit(self.font.render("IP: " + state.ip + "|",False,(0,0,0)),(560,200))
            self.screen.blit(self.font.render("Default IP: " + state.default_ip ,False,(0,0,0)),(560,220))

        elif state.selecting_colour:
            self.screen.blit(self.font.render("Colour: ",False,(0,0,0)),(590,150))
            pygame.draw.rect(self.screen,state.colour,state.total_colour_rect)
            pygame.draw.rect(self.screen,(0,0,0),state.total_colour_rect,1)
            for slider in state.sliders:
                pygame.draw.line(self.screen, slider.colour, (slider.start,slider.rect.center[1]), (slider.finish,slider.rect.center[1]))
                pygame.draw.rect(self.screen,slider.colour,slider.rect)
                
        elif state.typing:
            pygame.draw.rect(self.screen,(255,255,255),pygame.Rect(0,550,1200,50))
            pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(0,550,1200,50),1)
            self.screen.blit(self.font.render(state.player_name + ": " + state.message,False,(0,0,0)),(0,550))


renderer = Renderer()
state = State()
state.create_buttons()

def exit_handler():
    state.client.close()
    
atexit.register(exit_handler)

def print_data(client):
        while True:
            data = client.recv(1024)
            try:
                for players in data.split("^?^".encode()):
                    if "£".encode() in players and "!".encode() in players:
                        state.temp_player = players.strip("!".encode()).strip("£".encode()).strip("^".encode()).strip("?".encode())
                        if "£".encode() not in state.temp_player and  "!".encode() not in state.temp_player and  "^".encode() not in state.temp_player and  "?".encode() not in state.temp_player:
                            state.players = pickle.loads(state.temp_player)
                            break
                        
            except pickle.UnpicklingError:
                print("Error")
                pass

            if len(state.players) != 0:
                state.id_it = state.players[0][3]
                
            if state.message_timer != 0:
                state.message_timer -= 1
            
        

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

##Checks if a slider is being clicked on if on the right stage and sets the current slider selected to the one being clicked on            
            if state.selecting_colour:
                for slider in state.sliders:
                    if slider.rect.collidepoint(pygame.mouse.get_pos()):
                        state.slider_selected = state.sliders.index(slider)

##When the player stops holding down the mouse the slider selected is unselected               
        elif event.type == pygame.MOUSEBUTTONUP:
            state.slider_selected = -1
        
        elif event.type == pygame.KEYDOWN:
            if state.inputting_name:
                if len(state.player_name) < 16:
##  Detects if backspace is pressed,if it is it deletes the last character    
                    if event.key == 8 and len(state.player_name) != 0:
                       state.player_name = state.player_name[:-1]
##  Checks if the player enters a number
                    if event.key == 46 or event.key >= 48 and event.key <= 57:
                        state.player_name = state.player_name + pygame.key.name(event.key)
                   
## Detects if the player enters a character
                    elif event.key >= 97 and event.key <= 122:
                        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                            state.player_name = state.player_name + pygame.key.name(event.key).upper()
                        else:
                            state.player_name = state.player_name + pygame.key.name(event.key)
                        
##Checks if the player enters a space
                    elif event.key == 32:
                        state.player_name = state.player_name + " "
                    
            elif state.inputting_ip:
                if event.key == 8 and len(state.ip) != 0:
                    state.ip = state.ip[:-1]

                if event.key == 46 or event.key >= 48 and event.key <= 57:
                    state.ip = state.ip + pygame.key.name(event.key)
                
            if not state.main_menu:
##              Checks if the player presses enter, and sets the message or resets velocity, also makes the user begin typing  
                if event.key == 13:
                    if state.typing:
                        state.player_message = ": " + state.message
                        state.message = ""
                        state.message_timer = 100000
                    state.typing = not state.typing
                    
                elif state.typing:
                    if event.key == 8 and len(state.message) != 0:
                        state.message = state.message[:-1]

                    if event.key == 46 or event.key >= 48 and event.key <= 57:
                        state.message += pygame.key.name(event.key)
                        
                    elif event.key >= 97 and event.key <=122 and len(state.message) <= 50:
                        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                            state.message += pygame.key.name(event.key).upper()
                        else:
                            state.message += pygame.key.name(event.key)

                    elif event.key == 32 and len(state.message) <= 50:
                        state.message = state.message + " "
                            
                    
                else:
                    if event.key == pygame.K_d:
                        state.inputs[0] += 1

                    if event.key == pygame.K_a:
                        state.inputs[0] -= 1

                    if event.key == pygame.K_s:
                        state.inputs[1] += 1

                    if event.key == pygame.K_w:
                        state.inputs[1] -= 1

        elif event.type == pygame.KEYUP:
            if not state.main_menu:
                if event.key == pygame.K_d:
                    state.inputs[0] -= 1

                if event.key == pygame.K_a:
                    state.inputs[0] += 1

                if event.key == pygame.K_s:
                    state.inputs[1] -= 1

                if event.key == pygame.K_w:
                    state.inputs[1] += 1

        if 1 not in pygame.key.get_pressed():
            state.inputs = [0,0]
            
    state.player = [state.colour,state.inputs,state.player_name]
    state.player[2] = state.player_name + state.player_message

    if state.slider_selected != -1:
        state.sliders[state.slider_selected].on_hold()

##  Sends the player data to the server
    if not state.main_menu:
        state.client.send(pickle.dumps(state.player,protocol = pickle.HIGHEST_PROTOCOL))

    if state.message_timer == 0:
        state.player_message = ""

    if state.main_menu:
        for button in state.buttons:
            if button.visible:
                if button.rect.collidepoint(pygame.mouse.get_pos()):    
                    button.hovering = True

                else:
                    button.hovering = False

    if len(state.players) >0:
        state.gamemode = state.players[0][-1]
        if state.players[0][3] == state.player_id:
            state.player_it = True
            if state.gamemode == "dark":
                state.screen_colour = (255,255,255)
            
        else:
            state.player_it = False
            if state.gamemode == "dark":
                state.screen_colour = (0,0,0)
while True:
    renderer.render()
    input_getter()
    pygame.display.flip()
