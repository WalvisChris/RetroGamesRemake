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
    bush: pygame.Surface
    sand: pygame.Surface
    cursor: pygame.Surface
    outline: pygame.Surface

def load_sprites():
    SPRITE_PATH = "resources/re/images/"
    return Sprites (
        background = pygame.image.load(f"{SPRITE_PATH}bg.png").convert(),
        tile_grass = pygame.image.load(f"{SPRITE_PATH}tile-grass.png").convert_alpha(),
        tile_path_dark = pygame.image.load(f"{SPRITE_PATH}tile-path-dark.png").convert_alpha(),
        tile_path_light = pygame.image.load(f"{SPRITE_PATH}tile-path-light.png").convert_alpha(),
        bush = pygame.image.load(f"{SPRITE_PATH}bush.png").convert_alpha(),
        sand = pygame.image.load(f"{SPRITE_PATH}sand.png").convert_alpha(),
        cursor = pygame.image.load(f"{SPRITE_PATH}cursor.png").convert_alpha(),
        outline = pygame.image.load(f"{SPRITE_PATH}outline.png").convert_alpha()
    )

@dataclass
class Camera:
    position_x: float = -150.0
    position_y: float = 50.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0

@dataclass
class Cursor:
    position_x: float = Display.virtual_width / 2
    position_y: float = Display.virtual_height / 2
    tile_x: int = 0
    tile_y: int = 0

@dataclass
class Structure:
    sprite: pygame.Surface
    offset_x: float = 0.0
    offset_y: float = 0.0

@dataclass
class Grid:
    grid_size: int = 29
    tile_width: int = 23 # pixels
    tile_height: int = 12 # pixels
    tiles: list[list[Structure]] = field(init=False)
    def __post_init__(self):
        self.tiles = starting_grid(self.grid_size)

def ring(x, y, rings):
    center = 14
    dist = max(abs(y - center), abs(x - center))
    return dist in rings

def starting_grid(size):
    sprite = load_sprites()
    
    tiles = []
    for y in range(size):
        row = []
        for x in range(size):
            if ring(x, y, [14, 13]):
                row.append(Structure(sprite.tile_path_dark))
            elif ring(x, y, [12, 11, 10, 9]):
                row.append(Structure(sprite.tile_path_light))
            elif ring(x, y, [8]) and (x,y) not in [(22,10), (22,11), (22,12), (22,13)]:
                row.append(Structure(sprite.bush, 0, 12))
            else:
                row.append(Structure(sprite.sand))
        tiles.append(row)
        
    return tiles

def render_pipeline(screen, sprite, grid, camera, cursor):
    screen.blit(sprite.background, (0, 0))

    for y, row in enumerate(grid.tiles):
        for x, tile in enumerate(row):
            x_pos = (x * (grid.tile_width / 2)) - (y * (grid.tile_width / 2))
            y_pos = (y * (grid.tile_height / 2)) + (x * (grid.tile_height / 2))
            x_pos -= camera.position_x
            y_pos -= camera.position_y
            x_pos -= tile.offset_x
            y_pos -= tile.offset_y
            _sprite = sprite.outline if (x,y) == (cursor.tile_x, cursor.tile_y) else tile.sprite
            screen.blit(_sprite, (x_pos, y_pos))

    #screen.blit(sprite.cursor, (cursor.position_x, cursor.position_y))

def start(screen, window, clock, joystick):
    # PS5 controller
    controller = PS5controller(joystick)

    # load
    sprite = load_sprites()

    # starting values
    camera = Camera()
    grid = Grid()
    cursor = Cursor()

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

        if abs(controller.input.R.x) > 0 and cursor.position_x > 0 and cursor.position_x < Display.virtual_width:
            cursor.position_x += 2 * controller.input.R.x
        if abs(controller.input.R.y) > 0 and cursor.position_y > 0 and cursor.position_y < Display.virtual_height:
            cursor.position_y += 2 * controller.input.R.y

        if controller.input.OPTIONS.down:
            isPlaying = False

        # Logic - Camera
        camera.velocity_x *= 0.85
        camera.velocity_y *= 0.85
        camera.position_x += camera.velocity_x
        camera.position_y += camera.velocity_y

        # Logic - Cursor
        cursor_world_x = camera.position_x + cursor.position_x
        cursor_world_y = camera.position_y + cursor.position_y
        cursor.tile_x = (math.floor((((cursor_world_x / 2) + cursor_world_y) + 6) / 11.5)) - 1
        cursor.tile_y = math.floor((-((cursor_world_x / 2) - cursor_world_y) + 6) / 11.5)

        # Rendering
        render_pipeline(screen, sprite, grid, camera, cursor)

        upscaled = pygame.transform.scale(screen, (scaled_width, scaled_height))
        window.blit(upscaled, (0, 0))
        
        pygame.display.flip()

        milliseconds_passed = clock.tick(60)