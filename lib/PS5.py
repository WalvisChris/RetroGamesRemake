import pygame
import math

class Button:
    def __init__(self):
        self.down: bool = False
        self.pressed: bool = False
        self.flag: bool = False

    def update(self, new_down: bool):
        self.down = new_down
        
        if self.down and not self.flag:
            self.pressed = True
            self.flag = True
        else:
            self.pressed = False
        
        if self.flag and not self.down:
            self.flag = False

class Trigger:
    def __init__(self):
        self.raw: float = 0.0
        self.pressed: bool = False
        self.flag: bool = False

    def update(self, new_raw: float):
        self.raw = new_raw

        if self.raw > 0 and not self.flag:
            self.pressed = True
            self.flag = True
        else:
            self.pressed = False

        if self.flag and not self.raw > 0:
            self.flag = False

class Stick:
    def __init__(self):
        self.deadzone: float = 0.15
        self.x: float = 0.0
        self.y: float = 0.0
        self.radians: float = 0.0
        self.degrees: float = 0.0

    def update(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

        if abs(self.x) < self.deadzone:
            self.x = 0.0
        if abs(self.y) < self.deadzone:
            self.y = 0.0

        if self.x != 0.0 or self.y != 0.0:
            self.radians = math.atan2(-self.y, self.x)
            self.degrees = math.degrees(self.radians)

class PS5controller:
    class InputControls:
        def __init__(self, joystick:pygame.joystick.JoystickType):
            # pygame joystick
            self.joystick = joystick
            
            # Raw
            self.L = Stick()
            self.R = Stick()
            
            # Trigger
            self.L2 = Trigger()
            self.R2 = Trigger()
            
            # Button
            self.CROSS = Button()
            self.CIRCLE = Button()
            self.SQUARE = Button()
            self.TRIANGLE = Button()
            self.SHARE = Button()
            self.PLAYSTATION = Button()
            self.OPTIONS = Button()
            self.L3 = Button()
            self.R3 = Button()
            self.L1 = Button()
            self.R1 = Button()
            self.UP = Button()
            self.DOWN = Button()
            self.LEFT = Button()
            self.RIGHT = Button()
            self.TOUCH = Button()
        
        def Update(self):
            # Stick
            self.L.update(self.joystick.get_axis(0), self.joystick.get_axis(1))
            self.R.update(self.joystick.get_axis(2), self.joystick.get_axis(3))

            # Trigger
            self.L2.update(self.joystick.get_axis(4))
            self.R2.update(self.joystick.get_axis(5))
            
            # Button
            self.CROSS.update(self.joystick.get_button(0))
            self.CIRCLE.update(self.joystick.get_button(1))
            self.SQUARE.update(self.joystick.get_button(2))
            self.TRIANGLE.update(self.joystick.get_button(3))
            self.SHARE.update(self.joystick.get_button(4))
            self.PLAYSTATION.update(self.joystick.get_button(5))
            self.OPTIONS.update(self.joystick.get_button(6))
            self.L3.update(self.joystick.get_button(7))
            self.R3.update(self.joystick.get_button(8))
            self.L1.update(self.joystick.get_button(9))
            self.R1.update(self.joystick.get_button(10))
            self.UP.update(self.joystick.get_button(11))
            self.DOWN.update(self.joystick.get_button(12))
            self.LEFT.update(self.joystick.get_button(13))
            self.RIGHT.update(self.joystick.get_button(14))
            self.TOUCH.update(self.joystick.get_button(15))
    
    def __init__(self, joystick:pygame.joystick.JoystickType):
        self.joystick = joystick
        self.input = self.InputControls(joystick)