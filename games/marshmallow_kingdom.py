from dataclasses import dataclass
from lib.PS5 import PS5controller
import pygame
import random
import math
import sys

@dataclass
class Display:
    virtual_width: int = 320
    virtual_height: int = 240
    scale_factor: int = 3

@dataclass
class Entity:
    position_x: float
    position_y: float
    velocity_x: float
    velocity_y: float
    size: int
    health: int
    sprite: pygame.Surface

@dataclass
class Color:
    white: tuple = (255, 255, 255)
    black: tuple = (0, 0, 0)
    player: tuple = (0, 255, 128)
    enemy: tuple = (255, 128, 128)
    coin: tuple = (255, 255, 128)

def sign(x):
    return (x > 0) - (x < 0)

def distance(pos1:tuple, pos2:tuple):
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

def spawn_particles(x, y, particles, sprite):
    for _ in range(5):
        random_x = random.randint(-3, 3)
        random_y = random.randint(-1, 1)
        new_particle = Entity(x, y, random_x, random_y, 0, 0, sprite)
        particles.append(new_particle)

@dataclass
class SFX:
    death: pygame.mixer.Sound
    collect: pygame.mixer.Sound
    jump: pygame.mixer.Sound

def load_sfx():
    SFX_PATH = "resources/smk/audio/"
    return SFX(
        death = pygame.mixer.Sound(f"{SFX_PATH}death.mp3"),
        collect = pygame.mixer.Sound(f"{SFX_PATH}collect.mp3"),
        jump = pygame.mixer.Sound(f"{SFX_PATH}jump.mp3")
    )

@dataclass
class Sprites:
    background: pygame.Surface
    floor: pygame.Surface
    coin: pygame.Surface
    player: pygame.Surface
    marshmallow: pygame.Surface
    health: pygame.Surface
    money: pygame.Surface
    marshmallow_particle: pygame.Surface
    coin_particle: pygame.Surface
    power_box: pygame.Surface
    balloon: pygame.Surface
    whale: pygame.Surface
    bomb: pygame.Surface

def load_sprites():
    SPRITE_PATH = "resources/smk/images/"
    return Sprites(
        background = pygame.image.load(f"{SPRITE_PATH}bg.png").convert(),
        floor = pygame.image.load(f"{SPRITE_PATH}floor.png").convert_alpha(),
        coin = pygame.image.load(f"{SPRITE_PATH}coin.png").convert_alpha(),
        player = pygame.image.load(f"{SPRITE_PATH}player.png").convert_alpha(),
        marshmallow = pygame.image.load(f"{SPRITE_PATH}marshmallow.png").convert_alpha(),
        health = pygame.image.load(f"{SPRITE_PATH}health.png").convert_alpha(),
        money = pygame.image.load(f"{SPRITE_PATH}money.png").convert_alpha(),
        marshmallow_particle = pygame.image.load(f"{SPRITE_PATH}marshmallow-particle.png").convert_alpha(),
        coin_particle = pygame.image.load(f"{SPRITE_PATH}coin-particle.png").convert_alpha(),
        power_box = pygame.image.load(f"{SPRITE_PATH}power-box.png").convert_alpha(),
        balloon = pygame.image.load(f"{SPRITE_PATH}balloon.png").convert_alpha(),
        whale = pygame.image.load(f"{SPRITE_PATH}whale.png").convert_alpha(),
        bomb = pygame.image.load(f"{SPRITE_PATH}bomb.png").convert_alpha()
    )

def render_pipeline(screen, sprite, player, enemies, particles, coins, power_boxes, balloons, power_ups, score, whale, bombs):
    screen.blit(sprite.background, (0, 0))
    
    #pygame.draw.rect(screen, Color.white, (0, Display.virtual_height - floor_height, Display.virtual_width, floor_height))
    screen.blit(sprite.floor, (0, 10))

    #pygame.draw.rect(screen, Color.player, (player.position_x, player.position_y, player.size, player.size))
    screen.blit(sprite.player, (player.position_x, player.position_y - 20))

    screen.blit(sprite.whale, (whale.position_x, whale.position_y))

    for heart in range(player.health):
        x = 5 + heart * 20
        screen.blit(sprite.health, (x, 5))
    
    for enemy in enemies:
        #pygame.draw.rect(screen, Color.enemy, (enemy.position_x, enemy.position_y, enemy.size, enemy.size))
        screen.blit(sprite.marshmallow, (enemy.position_x, enemy.position_y - 20))

    for particle in particles:
        screen.blit(particle.sprite, (particle.position_x, particle.position_y))
    
    for coin in coins:
        #pygame.draw.rect(screen, Color.coin, (coin.position_x, coin.position_y, coin.size, coin.size))
        screen.blit(sprite.coin, (coin.position_x, coin.position_y))
    
    for power_box in power_boxes:
        screen.blit(sprite.power_box, (power_box.position_x, power_box.position_y))

    for balloon in balloons:
        screen.blit(sprite.balloon, (balloon.position_x, balloon.position_y))

    for power_up in power_ups:
        screen.blit(sprite.health, (power_up.position_x, power_up.position_y))

    for bomb in bombs:
        screen.blit(sprite.bomb, (bomb.position_x, bomb.position_y))

    screen.blit(sprite.money, (5, 25))
    font = pygame.font.Font(None, 25)
    money_text = font.render(str(score), True, Color.black)
    screen.blit(money_text, (25, 25))

def start(screen, window, clock, joystick):
    # PS5 controller
    controller = PS5controller(joystick)

    # load
    sfx = load_sfx()
    sprite = load_sprites()

    # starting values
    player = Entity(140, 190, 0, 0, 16, 3, None)
    enemies = []
    coins = []
    particles = []
    power_boxes = []
    balloons = []
    power_ups = []
    whale = Entity(5, 10, 0.5, 0, 0, 0, None)
    bombs = []
    floor_height = 18
    milliseconds_passed = 0
    enemy_counter = 0
    power_counter = 0
    bomb_counter = 0
    score = 0

    # window scaling
    scaled_width = Display.virtual_width * Display.scale_factor
    scaled_height = Display.virtual_height * Display.scale_factor

    # main loop
    isPlaying = True
    while isPlaying:

        # input - Keyboard
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
            player.velocity_x += 0.5 * controller.input.L.x
        if controller.input.OPTIONS.pressed:
            isPlaying = False

        # counter
        enemy_counter += milliseconds_passed
        enemy_cooldown = 2000 / (1 + (score / 10))
        if enemy_counter >= enemy_cooldown:
            random_x = random.randint(20, Display.virtual_width - 20)
            new_enemy = Entity(random_x, 0, 0, 0, 16, 0, None)
            enemies.append(new_enemy)
            enemy_counter -= enemy_cooldown

        power_counter += milliseconds_passed
        power_cooldown = 8000 / (1 + (score / 10))
        if power_counter >= power_cooldown:
            random_x = random.randint(20, Display.virtual_width - 20)
            new_power_box = Entity(random_x, -60, 0, 0.5, 0, 0, None)
            power_boxes.append(new_power_box)
            power_counter -= power_cooldown

        bomb_counter += milliseconds_passed
        bomb_cooldown  = 5000 / (1 + (score / 10))
        if bomb_counter >= bomb_cooldown:
            new_bomb = Entity(whale.position_x, whale.position_y, 0, 0, 0, 0, None)
            bombs.append(new_bomb)
            bomb_counter -= bomb_cooldown

        # Drag
        player.velocity_x *= 0.85

        # Gravity
        GRAVITY = 0.4
        player.velocity_y += GRAVITY

        # Jumping
        floor_y = Display.virtual_height - floor_height - player.size 
        if controller.input.CROSS.down and player.position_y >= floor_y - 2:
            player.velocity_y = -6
            sfx.jump.play()

        # Calculate new position
        player.position_x += player.velocity_x
        player.position_y += player.velocity_y

        # Edge collision
        if player.position_x < 0:
            player.position_x = 0
            player.velocity_x = 0
        elif player.position_x > Display.virtual_width - player.size:
            player.position_x = Display.virtual_width - player.size
            player.velocity_x = 0
            
        if player.position_y > floor_y:
            player.position_y = floor_y
            player.velocity_y = 0

        # Enemies
        for enemy in enemies[:]:
            enemy.velocity_y += GRAVITY / 3
            enemy.position_y += enemy.velocity_y
            
            if enemy.position_y >= floor_y:
                new_coin = Entity(enemy.position_x + 5, enemy.position_y, 0, 0, 5, 0, None)
                coins.append(new_coin)

                spawn_particles(enemy.position_x, enemy.position_y, particles, sprite.marshmallow_particle)
                enemies.remove(enemy)
                sfx.death.play()

            # collision & death
            # dist = math.sqrt((enemy.position_x - player.position_x)**2 + (enemy.position_y - player.position_y)**2)
            pos1 = (player.position_x, player.position_y)
            pos2 = (enemy.position_x, enemy.position_y)
            dist = distance(pos1, pos2)
            
            if dist < 15:
                player.health -= 1
                enemies.remove(enemy)
                if player.health <= 0:
                    isPlaying = False

        # Particles
        for particle in particles[:]:
            particle.velocity_x *= 0.85
            particle.velocity_y += GRAVITY / 3

            particle.position_x += particle.velocity_x
            particle.position_y += particle.velocity_y

            if particle.position_y < 2:
                particles.remove(particle)

        # Coins
        for coin in coins[:]:
            #dist = math.sqrt((coin.position_x - player.position_x)**2 + (coin.position_y - player.position_y)**2)
            pos1 = (player.position_x, player.position_y)
            pos2 = (coin.position_x, coin.position_y)
            dist = distance(pos1, pos2)
            if dist < 20:
                score += 1
                sfx.collect.play()
                spawn_particles(coin.position_x, coin.position_y, particles, sprite.coin_particle)
                coins.remove(coin)
            
            elif dist < 80:
                coin.velocity_x = sign(player.position_x - coin.position_x)
                coin.velocity_y = sign(player.position_y - (coin.position_y - coin.size))
                coin.position_x += coin.velocity_x
                coin.position_y += coin.velocity_y

        # power box
        for power_box in power_boxes[:]:
            power_box.position_y += power_box.velocity_y
            if power_box.position_y >= floor_y - 50:
                new_balloon = Entity(power_box.position_x, power_box.position_y, 0, -4, 0, 0, None)
                balloons.append(new_balloon)

                new_power_up = Entity(power_box.position_x, power_box.position_y + 50, 0, 0, 0, 0, None)
                power_ups.append(new_power_up)
                
                power_boxes.remove(power_box)

        # balloon
        for balloon in balloons[:]:
            balloon.velocity_x = math.cos(balloon.position_y / 40) * 3
            balloon.position_x += balloon.velocity_x
            balloon.position_y += balloon.velocity_y
            if balloon.position_y < 0:
                balloons.remove(balloon)

        # power ups
        for power_up in power_ups[:]:
            #distance = math.sqrt((power_up.position_x - player.position_x)**2 + (power_up.position_y - player.position_y)**2)
            pos1 = (player.position_x, player.position_y)
            pos2 = (power_up.position_x, power_up.position_y)
            dist = distance(pos1, pos2)
            if dist < 15:
                player.health += 1
                power_ups.remove(power_up)

        # whale  
        whale.position_x += whale.velocity_x
        if whale.position_x < 0 or whale.position_x > Display.virtual_width:
            whale.velocity_x *= -1

        # Bombs
        for bomb in bombs[:]:
            bomb.velocity_x *= 0.85
            bomb.velocity_y += GRAVITY / 3
            
            bomb.position_x += bomb.velocity_x
            bomb.position_y += bomb.velocity_y

            if bomb.position_y > floor_y:
                bomb.position_y = floor_y
                bomb.velocity_y = 0

            #distance = math.sqrt((bomb.position_x - player.position_x)**2 + (bomb.position_y - player.position_y)**2)
            pos1 = (player.position_x, player.position_y)
            pos2 = (bomb.position_x, bomb.position_y)
            dist = distance(pos1, pos2)
            if dist < 20:
                direction = sign(bomb.position_x - player.position_x)
                bomb.velocity_x = direction * (player.velocity_x * 2)

        # Rendering
        render_pipeline(screen, sprite, player, enemies, particles, coins, power_boxes, balloons, power_ups, score, whale, bombs)

        upscaled = pygame.transform.scale(screen, (scaled_width, scaled_height))
        window.blit(upscaled, (0, 0))
        
        pygame.display.flip()

        milliseconds_passed = clock.tick(60)
