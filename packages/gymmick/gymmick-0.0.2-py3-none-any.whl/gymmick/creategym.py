import pygame
from gym import Env
import numpy as np

class CustomEnv(Env):
    def __init__(self, action_space, observation_space, length, _handler, scr=False, **kwargs):
        self.members = []
        self.action_space = action_space
        self.observation_space = observation_space
        self.length = [length]
        self._handler = _handler
        if scr!=False:
            pygame.init()
            self.screen_h, self.screen_w = scr
            self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        self.optional_args = {key: [value] for (key, value) in kwargs.items()}
        self._initial_length = [length]
        self._optional_args_original = {key: [value] for (key, value) in kwargs.items()}
    def step(self, action):
        observation, reward, done, info = self._handler(action, self.members, self.length, self.optional_args)
        observation = np.array(observation)
        return observation, reward, done, info
    def reset(self):
        self.length[0] = self._initial_length[0]
        self.members.clear()
        for key in self.optional_args.keys():
            self.optional_args[key][0] = self._optional_args_original[key][0]
    def render(self):
        if self.scr != False:
            for e in pygame.event.get():   
                if e.type == pygame.QUIT:
                    break
            self.screen.fill((0, 0, 0))
            for member in self.members:
                if isinstance(member, Circle):
                    pygame.draw.circle(self.screen, member.color, (member.x, member.y), member.r)
                else:
                    pygame.draw.rect(self.screen, member.color, (member.x, member.y, member.w, member.h))
            pygame.display.update()    
        else:
            raise ValueError("Environment has not been instantiated with screen, and therefore cannot be rendered.")
    def add_member(self, member):
        if not isinstance(member, Circle) and not isinstance(member, Rect):
            raise ValueError("Member is not identifiable")
        else:
            self.members.append(member)
    # Testing...
    def _get_args(self):
        return self.members, self.optional_args

class Circle:
    def __init__(self, x, y, r, vx, vy, m, color):
        self.x = x
        self.y = y
        self.r = r
        self.vx = vx
        self.vy = vy
        self.m = m
        self.color = color
    def change_attr(self, x = None, y = None,  r = None, vx = None, vy = None, m = None, color = None):
        if x!=None: self.x = x
        if y!=None: self.y = y
        if r!=None: self.r = r
        if vx!=None: self.vx = vx
        if vy!=None: self.vy = vy
        if m!=None: self.m = m
        if color!=None: self.color = color

class Rect:
    def __init__(self, x, y, w, h, vx, vy, m, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = vx
        self.vy = vy
        self.m = m
        self.color = color
    def change_attr(self, x = None, y = None, w = None, h = None, vx = None, vy = None, m = None, color = None):
        if x!=None: self.x = x
        if y!=None: self.y = y
        if w!=None: self.w = w
        if h!=None: self.h = h
        if vx!=None: self.vx = vx
        if vy!=None: self.vy = vy
        if m!=None: self.m = m
        if color!=None: self.color = color