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
class Sprites:
    background: pygame.Surface
    horse_idle: pygame.Surface
    horse_jump1: pygame.Surface
    horse_jump2: pygame.Surface
    horse_jump3: pygame.Surface
    horse_run1: pygame.Surface
    horse_run2: pygame.Surface
    horse_run3: pygame.Surface
    horse_run4: pygame.Surface
    horse_run5: pygame.Surface
    health0: pygame.Surface
    health1: pygame.Surface
    health2: pygame.Surface
    health3: pygame.Surface
    health4: pygame.Surface
    gun: pygame.Surface
    bullet: pygame.Surface
    balloon1: pygame.Surface
    bomb: pygame.Surface
    powerup: pygame.Surface
    plane: pygame.Surface
    plane_bullet: pygame.Surface

def load_sprites():
    SPRITE_PATH = "resources/bb/images/"
    return Sprites(
        background = pygame.image.load(f"{SPRITE_PATH}bg.png").convert(),
        horse_idle = pygame.image.load(f"{SPRITE_PATH}horse-idle.png").convert_alpha(),
        horse_jump1 = pygame.image.load(f"{SPRITE_PATH}horse-jump1.png").convert_alpha(),
        horse_jump2 = pygame.image.load(f"{SPRITE_PATH}horse-jump2.png").convert_alpha(),
        horse_jump3 = pygame.image.load(f"{SPRITE_PATH}horse-jump3.png").convert_alpha(),
        horse_run1 = pygame.image.load(f"{SPRITE_PATH}horse-run1.png").convert_alpha(),
        horse_run2 = pygame.image.load(f"{SPRITE_PATH}horse-run2.png").convert_alpha(),
        horse_run3 = pygame.image.load(f"{SPRITE_PATH}horse-run3.png").convert_alpha(),
        horse_run4 = pygame.image.load(f"{SPRITE_PATH}horse-run4.png").convert_alpha(),
        horse_run5 = pygame.image.load(f"{SPRITE_PATH}horse-run5.png").convert_alpha(),
        health0 = pygame.image.load(f"{SPRITE_PATH}health0.png").convert_alpha(),
        health1 = pygame.image.load(f"{SPRITE_PATH}health1.png").convert_alpha(),
        health2 = pygame.image.load(f"{SPRITE_PATH}health2.png").convert_alpha(),
        health3 = pygame.image.load(f"{SPRITE_PATH}health3.png").convert_alpha(),
        health4 = pygame.image.load(f"{SPRITE_PATH}health4.png").convert_alpha(),
        gun = pygame.image.load(f"{SPRITE_PATH}gun.png").convert_alpha(),
        bullet = pygame.image.load(f"{SPRITE_PATH}bullet.png").convert_alpha(),
        balloon1 = pygame.image.load(f"{SPRITE_PATH}balloon1.png").convert_alpha(),
        bomb = pygame.image.load(f"{SPRITE_PATH}bomb.png").convert_alpha(),
        powerup = pygame.image.load(f"{SPRITE_PATH}power-up.png").convert_alpha(),
        plane = pygame.image.load(f"{SPRITE_PATH}plane.png").convert_alpha(),
        plane_bullet = pygame.image.load(f"{SPRITE_PATH}plane-bullet.png").convert_alpha()
    )

@dataclass
class Player:
    position_x: float
    position_y: float
    velocity_x: float
    velocity_y: float
    size: int
    health: int
    max_health: int
    sprite: pygame.Surface # animation frame / state
    gun_sprite: pygame.Surface
    right: bool # facing / direction

@dataclass
class Bullet:
    position_x: float
    position_y: float
    sprite: pygame.Surface  # rotation
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    damage: int = 1

@dataclass
class PlaneBullet:
    position_x: float
    position_y: float
    sprite: pygame.Surface  # rotation
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    damage: int = 1

@dataclass
class Balloon:
    position_x: float
    position_y: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    health: int = 10

@dataclass
class Bomb:
    position_x: float
    position_y: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    damage: int = 1

@dataclass
class Powerup:
    position_x: float
    position_y: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0

@dataclass
class Plane:
    position_x: float
    position_y: float
    sprite: pygame.Surface # rotation
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    node: tuple = (30, 30)
    current_radians: float = 0.0
    target_radians: float = 0.0
    current_degrees: float = 0.0
    target_degrees: float = 0.0
    state: int = 0
    health: int = 3

def sign(x):
    return (x > 0) - (x < 0)

def distance(pos1:tuple, pos2:tuple):
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

def animation_frames(sprite, player):
    # Facing direction
    if player.right and sign(player.velocity_x) < 0:
        player.right = False
    elif not player.right and sign(player.velocity_x) > 0:
        player.right = True
    
    # Jump
    if abs(player.velocity_y) > 0.1:
        if abs(player.velocity_y) < 2:
            player.sprite = sprite.horse_jump2 if player.right else pygame.transform.flip(sprite.horse_jump2, True, False)
        elif player.velocity_y > 1:
            player.sprite = sprite.horse_jump3 if player.right else pygame.transform.flip(sprite.horse_jump3, True, False)
        else:
            player.sprite = sprite.horse_jump1 if player.right else pygame.transform.flip(sprite.horse_jump1, True, False)

    # Run
    elif abs(player.velocity_x) > 0.1:
        run_frames = [sprite.horse_run1, sprite.horse_run2, sprite.horse_run3, sprite.horse_run4, sprite.horse_run5]
        x_to_frame = abs(round(player.position_x / 10)) % len(run_frames)
        new_frame = run_frames[x_to_frame]
        if not player.right:
            new_frame = pygame.transform.flip(new_frame, True, False)
        player.sprite = new_frame

    # Idle
    else:
        player.sprite = sprite.horse_idle if player.right else pygame.transform.flip(sprite.horse_idle, True, False)

def render_pipeline(screen, sprite, player, bullets, balloons, bombs, powerups, planes, plane_bullets):
    screen.blit(sprite.background, (0, 0))
    
    screen.blit(player.sprite, (player.position_x, player.position_y))
    screen.blit(player.gun_sprite, (player.position_x, player.position_y))

    for balloon in balloons:
        screen.blit(sprite.balloon1, (balloon.position_x, balloon.position_y))

    for bomb in bombs:
        screen.blit(sprite.bomb, (bomb.position_x, bomb.position_y))

    for bullet in bullets:
        screen.blit(bullet.sprite, (bullet.position_x, bullet.position_y))

    for powerup in powerups:
        screen.blit(sprite.powerup, (powerup.position_x, powerup.position_y))

    for plane in planes:
        screen.blit(plane.sprite, (plane.position_x, plane.position_y))

    for pb in plane_bullets:
        screen.blit(pb.sprite, (pb.position_x, pb.position_y))

    health_sprite = {
        1: sprite.health1,
        2: sprite.health2,
        3: sprite.health3,
    }
    
    full_hearts = player.health // 4
    remainder = player.health % 4
    total_hearts = (player.max_health // 4) + ((player.max_health % 4) > 0)
    empty_hearts = total_hearts - full_hearts - (remainder > 0)

    heart_index = 0
    if full_hearts > 0:
        for fh in range(full_hearts):
            x = 5 + heart_index * 20
            screen.blit(sprite.health4, (x, 5))
            heart_index += 1

    if remainder > 0:
        x = 5 + heart_index * 20
        remainder_sprite = health_sprite[remainder]
        screen.blit(remainder_sprite, (x, 5))
        heart_index += 1

    if empty_hearts > 0:
        for eh in range(empty_hearts):
            x = 5 + heart_index * 20
            screen.blit(sprite.health0, (x, 5))
            heart_index += 1

def start(screen, window, clock, joystick):
    # PS5 controller
    controller = PS5controller(joystick)

    # load
    sprite = load_sprites()

    # starting values
    player = Player(Display.virtual_width / 2, 150, 0, 0, 32, 4, 12, sprite.horse_idle, sprite.gun, True)
    score = 0
    bullets = []
    balloons = []
    bombs = []
    powerups = []
    planes = []
    plane_bullets = []
    balloon_counter = 0
    bomb_counter = 0
    powerup_counter = 0
    plane_counter = 0
    pb_counter = 0
    milliseconds_passed = 0
    floor_height = 15

    # window scaling
    scaled_width = Display.virtual_width * Display.scale_factor
    scaled_height = Display.virtual_height * Display.scale_factor

    # main loop
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
            player.velocity_x += 0.5 * controller.input.L.x
        
        player.gun_sprite = pygame.transform.rotate(sprite.gun, controller.input.R.degrees)
        
        if controller.input.R2.pressed:
            rotated_bullet = pygame.transform.rotate(sprite.bullet, controller.input.R.degrees)
            dx = 3 * math.cos(controller.input.R.radians)
            dy = 3 * -math.sin(controller.input.R.radians)
            new_bullet = Bullet(player.position_x, player.position_y, rotated_bullet, dx, dy)
            bullets.append(new_bullet)
        
        if controller.input.OPTIONS.down:
            isPlaying = False

        # Counter
        balloon_counter += milliseconds_passed
        balloon_cooldown = (5 * 1000) / (1 + (score / 10))
        if balloon_counter >= balloon_cooldown:
            if len(balloons) < 2:
                new_balloon = Balloon(20, 20, 1, 0)
                balloons.append(new_balloon)
            balloon_counter -= balloon_cooldown

        bomb_counter += milliseconds_passed
        bomb_cooldown = (3 * 1000) / (1 + (score / 10))
        if bomb_counter >= bomb_cooldown:
            if len(balloons) > 0:
                for balloon in balloons:
                    new_bomb = Bomb(balloon.position_x, balloon.position_y + 20)
                    bombs.append(new_bomb)
            bomb_counter -= bomb_cooldown

        powerup_counter += milliseconds_passed
        powerup_cooldown = (7 * 1000) / (1 + (score / 10))
        if powerup_counter >= powerup_cooldown:
            random_x = random.randint(20, Display.virtual_width - 20)
            new_powerup = Powerup(random_x, 20)
            powerups.append(new_powerup)
            powerup_counter -= powerup_cooldown

        plane_counter += milliseconds_passed
        plane_cooldown = (8 * 1000) / (1 + (score / 10))
        if plane_counter >= plane_cooldown:
            if len(planes) < 2:
                new_plane = Plane(100, 100, sprite.plane)
                planes.append(new_plane)
            plane_counter -= plane_cooldown

        pb_counter += milliseconds_passed
        pb_cooldown = 800
        if pb_counter >= pb_cooldown:
            if len(planes) > 0:
                for plane in planes:
                    if plane.state == 2:
                        rotated_pb = pygame.transform.rotate(sprite.plane_bullet, -plane.current_degrees)
                        dx = 3 * math.cos(plane.current_radians)
                        dy = 3 * math.sin(plane.current_radians)
                        new_pb = PlaneBullet(plane.position_x, plane.position_y, rotated_pb, dx, dy, 1)
                        plane_bullets.append(new_pb)
            pb_counter -= pb_cooldown

        # Logic - Player
        if player.health <= 0:
            isPlaying = False

        player.velocity_x *= 0.85 # drag
        GRAVITY = 0.4
        player.velocity_y += GRAVITY

        floor_y = Display.virtual_height - floor_height - player.size 
        if controller.input.L2.raw > 0.0 and player.position_y >= floor_y - 2:
            player.velocity_y = -6

        player.position_x += player.velocity_x
        player.position_y += player.velocity_y

        if player.position_x < 0:
            player.position_x = 0
            player.velocity_x = 0
        elif player.position_x > Display.virtual_width - player.size:
            player.position_x = Display.virtual_width - player.size
            player.velocity_x = 0
            
        if player.position_y > floor_y:
            player.position_y = floor_y
            player.velocity_y = 0

        # Logic - Bullets
        for bullet in bullets[:]:
            # hit balloon
            for balloon in balloons:
                pos1 = (balloon.position_x, balloon.position_y)
                pos2 = (bullet.position_x, bullet.position_y)
                dist = distance(pos1, pos2)
                if dist < 15:
                    balloon.health -= bullet.damage
                    bullets.remove(bullet)
                    break

            for plane in planes:
                pos1 = (bullet.position_x, bullet.position_y)
                pos2 = (plane.position_x, plane.position_y)
                dist = distance(pos1, pos2)
                if dist < 15:
                    plane.health -= bullet.damage
                    bullets.remove(bullet)
                    break

            # move
            bullet.position_x += bullet.velocity_x
            bullet.position_y += bullet.velocity_y

            # edges
            if bullet.position_x < 0 or bullet.position_x > Display.virtual_width or bullet.position_y < 0 or bullet.position_y > Display.virtual_height:
                bullets.remove(bullet)
                break

        # Logic - Balloons
        for balloon in balloons[:]:
            if balloon.health <= 0:
                balloons.remove(balloon)
                break
            
            # move
            balloon.position_x += balloon.velocity_x
            balloon.position_y += balloon.velocity_y
            
            # edges
            if balloon.position_x < 0 or balloon.position_x > Display.virtual_width:
                balloon.velocity_x *= -1

        # Logic - Bombs
        for bomb in bombs[:]:
            # hit ground
            if bomb.position_y >= floor_y + 20:
                bombs.remove(bomb)
                break

            # hit player
            pos1 = (bomb.position_x, bomb.position_y)
            pos2 = (player.position_x, player.position_y)
            dist = distance(pos1, pos2)
            if dist < 15:
                player.health -= bomb.damage
                bombs.remove(bomb)
                break

            # gravity
            bomb.velocity_y += GRAVITY / 4

            # move
            bomb.position_x += bomb.velocity_x
            bomb.position_y += bomb.velocity_y

        # Logic - Powerups
        for powerup in powerups[:]:
            # pick up
            pos1 = (powerup.position_x, powerup.position_y)
            pos2 = (player.position_x, player.position_y)
            dist = distance(pos1, pos2)
            if dist < 20:
                if player.health < player.max_health:
                    player.health += 1
                powerups.remove(powerup)
                break
            
            # gravity
            powerup.velocity_y += GRAVITY / 4

            # move
            powerup.position_x += powerup.velocity_x
            powerup.position_y += powerup.velocity_y
            if powerup.position_y > floor_y + 15:
                        powerup.position_y = floor_y + 15
                        powerup.velocity_y = 0

        # Logic - Planes
        for plane in planes[:]:
            if plane.health <= 0:
                planes.remove(plane)
                break

            match plane.state:
                case 0: # find node
                    plane.node = (30, 30) if player.position_x < (Display.virtual_width / 2) else (Display.virtual_width - 30, 30)
                    plane.state = 1
                case 1: # go to node
                    dx = plane.node[0] - plane.position_x
                    dy = plane.node[1] - plane.position_y

                    plane.target_radians = math.atan2(dy, dx)
                    plane.target_degrees = math.degrees(plane.target_radians)

                    plane.current_degrees += sign(plane.target_degrees - plane.current_degrees) * 2
                    plane.current_radians = math.radians(plane.current_degrees)

                    plane.sprite = pygame.transform.rotate(sprite.plane, -plane.current_degrees)
                    
                    plane.velocity_x = math.cos(plane.current_radians)
                    plane.velocity_y = math.sin(plane.current_radians)
                    
                    plane.position_x += plane.velocity_x
                    plane.position_y += plane.velocity_y

                    pos1 = (plane.position_x, plane.position_y)
                    pos2 = (plane.node[0], plane.node[1])
                    dist = distance(pos1, pos2)
                    if dist < 5:
                        plane.state = 2
                case 2: # shoot player
                    plane.node = (player.position_x, player.position_y)

                    dx = plane.node[0] - plane.position_x
                    dy = plane.node[1] - plane.position_y

                    plane.target_radians = math.atan2(dy, dx)
                    plane.target_degrees = math.degrees(plane.target_radians)

                    plane.current_degrees += sign(plane.target_degrees - plane.current_degrees) * 2
                    plane.current_radians = math.radians(plane.current_degrees)

                    plane.sprite = pygame.transform.rotate(sprite.plane, -plane.current_degrees)

                    plane.velocity_x = math.cos(plane.current_radians)
                    plane.velocity_y = math.sin(plane.current_radians)
                    
                    plane.position_x += plane.velocity_x
                    plane.position_y += plane.velocity_y

                    if plane.position_y > Display.virtual_height - 100:
                        plane.state = 0

        # Logic - Plane Bullets
        for pb in plane_bullets[:]:
            # move
            pb.position_x += pb.velocity_x
            pb.position_y += pb.velocity_y

            # edges
            if pb.position_x < 0 or pb.position_x > Display.virtual_width or pb.position_y < 0 or pb.position_y > Display.virtual_height:
                plane_bullets.remove(pb)
                break

            # player hit
            pos1 = (pb.position_x, pb.position_y)
            pos2 = (player.position_x, player.position_y)
            dist = distance(pos1, pos2)
            if dist < 15:
                player.health -= pb.damage
                plane_bullets.remove(pb)
                break

        # Animation
        animation_frames(sprite, player)

        # Rendering
        render_pipeline(screen, sprite, player, bullets, balloons, bombs, powerups, planes, plane_bullets)

        upscaled = pygame.transform.scale(screen, (scaled_width, scaled_height))
        window.blit(upscaled, (0, 0))
        
        pygame.display.flip()

        milliseconds_passed = clock.tick(60)