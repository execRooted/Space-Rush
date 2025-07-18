import turtle
import random
import math
import time
from collections import deque
import serial
import serial.tools.list_ports
import threading
import os
import sys
import pygame


# --- Music ---
pygame.mixer.init()
button_click = pygame.mixer.Sound("bc.mp3")
hurt = pygame.mixer.Sound("rh.mp3")
g_o = pygame.mixer.Sound("game_over.mp3")
pu = pygame.mixer.Sound("orb.mp3")
loading_menu = pygame.mixer.Sound("loading_menu.mp3")


mode_music = {
    "classic": "Hammer of Justice.mp3",
    "falling": "Spear of Justice.mp3",
    "hardcore": "Attack of the Killer Queen.mp3",
    "reversed": "MEGALOVANIA.mp3",
    "chase": "Spider Dance.mp3"
}

pygame.mixer.music.set_volume(0.3)


def play_music(sound_file, loop=True):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(-1 if loop else 0)

# --- Hi score ---
high_scores = {
    "classic": 0,
    "falling": 0,
    "hardcore": 0,
    "reversed": 0,
    "chase": 0
}

#---vars---
is_paused = False
pause_menu_items = []


def load_high_scores():
    global high_scores
    try:
        with open("highscores.txt", "r") as f:
            scores = f.read().split(',')
            if len(scores) == 5:
                high_scores["classic"] = int(scores[0])
                high_scores["falling"] = int(scores[1])
                high_scores["hardcore"] = int(scores[2])
                high_scores["reversed"] = int(scores[3])
                high_scores["chase"] = int(scores[4])
    except:
        high_scores = {
            "classic": 0,
            "falling": 0,
            "hardcore": 0,
            "reversed": 0,
            "chase": 0
        }


def save_high_scores():
    global high_scores
    with open("highscores.txt", "w") as f:
        f.write(
            f"{high_scores['classic']},"
            f"{high_scores['falling']},"
            f"{high_scores['hardcore']},"
            f"{high_scores['reversed']},"
            f"{high_scores['chase']}"
        )


# --- Screen Setup ---
win = turtle.Screen()
win.bgcolor("black")
win.setup(width=1.0, height=1.0)
win.tracer(0)
canvas = win.getcanvas()
root = canvas.winfo_toplevel()
root.attributes("-fullscreen", True)

screen_width = win.window_width()
screen_height = win.window_height()
X_BOUND = screen_width // 2 - 20
Y_BOUND = screen_height // 2 - 20


# --- Game Modes ---
class GameMode:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.mode_id = ""

    def setup(self):
        pass

    def update(self):
        if is_paused:
            return



class ClassicMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "CLASSIC MODE"
        self.description = "Dodge enemies coming from above"
        self.mode_id = "classic"

    def setup(self):
        self.enemies = []
        self.base_enemy_speed = 3
        self.enemy_speed = self.base_enemy_speed
        self.spawn_delay = 40
        self.max_spawn = 37

    def update(self):
        capped_score = min(score, 300)
        self.enemy_speed = self.base_enemy_speed + (capped_score / 50)
        self.spawn_delay = max(10, int(40 - capped_score / 5))
        if is_paused:
            return

        available_spawn_slots = self.max_spawn - len(self.enemies)
        enemies_per_spawn = min(available_spawn_slots, 1 + score // 37)
        enemies_per_spawn = max(enemies_per_spawn, 0)

        if frame_count % self.spawn_delay == 0:
            for _ in range(enemies_per_spawn):
                enemy = turtle.Turtle()
                enemy.shape("circle")
                enemy.color("red")
                enemy.penup()
                x_pos = random.randint(-X_BOUND + 20, X_BOUND - 20)
                y_pos = Y_BOUND + random.randint(10, 50)
                enemy.goto(x_pos, y_pos)
                self.enemies.append(enemy)

        for enemy in self.enemies[:]:
            enemy.sety(enemy.ycor() - self.enemy_speed)
            if is_collision(enemy, player, 20) and not is_spawning_protected and active_powerup != "invincibility":
                lives_decrease(1)
                self.enemies.remove(enemy)
                enemy.hideturtle()
                if lives <= 0:
                    show_game_over()
                    return
            elif enemy.ycor() < -Y_BOUND - 20:
                self.enemies.remove(enemy)
                enemy.hideturtle()
                increase_score(1)


class FallingBallsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "FALLING ENEMIES MODE"
        self.description = "Dodge enemies falling from all directions"
        self.mode_id = "falling"

    def setup(self):
        self.enemies = []
        self.base_enemy_speed = 3
        self.enemy_speed = self.base_enemy_speed
        self.spawn_delay = 30
        self.max_spawn = 30
        self.directions = ["top", "bottom", "left", "right"]

    def update(self):
        capped_score = min(score, 500)
        self.enemy_speed = self.base_enemy_speed + (capped_score / 80)
        self.spawn_delay = max(5, int(30 - capped_score / 8))
        if is_paused:
            return

        available_spawn_slots = self.max_spawn - len(self.enemies)
        enemies_per_spawn = min(available_spawn_slots, 1 + score // 40)
        enemies_per_spawn = max(enemies_per_spawn, 0)

        if frame_count % self.spawn_delay == 0:
            for _ in range(enemies_per_spawn):
                enemy = turtle.Turtle()
                enemy.shape("circle")
                enemy.color("red")
                enemy.penup()

                direction = random.choice(self.directions)
                if direction == "top":
                    x_pos = random.randint(-X_BOUND + 20, X_BOUND - 20)
                    y_pos = Y_BOUND + random.randint(10, 50)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(270)
                elif direction == "bottom":
                    x_pos = random.randint(-X_BOUND + 20, X_BOUND - 20)
                    y_pos = -Y_BOUND - random.randint(10, 50)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(90)
                elif direction == "left":
                    x_pos = -X_BOUND - random.randint(10, 50)
                    y_pos = random.randint(-Y_BOUND + 20, Y_BOUND - 20)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(0)
                elif direction == "right":
                    x_pos = X_BOUND + random.randint(10, 50)
                    y_pos = random.randint(-Y_BOUND + 20, Y_BOUND - 20)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(180)

                self.enemies.append(enemy)

        for enemy in self.enemies[:]:
            if enemy.heading() == 270:
                enemy.sety(enemy.ycor() - self.enemy_speed)
            elif enemy.heading() == 90:
                enemy.sety(enemy.ycor() + self.enemy_speed)
            elif enemy.heading() == 0:
                enemy.setx(enemy.xcor() + self.enemy_speed)
            elif enemy.heading() == 180:
                enemy.setx(enemy.xcor() - self.enemy_speed)

            if is_collision(enemy, player, 20) and not is_spawning_protected and active_powerup != "invincibility":
                lives_decrease(1)
                self.enemies.remove(enemy)
                enemy.hideturtle()
                if lives <= 0:
                    show_game_over()
                    return
            elif (abs(enemy.xcor()) > X_BOUND + 50 or abs(enemy.ycor()) > Y_BOUND + 50):
                self.enemies.remove(enemy)
                enemy.hideturtle()
                increase_score(1)


class HardcoreMode(FallingBallsMode):
    def __init__(self):
        super().__init__()
        self.name = "HARDCORE MODE"
        self.description = "No power ups, starts at the hardest difficulty, one life, enemies coming from all directions"
        self.mode_id = "hardcore"
        self.inverted_controls = False

    def setup(self):
        self.enemies = []
        checker = True
        self.base_enemy_speed = 7
        self.enemy_speed = self.base_enemy_speed
        self.spawn_delay = 17
        self.max_spawn = 37
        self.directions = ["top", "bottom", "left", "right"]

    def update(self):
        if is_paused:
            return
        available_spawn_slots = self.max_spawn - len(self.enemies)
        enemies_per_spawn = min(available_spawn_slots, 3)


        if frame_count % self.spawn_delay == 0:
            for _ in range(enemies_per_spawn):
                enemy = turtle.Turtle()
                enemy.shape("circle")
                enemy.color("red")
                enemy.penup()

                direction = random.choice(self.directions)
                if direction == "top":
                    x_pos = random.randint(-X_BOUND + 20, X_BOUND - 20)
                    y_pos = Y_BOUND + random.randint(10, 50)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(270)
                elif direction == "bottom":
                    x_pos = random.randint(-X_BOUND + 20, X_BOUND - 20)
                    y_pos = -Y_BOUND - random.randint(10, 50)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(90)
                elif direction == "left":
                    x_pos = -X_BOUND - random.randint(10, 50)
                    y_pos = random.randint(-Y_BOUND + 20, Y_BOUND - 20)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(0)
                elif direction == "right":
                    x_pos = X_BOUND + random.randint(10, 50)
                    y_pos = random.randint(-Y_BOUND + 20, Y_BOUND - 20)
                    enemy.goto(x_pos, y_pos)
                    enemy.setheading(180)

                self.enemies.append(enemy)

        for enemy in self.enemies[:]:
            if enemy.heading() == 270:
                enemy.sety(enemy.ycor() - self.enemy_speed)
            elif enemy.heading() == 90:
                enemy.sety(enemy.ycor() + self.enemy_speed)
            elif enemy.heading() == 0:
                enemy.setx(enemy.xcor() + self.enemy_speed)
            elif enemy.heading() == 180:
                enemy.setx(enemy.xcor() - self.enemy_speed)

            if is_collision(enemy, player, 20) and not is_spawning_protected:
                lives_decrease(1)
                self.enemies.remove(enemy)
                enemy.hideturtle()
                if lives <= 0:
                    show_game_over()
                    return
            elif (abs(enemy.xcor()) > X_BOUND + 50 or abs(enemy.ycor()) > Y_BOUND + 50):
                self.enemies.remove(enemy)
                enemy.hideturtle()
                increase_score(1)

class ReversedHardcoreMode(HardcoreMode):
    def __init__(self):
        super().__init__()
        self.name = "REVERSED HARDCORE"
        self.description = "Hardcore with reversed controls"
        self.mode_id = "reversed"
        self.inverted_controls = True


class ChaseMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "CHASE MODE"
        self.description = "Enemies chase you then respawn"
        self.mode_id = "chase"

    def setup(self):
        self.enemies = []
        self.base_enemy_speed = 3.0
        self.enemy_speed = self.base_enemy_speed
        self.spawn_delay = 30
        self.max_spawn = 23
        self.chase_duration = 10

    def update(self):
        current_time = time.time()
        if is_paused:
            return


        capped_score = min(score, 500)
        self.enemy_speed = self.base_enemy_speed + (capped_score / 120)
        self.spawn_delay = max(15, int(45 - capped_score / 12))


        if frame_count % self.spawn_delay == 0 and len(self.enemies) < self.max_spawn:
            self.spawn_enemy(current_time)


        for enemy_data in self.enemies[:]:
            enemy, spawn_time = enemy_data


            if current_time - spawn_time > self.chase_duration:
                enemy.hideturtle()
                self.enemies.remove(enemy_data)
                self.spawn_enemy(current_time)
                increase_score(1)
                continue


            dx = player.xcor() - enemy.xcor()
            dy = player.ycor() - enemy.ycor()
            dist = math.hypot(dx, dy)

            if dist > 0:
                enemy.setx(enemy.xcor() + (dx / dist) * self.enemy_speed)
                enemy.sety(enemy.ycor() + (dy / dist) * self.enemy_speed)


            if is_collision(enemy, player, 20) and not is_spawning_protected and active_powerup != "invincibility":
                lives_decrease(1)
                self.enemies.remove(enemy_data)
                enemy.hideturtle()
                if lives <= 0:
                    show_game_over()
                    return

    def spawn_enemy(self, current_time):
        """Helper method to spawn a new enemy"""
        enemy = turtle.Turtle()
        enemy.shape("circle")
        enemy.color("red")
        enemy.penup()


        spawn_side = random.choice(["top", "bottom", "left", "right"])

        if spawn_side == "top":
            x = random.randint(-X_BOUND + 20, X_BOUND - 20)
            y = Y_BOUND + random.randint(10, 50)
        elif spawn_side == "bottom":
            x = random.randint(-X_BOUND + 20, X_BOUND - 20)
            y = -Y_BOUND - random.randint(10, 50)
        elif spawn_side == "left":
            x = -X_BOUND - random.randint(10, 50)
            y = random.randint(-Y_BOUND + 20, Y_BOUND - 20)
        else:
            x = X_BOUND + random.randint(10, 50)
            y = random.randint(-Y_BOUND + 20, Y_BOUND - 20)

        enemy.goto(x, y)
        self.enemies.append((enemy, current_time))



game_modes = [ClassicMode(), FallingBallsMode(), HardcoreMode(), ReversedHardcoreMode(), ChaseMode()]
current_game_mode = None

# --- Player Setup ---
base_move_speed = 13
player = turtle.Turtle()
player.shape("circle")
player.penup()
player.goto(0, -Y_BOUND + 50)
player.setheading(90)
player.hideturtle()

trail_points = deque(maxlen=25)
trail_turtle = turtle.Turtle()
trail_turtle.hideturtle()
trail_turtle.speed(0)
trail_turtle.penup()
trail_turtle.pensize(6)
trail_turtle.color("white")

MAX_TRAIL_LENGTH = 25
move_speed = base_move_speed

# --- Powerups ---
powerup_color_map = {
    "invincibility": "purple",
    "speed": "yellow"
}

powerups = []
powerup_score_interval = 37
last_powerup_score = 0
powerups_collected_after_500 = 0
active_powerup = None
powerup_end_time = 0

# --- Score & Lives ---
score = 0
lives = 3

score_pen = turtle.Turtle()
score_pen.hideturtle()
score_pen.color("white")
score_pen.penup()
score_pen.goto(-X_BOUND + 20, Y_BOUND - 40)

lives_pen = turtle.Turtle()
lives_pen.hideturtle()
lives_pen.color("white")
lives_pen.penup()
lives_pen.goto(X_BOUND - 120, Y_BOUND - 40)

hi_pen = turtle.Turtle()
hi_pen.hideturtle()
hi_pen.color("white")
hi_pen.penup()
hi_pen.goto(0, Y_BOUND - 40)


def update_score_and_lives():
    score_pen.clear()
    score_pen.write(f"Score: {score}", font=("Courier", 14, "normal"))
    lives_pen.clear()
    lives_pen.write(f"Lives: {lives}", font=("Courier", 14, "normal"))
    hi_pen.clear()
    hi_pen.write(
        f"M1HI: {high_scores['classic']}  M2HI: {high_scores['falling']}  M3HI: {high_scores['hardcore']}  M4HI: {high_scores['reversed']}  M5HI: {high_scores['chase']}",
        align="center", font=("Courier", 14, "normal"))


def increase_score(amount):
    global score
    score += amount
    update_score_and_lives()


def lives_decrease(amount):
    global lives
    lives -= amount
    hurt.play()
    update_score_and_lives()
    start_spawn_protection()


load_high_scores()
update_score_and_lives()

spawn_protection_time = 3
spawn_protection_start = None
is_spawning_protected = False


def start_spawn_protection():
    global spawn_protection_start, is_spawning_protected
    spawn_protection_start = time.time()
    is_spawning_protected = True


def update_spawn_protection():
    global is_spawning_protected
    if not is_spawning_protected:
        return False
    elapsed = time.time() - spawn_protection_start
    if elapsed >= spawn_protection_time:
        is_spawning_protected = False
        player.showturtle()
        return False
    if int(elapsed * 3) % 2 == 0:
        player.hideturtle()
    else:
        player.showturtle()
    return True


# --- Joystick Globals ---
ser = None
use_joystick = False
joystick_x = 512
joystick_y = 512
joystick_button = 1


def read_joystick():
    global joystick_x, joystick_y, joystick_button
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(',')
                if len(parts) == 3:
                    joystick_x = int(parts[0])
                    joystick_y = int(parts[1])
                    joystick_button = int(parts[2])
        except Exception:
            pass


def move_player():
    global joystick_x, joystick_y, move_speed
    threshold = 100
    dx_raw = joystick_x - 512
    dy_raw = 512 - joystick_y

    if current_game_mode and hasattr(current_game_mode, 'inverted_controls') and current_game_mode.inverted_controls:
        dx_raw = -dx_raw
        dy_raw = -dy_raw

    if abs(dx_raw) < threshold:
        dx_raw = 0
    if abs(dy_raw) < threshold:
        dy_raw = 0
    dx = (dx_raw / 512) * move_speed
    dy = (dy_raw / 512) * move_speed
    move(dx, dy)


def move(dx, dy):
    new_x = player.xcor() + dx
    new_y = player.ycor() + dy
    if -X_BOUND < new_x < X_BOUND:
        player.setx(new_x)
    if -Y_BOUND < new_y < Y_BOUND:
        player.sety(new_y)
    if dx != 0 or dy != 0:
        angle = math.degrees(math.atan2(dy, dx))
        player.setheading(angle)


def move_player_keyboard():
    global move_speed
    dx = 0
    dy = 0
    if current_game_mode and hasattr(current_game_mode, 'inverted_controls') and current_game_mode.inverted_controls:
        if keys["w"]: dy -= move_speed
        if keys["s"]: dy += move_speed
        if keys["a"]: dx += move_speed
        if keys["d"]: dx -= move_speed
    else:
        if keys["w"]: dy += move_speed
        if keys["s"]: dy -= move_speed
        if keys["a"]: dx -= move_speed
        if keys["d"]: dx += move_speed
    move(dx, dy)


def is_collision(a, b, dist=15):
    return math.hypot(a.xcor() - b.xcor(), a.ycor() - b.ycor()) < dist


def set_player_color(color):
    player.color(color)
    trail_turtle.color(color)


def clear_powerup():
    global active_powerup, powerup_end_time, move_speed
    active_powerup = None
    powerup_end_time = 0
    move_speed = base_move_speed
    set_player_color("white")


def apply_powerup(kind):
    global lives, powerups_collected_after_500, powerup_spawn_increase, active_powerup, powerup_end_time, move_speed
    if kind == "life":
        lives += 1
        powerups_collected_after_500 += 1
        if powerups_collected_after_500 % 3 == 0:
            powerup_spawn_increase += 50
        update_score_and_lives()
    elif kind == "invincibility":
        active_powerup = "invincibility"
        powerup_end_time = time.time() + 10
        set_player_color("purple")
    elif kind == "speed":
        active_powerup = "speed"
        powerup_end_time = time.time() + 7
        move_speed += 10
        set_player_color("yellow")


def draw_trail():
    trail_turtle.clear()
    if len(trail_points) < 2:
        return
    now = time.time()

    trail_length = len(trail_points)
    for i in range(trail_length - 1):
        start = trail_points[i]
        end = trail_points[i + 1]
        trail_turtle.width(13 * (i / trail_length))
        trail_turtle.penup()
        trail_turtle.goto(start)
        trail_turtle.pendown()
        trail_turtle.goto(end)
    trail_turtle.penup()


def show_game_over():
    global game_running
    game_running = False


    player.hideturtle()


    if hasattr(current_game_mode, 'enemies'):
        if current_game_mode.mode_id == "chase":

            for enemy_data in current_game_mode.enemies[:]:
                enemy, _ = enemy_data
                enemy.hideturtle()
        else:

            for enemy in current_game_mode.enemies[:]:
                enemy.hideturtle()
        current_game_mode.enemies.clear()


    for powerup in powerups[:]:
        powerup.hideturtle()
    powerups.clear()


    score_pen.clear()
    lives_pen.clear()

    win.bgcolor("black")


    go_text = turtle.Turtle()
    go_text.hideturtle()
    go_text.color("white")
    go_text.penup()

    go_text.goto(0, 60)
    go_text.write("GAME OVER", align="center", font=("Courier", 48, "bold"))


    go_text.goto(0, 0)
    go_text.write(f"Score: {score}", align="center", font=("Courier", 24, "normal"))


    current_high = high_scores[current_game_mode.mode_id]
    go_text.goto(0, -40)

    if score > current_high:
        go_text.write("NEW HIGH SCORE!", align="center", font=("Courier", 24, "bold"))
        high_scores[current_game_mode.mode_id] = score
        save_high_scores()
    else:
        go_text.write(f"High Score: {current_high}", align="center", font=("Courier", 24, "normal"))


    go_text.goto(0, -100)
    go_text.write("Press R to Restart or Q to Quit", align="center", font=("Courier", 18, "normal"))


    pygame.mixer.music.stop()
    g_o.play()


    def quit_game():
        turtle.bye()

    def restart_game():
        os.execl(sys.executable, sys.executable, *sys.argv)


    win.onkey(quit_game, "q")
    win.onkey(restart_game, "r")
    win.listen()


def toggle_pause():
    global is_paused
    is_paused = not is_paused

    if is_paused:
        show_pause_menu()
        pygame.mixer.music.pause()
    else:
        hide_pause_menu()
        pygame.mixer.music.unpause()
    button_click.play()


def show_pause_menu():
    """Draws the pause menu text without overlay"""
    global pause_menu_items


    text = turtle.Turtle()
    text.hideturtle()
    text.penup()
    text.color("white")
    text.goto(0, 50)
    text.write("PAUSED", align="center", font=("Courier", 36, "bold"))


    pause_menu_items = [text]


def hide_pause_menu():
    """Clears the pause menu"""
    global pause_menu_items
    for item in pause_menu_items:
        item.clear()
        item.hideturtle()
    pause_menu_items = []

def reset_game():
    global score, lives, game_running, frame_count, move_speed, last_powerup_score, powerup_spawn_increase, powerups_collected_after_500
    menu_pen.clear()
    draw_stars(70)
    score = 0

    if current_game_mode.mode_id in ["hardcore", "reversed"]:
        lives = 1
    else:
        lives = 3
    update_score_and_lives()
    player.goto(0, -Y_BOUND + 50)
    player.showturtle()
    frame_count = 0
    move_speed = base_move_speed
    last_powerup_score = 0
    powerup_spawn_increase = 0
    powerups_collected_after_500 = 0
    clear_powerup()
    current_game_mode.setup()
    start_spawn_protection()
    game_running = True
    game_loop()

keys = {"w": False, "a": False, "s": False, "d": False}


def key_press_w(): keys["w"] = True


def key_release_w(): keys["w"] = False


def key_press_a(): keys["a"] = True


def key_release_a(): keys["a"] = False


def key_press_s(): keys["s"] = True


def key_release_s(): keys["s"] = False


def key_press_d(): keys["d"] = True


def key_release_d(): keys["d"] = False


def setup_controls():
    win.listen()
    win.onkeypress(key_press_w, "w")
    win.onkeyrelease(key_release_w, "w")
    win.onkeypress(key_press_a, "a")
    win.onkeyrelease(key_release_a, "a")
    win.onkeypress(key_press_s, "s")
    win.onkeyrelease(key_release_s, "s")
    win.onkeypress(key_press_d, "d")
    win.onkeyrelease(key_release_d, "d")
    win.onkeypress(toggle_pause, "Escape")
    win.listen()


game_running = True
frame_count = 0

powerup_spawn_increase = 0


def spawn_powerup():
    global last_powerup_score, powerups_collected_after_500, powerup_spawn_increase
    if is_paused:
        return

    if current_game_mode and hasattr(current_game_mode, 'inverted_controls') and current_game_mode.inverted_controls:
        return

    if current_game_mode and current_game_mode.mode_id == "chase":
        powerup_interval = 50
    else:
        powerup_interval = powerup_score_interval + (powerup_spawn_increase if score > 500 else 0)

    if score - last_powerup_score >= powerup_interval:
        last_powerup_score = score
        if current_game_mode and current_game_mode.mode_id == "chase":
            kind = random.choice(["invincibility", "speed"])
        else:
            kind = random.choice(["life", "invincibility", "speed"])
        power = turtle.Turtle()
        power.shape("circle")
        if kind == "life":
            power.color("cyan")
        elif kind == "invincibility":
            power.color("purple")
        elif kind == "speed":
            power.color("yellow")
        power.penup()
        power.goto(random.randint(-X_BOUND, X_BOUND), Y_BOUND + 40)
        power.setheading(270)
        power.kind = kind
        powerups.append(power)

def update_powerups():
    if is_paused:
        return
    if current_game_mode and hasattr(current_game_mode, 'inverted_controls') and current_game_mode.inverted_controls:
        return

    for power in powerups[:]:
        power.sety(power.ycor() - 3)
        if is_collision(power, player, 20):
            apply_powerup(power.kind)
            pu.play()
            power.hideturtle()
            powerups.remove(power)
        elif power.ycor() < -Y_BOUND - 20:
            power.hideturtle()
            powerups.remove(power)


def game_loop():
    global frame_count

    if not game_running or is_paused:
        win.update()
        win.ontimer(game_loop, 16)
        return

    now = time.time()


    if not (current_game_mode and current_game_mode.mode_id == "hardcore"):
        if active_powerup:
            time_left = powerup_end_time - now
            if time_left <= 0:
                clear_powerup()
            elif time_left <= 3:
                blink_interval = 0.3
                blink_phase = int((3 - time_left) / blink_interval) % 2
                if blink_phase == 0:
                    set_player_color(powerup_color_map.get(active_powerup, "white"))
                else:
                    set_player_color("white")
            else:
                set_player_color(powerup_color_map.get(active_powerup, "white"))
        else:
            set_player_color("white")

    if active_powerup != "speed":
        move_speed = base_move_speed + (min(score, 300) / 100)

    win.update()
    frame_count += 1

    if use_joystick:
        move_player()
    else:
        move_player_keyboard()

    update_spawn_protection()
    trail_points.append((player.xcor(), player.ycor()))
    draw_trail()

    current_game_mode.update()


    if not (current_game_mode and current_game_mode.mode_id == "hardcore"):
        spawn_powerup()
        update_powerups()

    win.ontimer(game_loop, 16)


menu_pen = turtle.Turtle()
menu_pen.hideturtle()
menu_pen.color("white")
menu_pen.penup()


def draw_stars(num_stars=50):
    menu_pen.color("white")
    for _ in range(num_stars):
        x = random.randint(-X_BOUND, X_BOUND)
        y = random.randint(-Y_BOUND, Y_BOUND)
        menu_pen.penup()
        menu_pen.goto(x, y)
        menu_pen.pendown()
        menu_pen.dot(random.randint(2, 5))


def show_mode_selection():
    menu_pen.clear()
    draw_stars(70)

    menu_pen.goto(0, 150)
    menu_pen.write("Select Game Mode", align="center", font=("Courier", 30, "bold"))

    for i, mode in enumerate(game_modes):
        y_pos = 50 - i * 60
        menu_pen.goto(0, y_pos)
        menu_pen.write(f"{i + 1}. {mode.name}", align="center", font=("Courier", 24, "normal"))
        menu_pen.goto(0, y_pos - 15)
        menu_pen.write(mode.description, align="center", font=("Courier", 16, "normal"))

    win.onkeypress(None, "1")
    win.onkeypress(None, "2")
    win.onkeypress(None, "3")
    win.onkeypress(None, "4")
    win.onkeypress(None, "4")


    def select_mode(mode_index):
        global current_game_mode
        if 0 <= mode_index < len(game_modes):
            current_game_mode = game_modes[mode_index]
            button_click.play()
            start_game()

    win.onkeypress(lambda: select_mode(0), "1")
    win.onkeypress(lambda: select_mode(1), "2")
    win.onkeypress(lambda: select_mode(2), "3")
    win.onkeypress(lambda: select_mode(3), "4")
    win.onkeypress(lambda: select_mode(4), "5")
    win.listen()


def choose_joystick():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        menu_pen.goto(0, 80)
        menu_pen.write("No serial ports found!", align="center", font=("Courier", 16, "normal"))
        return

    menu_pen.clear()
    menu_pen.goto(0, 80)
    menu_pen.write("Available COM Ports:", align="center", font=("Courier", 20, "bold"))

    y_pos = 40
    for i, port in enumerate(ports):
        port_desc = f"{port.device} ({port.description})"
        menu_pen.goto(0, y_pos - i * 30)
        menu_pen.write(f"{i}: {port_desc}", align="center", font=("Courier", 16, "normal"))

    selected = win.textinput("Select Port", "Enter the number of the port:")

    def on_text_input(text):
        global use_joystick, ser
        try:
            index = int(text)
            if 0 <= index < len(ports):
                use_joystick = True
                menu_pen.clear()
                menu_pen.write(f"Selected {ports[index].device}", align="center", font=("Courier", 18, "normal"))
                try:
                    ser = serial.Serial(ports[index].device, 9600, timeout=0.1)
                except Exception:
                    menu_pen.goto(0, -40)
                    menu_pen.write("Failed to open port", align="center", font=("Courier", 14, "normal"))
                    return
                threading.Thread(target=read_joystick, daemon=True).start()
                time.sleep(1)
                menu_pen.clear()
                show_mode_selection()
            else:
                menu_pen.clear()
                menu_pen.write("Invalid number", align="center", font=("Courier", 14, "normal"))
        except:
            menu_pen.clear()
            menu_pen.write("Please enter a valid number", align="center", font=("Courier", 14, "normal"))

    on_text_input(selected)


def choose_keyboard():
    menu_pen.clear()
    show_mode_selection()


def start_menu():
    play_music("loading_menu.mp3")

    menu_pen.clear()
    menu_pen.color("white")
    menu_pen.screen.bgcolor("black")
    draw_stars(70)

    menu_pen.goto(0, 300)
    menu_pen.write("""Space Rush""", align="center", font=("Courier", 40, "bold"))

    menu_pen.goto(0, 267)
    menu_pen.write("""by execRooted""", align="center", font=("Courier", 15, "normal"))

    menu_pen.goto(0, 130)
    menu_pen.write("Choose your control mode to begin:", align="center", font=("Courier", 20, "bold"))

    menu_pen.goto(0, 80)
    menu_pen.write("Press J - Joystick Control", align="center", font=("Courier", 24, "normal"))

    menu_pen.goto(0, 40)
    menu_pen.write("Press K - Keyboard Control (WASD)", align="center", font=("Courier", 24, "normal"))

    menu_pen.goto(0, -120)
    menu_pen.write("Instructions:", align="center", font=("Courier", 18, "bold"))

    menu_pen.goto(0, -300)
    menu_pen.write(
        "- Move using WASD keys or joystick\n"
        "- The 5 HI's on the top of the screen, reprezent your high score in the 5 different levels\n"
        "- Dodge enemies to survive(red balls)\n"
        "- Collect power-ups for advantages(different colored balls)\n"
        "       -Life (cyan): Extra life\n"
        "       -Invincibility (purple): Temporary immunity\n"
        "       -Speed (yellow): Move faster briefly\n",
        align="center", font=("Courier", 14, "normal")
    )

    def on_key_j():
        choose_joystick()
        button_click.play()

    def on_key_k():
        choose_keyboard()
        button_click.play()

    win.onkey(on_key_j, "j")
    win.onkey(on_key_k, "k")
    win.listen()


def start_game():

    if current_game_mode and current_game_mode.mode_id in mode_music:
        play_music(mode_music[current_game_mode.mode_id])
    menu_pen.clear()
    setup_controls()
    reset_game()


start_menu()
win.mainloop()

#This is all. If you found this, have a good day :)
