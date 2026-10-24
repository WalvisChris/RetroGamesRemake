from dataclasses import dataclass, field
from lib.PS5 import PS5controller
import pygame
import math
import sys

@dataclass
class Display:
    virtual_width: int = 320
    virtual_height: int = 240
    scale_factor: int = 3

@dataclass
class Sprites:
    background: pygame.Surface
    tile_grass: pygame.Surface
    tile_path_dark: pygame.Surface
    tile_path_light: pygame.Surface

def load_sprites():
    SPRITE_PATH = "resources/re/images/"
    return Sprites (
        background = pygame.image.load(f"{SPRITE_PATH}bg.png").convert(),
        tile_grass = pygame.image.load(f"{SPRITE_PATH}tile-grass.png").convert_alpha(),
        tile_path_dark = pygame.image.load(f"{SPRITE_PATH}tile-path-dark.png").convert_alpha(),
        tile_path_light = pygame.image.load(f"{SPRITE_PATH}tile-path-light.png").convert_alpha(),
    )

@dataclass
class Camera:
    position_x: float = -150.0
    position_y: float = 50.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0

@dataclass
class Structure:
    sprite: pygame.Surface

@dataclass
class Grid:
    grid_size: int = 29
    tile_width: int = 23 # pixels
    tile_height: int = 12 # pixels
    tiles: list[list[Structure]] = field(init=False)
    def __post_init__(self):
        self.tiles = starting_grid(self.grid_size)

def starting_grid(size):
    sprite = load_sprites()
    
    tiles = []
    for y in range(size):
        row = []
        for x in range(size):
            if x in [0, 1, size-1, size] or y in [0, 1, size-1, size]:
                row.append(Structure(sprite.tile_path_dark))
            elif x in [2, 3, 4, 5, size-2, size-3, size-4, size-4] or y in [2, 3, 4, 5, size-2, size-3, size-4, size-4]:
                row.append(Structure(sprite.tile_path_light))
            else:
                row.append(Structure(sprite.tile_grass))
        tiles.append(row)
        
    return tiles

def render_pipeline(screen, sprite, grid, camera):
    screen.blit(sprite.background, (0, 0))

    for y, row in enumerate(grid.tiles):
        for x, tile in enumerate(row):
            x_pos = (x * (grid.tile_width / 2)) - (y * (grid.tile_width / 2))
            y_pos = (y * (grid.tile_height / 2)) + (x * (grid.tile_height / 2))
            x_pos -= camera.position_x
            y_pos -= camera.position_y
            screen.blit(tile.sprite, (x_pos, y_pos))

def start(screen, window, clock, joystick):
    # PS5 controller
    controller = PS5controller(joystick)

    # load
    sprite = load_sprites()

    # starting values
    camera = Camera()
    grid = Grid()

    # window scaling
    scaled_width = Display.virtual_width * Display.scale_factor
    scaled_height = Display.virtual_height * Display.scale_factor
    
    isPlaying = True
    while isPlaying:
        # Input - Keyboard
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    isPlaying = False

        # Input - Controller
        controller.input.Update()
        if abs(controller.input.L.x) > 0:
            camera.velocity_x += 0.5 * controller.input.L.x
        if abs(controller.input.L.y) > 0:
            camera.velocity_y += 0.5 * controller.input.L.y

        if controller.input.OPTIONS.down:
            isPlaying = False

        # Logic - Camera
        camera.velocity_x *= 0.85
        camera.velocity_y *= 0.85
        camera.position_x += camera.velocity_x
        camera.position_y += camera.velocity_y

        # Rendering
        render_pipeline(screen, sprite, grid, camera)

        upscaled = pygame.transform.scale(screen, (scaled_width, scaled_height))
        window.blit(upscaled, (0, 0))
        
        pygame.display.flip()

        milliseconds_passed = clock.tick(60)