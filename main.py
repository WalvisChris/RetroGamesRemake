from dataclasses import dataclass
from lib.PS5 import PS5controller
import pygame
import math
import sys
from games import marshmallow_kingdom, bitzy_blitz

@dataclass
class Display:
    virtual_width: int = 320
    virtual_height: int = 240
    scaled_width: int = virtual_width * 3
    scaled_height: int = virtual_height * 3

@dataclass
class Image:
    background: pygame.Surface
    pointer: pygame.Surface

@dataclass
class Thumbnail:
    SuperMarshmallowKingdom: pygame.Surface
    BitzyBlitz: pygame.Surface
    MonsterCraft: pygame.Surface
    ResortEmpire: pygame.Surface

def load_thumbnails():
    THUMBNAIL_PATH = "resources/images/thumbnail-"
    return Thumbnail(
        SuperMarshmallowKingdom = pygame.image.load(f"{THUMBNAIL_PATH}smk.jpg").convert(),
        BitzyBlitz = pygame.image.load(f"{THUMBNAIL_PATH}bb.jpg").convert(),
        MonsterCraft = pygame.image.load(f"{THUMBNAIL_PATH}mc.jpg").convert(),
        ResortEmpire = pygame.image.load(f"{THUMBNAIL_PATH}re.jpg").convert()
    )

@dataclass
class SFX:
    up: pygame.mixer.Sound
    down: pygame.mixer.Sound

def load_sfx():
    SFX_PATH = "resources/audio/"
    return SFX(
        up = pygame.mixer.Sound(f"{SFX_PATH}scroll-up.mp3"),
        down = pygame.mixer.Sound(f"{SFX_PATH}scroll-down.mp3")
    )

@dataclass
class Color:
    white: tuple = (255, 255, 255)

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

# Controller init
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)

# window
window = pygame.display.set_mode((Display.scaled_width, Display.scaled_height))
pygame.display.set_caption("Retro Gaming Simulation")
virtual_screen = pygame.Surface((Display.virtual_width, Display.virtual_height))

# load sprites
image = Image(
    background = pygame.image.load("resources/images/bg.png").convert(),
    pointer = pygame.image.load("resources/images/pointer.png").convert_alpha()
)

def menu():
    # load
    thumbnail = load_thumbnails()
    index_to_thumbnail = {
        0: thumbnail.SuperMarshmallowKingdom,
        1: thumbnail.BitzyBlitz,
        2: thumbnail.MonsterCraft,
        3: thumbnail.ResortEmpire
    }
    games = 4
    sfx = load_sfx()

    # starting values
    controller = PS5controller(joystick)
    game_index = 0
    
    # main loop
    while True:

        # Input - Keyboard
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game_index = (game_index + (len(games) - 1)) % len(games)
                    sfx.up.play()
                elif event.key == pygame.K_DOWN:
                    game_index = (game_index + 1) % len(games)
                    sfx.down.play()

                elif event.key == pygame.K_RIGHT:
                    if game_index == 0:
                        marshmallow_kingdom.start(virtual_screen, window, clock, joystick)
                    elif game_index == 1:
                        bitzy_blitz.start(virtual_screen, window, clock, joystick)
                
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Input - Controller
        controller.input.Update()
        if controller.input.UP.pressed:
            game_index = (game_index + (games - 1)) % games
            sfx.up.play()
        elif controller.input.DOWN.pressed:
            game_index = (game_index + 1) % games
            sfx.down.play()
        elif controller.input.CROSS.pressed:
            if game_index == 0:
                marshmallow_kingdom.start(virtual_screen, window, clock, joystick)
            elif game_index == 1:
                bitzy_blitz.start(virtual_screen, window, clock, joystick)
        #elif controller.input.OPTIONS.pressed:
        #    pygame.quit()
        #    sys.exit()

        # Rendering
        background: pygame.Surface = index_to_thumbnail[game_index]
        virtual_screen.blit(background, (0, 0))
        scaled_display = pygame.transform.scale(virtual_screen, (Display.scaled_width, Display.scaled_height))
        window.blit(scaled_display, (0, 0))

        # Loop end
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    menu()
