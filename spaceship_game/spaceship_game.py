import random
import sys

WIDTH = 600
HEIGHT = 700

class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.fire = False
        self.start_screen = True
        self.game_over = False
        self.paused = False
        self.sound_on = True

game_state = GameState()

spaceship_frames = ["spaceship1", "spaceship2", "spaceship3"]
meteor_images = [f"m{i}" for i in range(8)]
meteor_speeds = [1, 2, 3, 4, 5, 6]
animation_speed = 0.2
meteor_rotation_speed = 90

spaceship = Actor(spaceship_frames[0])
laser = Actor("laser")
meteor_list = [
    Actor(random.choice(meteor_images), (random.randint(40, WIDTH - 40), 0))
    for _ in range(5)
]

spaceship_animation_timer = 0

spaceship.midbottom = (WIDTH / 2, HEIGHT)
laser.midbottom = spaceship.midbottom

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60
BUTTON_SPACING = 20

start_button = Actor("button_start")
replay_button = Actor("button_replay")
pause_button = Actor("button_pause")
exit_button = Actor("button_exit")
sound_button = Actor("button_sound_on")

background = Actor("background_image", (WIDTH // 2, HEIGHT // 2))

laser_sound = sounds.laser
background_music = sounds.background_music

def on_mouse_down(pos, button):
    if start_button.collidepoint(pos):
        game_state.start_screen = False
        game_state.paused = False
        if game_state.sound_on:
            background_music.play()
    elif replay_button.collidepoint(pos):
        reset_game()
        game_state.game_over = False
        game_state.start_screen = False
        game_state.paused = False
    elif pause_button.collidepoint(pos) and button == mouse.LEFT:
        if pause_button.image == "button_pause":
            pause_button.image = "button_start"
        else:
            pause_button.image = "button_pause"
        game_state.paused = not game_state.paused
    elif exit_button.collidepoint(pos) and button == mouse.LEFT:
        sys.exit()
    elif sound_button.collidepoint(pos) and button == mouse.LEFT:
        if sound_button.image == "button_sound_on":
            game_state.sound_on = False
            sound_button.image = "button_sound_off"
        else:
            sound_button.image = "button_sound_on"
            game_state.sound_on = True

def draw():
    if game_state.start_screen:
        draw_start_screen()
    elif game_state.game_over:
        draw_game_over_screen()
    elif game_state.lives > 0:
        draw_game_screen()

def draw_start_screen():
    screen.blit('home_background_picture', (0, 0))
    screen.draw.text("SPACESHIP GAME", (WIDTH // 2 - 150, 100), color=(0, 0, 0), fontsize=40)
    start_button.pos = (WIDTH // 2 - BUTTON_WIDTH - BUTTON_SPACING, HEIGHT // 2)
    sound_button.pos = (WIDTH // 2, HEIGHT // 2)
    exit_button.pos = (WIDTH // 2 + BUTTON_WIDTH + BUTTON_SPACING, HEIGHT // 2)
    start_button.draw()
    sound_button.draw()
    exit_button.draw()

def draw_game_over_screen():
    screen.fill((250, 10, 10))
    screen.draw.text("Game Over", (150, 260), color=(255, 255, 255), fontsize=80)
    screen.draw.text(f"Score: {game_state.score}", (230, 350), color=(255, 255, 255), fontsize=50)
    exit_button.pos = (WIDTH // 2, HEIGHT // 2 + 80)
    replay_button.draw()
    exit_button.draw()

def draw_game_screen():
    background.width = WIDTH
    background.height = HEIGHT
    background.x = WIDTH // 2
    background.y = HEIGHT // 2
    background.draw()
    spaceship.draw()
    laser.draw()
    for meteor in meteor_list:
        meteor.draw()
    screen.draw.text(f"Score={game_state.score}", (10, 10), color=(0, 255, 255), fontsize=30)
    screen.draw.text(f"Lives={game_state.lives}", (WIDTH - 100, 10), color=(0, 255, 255), fontsize=30)
    exit_button.pos = (WIDTH // 2 + 100, 30)
    pause_button.pos = (WIDTH // 2 - 100, 30)
    pause_button.draw()
    exit_button.draw()

def update(dt):
    global spaceship_animation_timer

    if game_state.game_over or game_state.paused:
        background_music.stop()
        return

    if not game_state.game_over and not game_state.start_screen and not game_state.paused:
        if game_state.sound_on:
            background_music.play()
        update_spaceship_animation(dt)
        update_meteors(dt)
        handle_input()

def update_spaceship_animation(dt):
    global spaceship_animation_timer
    spaceship_animation_timer += dt
    if spaceship_animation_timer >= animation_speed:
        current_frame = spaceship_frames.index(spaceship.image)
        next_frame = (current_frame + 1) % len(spaceship_frames)
        spaceship.image = spaceship_frames[next_frame]
        spaceship_animation_timer = 0

def update_meteors(dt):
    for meteor in meteor_list:
        if meteor.y > HEIGHT:
            reset_meteor(meteor)
        elif meteor.colliderect(laser):
            handle_laser_hit(meteor)
        elif meteor.colliderect(spaceship):
            handle_spaceship_hit(meteor)
        else:
            meteor.y += meteor_speeds[meteor_list.index(meteor)]
            meteor.angle += meteor_rotation_speed * dt

def handle_laser_hit(meteor):
    game_state.score += 10
    reset_meteor(meteor)
    laser.midbottom = spaceship.midbottom
    game_state.fire = False

def handle_spaceship_hit(meteor):
    game_state.lives -= 1
    reset_meteor(meteor)
    if game_state.lives <= 0:
        game_state.game_over = True

def handle_input():
    if keyboard.left and spaceship.left > 0:
        spaceship.x -= 5
        if not game_state.fire:
            laser.midbottom = spaceship.midbottom
    if keyboard.right and spaceship.right < WIDTH:
        spaceship.x += 5
        if not game_state.fire:
            laser.midbottom = spaceship.midbottom
    if keyboard.up and spaceship.top > 0:
        spaceship.y -= 5
        if not game_state.fire:
            laser.midbottom = spaceship.midbottom
    if keyboard.down and spaceship.bottom < HEIGHT:
        spaceship.y += 5
        if not game_state.fire:
            laser.midbottom = spaceship.midbottom

    if keyboard.space and not game_state.fire:
        game_state.fire = True
        if game_state.sound_on:
            background_music.stop()
            laser_sound.play()
    if game_state.fire:
        move_laser()

def reset_meteor(actor):
    actor.y = 0
    actor.x = random.randint(40, WIDTH - 40)
    actor.image = random.choice(meteor_images)
    actor.angle = 0

def move_laser():
    if game_state.fire and laser.y > 0:
        laser.y -= 10
    else:
        game_state.fire = False
        laser.midbottom = spaceship.midbottom

def reset_game():
    game_state.score = 0
    game_state.lives = 3
    game_state.fire = False
    game_state.game_over = False
    game_state.paused = False
    spaceship.midbottom = (WIDTH / 2, HEIGHT)
    laser.midbottom = spaceship.midbottom
    for meteor in meteor_list:
        reset_meteor(meteor)
