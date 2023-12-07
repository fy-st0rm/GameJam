import pygame as pg
import pygame_gui as pgui
import time
import math
import random
from dataclasses import dataclass


# Configs
WINDOW_WIDTH	= 800
WINDOW_HEIGHT = 600

DISPLAY_WIDTH  = WINDOW_WIDTH / 3
DISPLAY_HEIGHT = WINDOW_HEIGHT / 3

BG_COLOR = (36, 36, 36)

SPRITE_SHEET = "assets/sprites.png"
SPRITE_COLOR_KEY = (255, 0, 255)
SPRITE_SIZE = 16
FPS = 60

GUN_DIST = 15
GUN_LEN  = 10
GUN_WIDTH = 1
GUN_RANGE = 1000
GUN_KICKBACK = 5
GUN_MAX_TIMEOUT = 5
GUN_FIRERATE = 0.5
GUN_COLOR = (255, 0, 0)


# Inits
pg.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display = pg.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
ui_surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

ui_manager = pgui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pg.time.Clock()


# Main menu
title = pgui.elements.UILabel(
	relative_rect = pg.Rect(300, 100, 200, 50),
	text = "Game",
	manager = ui_manager
)

start_button = pgui.elements.UIButton(
	relative_rect = pg.Rect(350, 275, 100, 50),
	text = "Start",
	manager = ui_manager
)

quit_button = pgui.elements.UIButton(
	relative_rect = pg.Rect(350, 375, 100, 50),
	text = "Quit",
	manager = ui_manager
)

def menu_show():
	title.show()
	start_button.show()
	quit_button.show()

def menu_hide():
	title.hide()
	start_button.hide()
	quit_button.hide()


# Math
def clamp(n, min, max): 
	if n < min:
		return min
	elif n > max:
		return max
	else:
		return n

def dist(start: list[float, float], end: list[float, float]) -> float:
	return math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)

def get_mouse_pos() -> list[float, float]:
	mp = pg.mouse.get_pos()
	mp = [
		mp[0] / WINDOW_WIDTH * DISPLAY_WIDTH,
		mp[1] / WINDOW_HEIGHT * DISPLAY_HEIGHT
	]
	return mp

def calc_angle(start_pos: list[float, float], end_pos: list[float, float]) -> float:
		P = abs(end_pos[1] - start_pos[1])
		B = abs(end_pos[0] - start_pos[0])
		angle = math.degrees(math.atan2(P, B))

		# Angle resolution
		if end_pos[0] < start_pos[0] and end_pos[1] < center[1]:
			angle = 180 + angle
		elif end_pos[0] < start_pos[0] and end_pos[1] > center[1]:
			angle = 180 - angle
		elif end_pos[0] > start_pos[0] and end_pos[1] < center[1]:
			angle = 360 - angle
		else:
			angle = 360 + angle

		return angle


# Particle
@dataclass
class Particle:
	pos: list[float, float]
	vel: list[float, float]
	col: list[float, float, float]
	time: float
	radius: float

particles: list[Particle] = []

def particle_add(
	pos: list[float, float],
	col: list[float, float, float],
	vel: list[float, float],
	time: float,
	amt: int,
	radius: float
):
	for i in range(amt):
		particles.append(Particle(pos, vel, col, time, radius))

def particle_draw():
	for p in particles:
		p.pos[0] += p.vel[0]
		p.pos[1] += p.vel[1]
		p.time -= 0.1
		p.radius -= 0.2

		pg.draw.circle(display, p.col, p.pos, p.radius)
		if p.time <= 0:
			particles.remove(p)


# Spritesheet
sprite_sheet: pg.Surface = pg.image.load(SPRITE_SHEET)

def sprite_sheet_get(rect: pg.Rect) -> pg.Surface:
	rect.x *= rect.w
	rect.y *= rect.h

	sprite = pg.Surface(rect.size)
	sprite.set_colorkey(SPRITE_COLOR_KEY)
	sprite.fill(SPRITE_COLOR_KEY)
	sprite.blit(sprite_sheet, (0, 0), rect)
	return sprite


# Player
player_sprite = sprite_sheet_get(pg.Rect(2, 0, SPRITE_SIZE, SPRITE_SIZE))
player_rect = pg.Rect(0, 0, SPRITE_SIZE, SPRITE_SIZE)
player_speed = 2
player_tick = 0
player_walk_curve = 0
player_movement = {
	"left" : False,
	"right": False,
	"up"   : False,
	"down" : False
}

def walk_curve(amp: float, freq: float, t: float) -> float:
	return amp * math.sin(freq * math.radians(t))


# Trail
@dataclass
class Trail:
	angle: float
	start_pos: list[float, float]
	end_pos: list[float, float]
	color: tuple[float, float, float]

trails: list[Trail] = []

def add_trail(trail_start: list[float, float], angle: float):
	trail_end = [
		trail_start[0] + gun_range * math.cos(math.radians(angle)),
		trail_start[1] + gun_range * math.sin(math.radians(angle))
	]
	trails.append(Trail(angle, trail_start, trail_end, (255, 255, 255)))

def draw_trail():
	for trail in trails:
		pg.draw.line(display, trail.color, trail.start_pos, trail.end_pos, 1)
		trail.start_pos = [
			trail.start_pos[0] + 5 * math.cos(math.radians(trail.angle)),
			trail.start_pos[1] + 5 * math.sin(math.radians(trail.angle))
		]

		if dist(trail.start_pos, trail.end_pos) < 10:
			trails.remove(trail)


# Gun
gun_dist  = GUN_DIST
gun_len   = GUN_LEN
gun_width = GUN_WIDTH
gun_color = GUN_COLOR
gun_range = GUN_RANGE
gun_kickback = GUN_KICKBACK
gun_timeout  = GUN_MAX_TIMEOUT
gun_firerate = GUN_FIRERATE
gun_fire = False

def gun_interpolate(src: float, dest: float, speed: float) -> float:
	if src == dest: return src

	if src < dest:
		src += speed
	elif src > dest:
		src -= speed

	return src

def draw_muzzle_flash(position: list[float, float]):
	mp = get_mouse_pos()
	vel = [0, 0]

	if mp[0] > position[0]:
		vel[0] = 1
	elif mp[0] < position[0]:
		vel[0] = -1

	if mp[1] > position[1]:
		vel[1] = 1
	elif mp[1] < position[1]:
		vel[1] = -1

	# YELLOW_NOZZLE_FLASH_FORWARD
	particle_add(
			position, (240, 206, 65),
			vel,
			1, random.choices([0, 1], weights=(20,80))[0], 3
	)

	# RED_NOZZLE_FLASH_FORWARD
	particle_add(
			position, (255, 90, 0),
			vel,
			2, random.choices([0, 1], weights=(20,80))[0], 3
	)

	# RED_NOZZLE_UP_DOWN
	particle_add(
			position, (255, 90, 0),
			[1, random.randint(-1,1)],
			2, random.choices([0, 1], weights=(20,80))[0], 2
	)

	# YELLOW_NOZZLE_UP_DOWN
	particle_add(
			position, (240, 206, 65),
			[1, random.randint(-1,1)],
			1, random.choices([0, 1], weights=(20,80))[0], 2
	)

# Main loop
game = False
running = True
last_time = time.time()

while running:
	# Calculating delta time
	dt = time.time() - last_time
	dt *= FPS
	last_time = time.time()
	tick = clock.tick(FPS)

	# Gameloop
	if game:
		display.fill(BG_COLOR)

		# Player logic
		vel = [0, 0]
		if player_movement["left"]:
			vel[0] -= player_speed * dt
		if player_movement["right"]:
			vel[0] += player_speed * dt
		if player_movement["up"]:
			vel[1] -= player_speed * dt
		if player_movement["down"]:
			vel[1] += player_speed * dt

		player_rect.x += vel[0]
		player_rect.y += vel[1]

		# Player walk animation and particle
		p_tmp_rect = player_rect.copy()
		if vel[0] or vel[1]:
			player_walk_curve = walk_curve(1.5, 15, player_tick)
			player_tick += 1

			if vel[0]:
				p_tmp_rect.y += player_walk_curve
			elif vel[1]:
				p_tmp_rect.x += player_walk_curve

			feet = [player_rect.x + player_rect.w / 2, player_rect.y + player_rect.h - 2]

			particle_add(
				feet, (165, 165, 165),
				[random.randint(-1, 1), 0],
				4, random.choices([0, 1], weights=(70,30))[0], 3
			)
			particle_add(
				feet, (110, 110, 110),
				[random.randint(-1, 1), 0],
				4, random.choices([0, 1], weights=(70,30))[0], 3
			)
		else:
			player_tick = 0
			player_walk_curve = 0

		# Weapon Holding
		mp = get_mouse_pos()
		center = [
			player_rect.x + player_rect.w / 2,
			player_rect.y + player_rect.h / 2
		]
		angle = calc_angle(center, mp)

		# Calculating gun position
		gun_start = [
			center[0] + gun_dist * math.cos(math.radians(angle)),
			center[1] + gun_dist * math.sin(math.radians(angle))
		]

		gun_end = [
			gun_start[0] + gun_len * math.cos(math.radians(angle)),
			gun_start[1] + gun_len * math.sin(math.radians(angle))
		]

		muzzle_start = [
			gun_start[0] + 3 + gun_len * math.cos(math.radians(angle)),
			gun_start[1] + 3 + gun_len * math.sin(math.radians(angle))
		]

		# Firing
		if gun_fire:
			if gun_timeout >= GUN_MAX_TIMEOUT:
				gun_dist = gun_interpolate(gun_dist, GUN_DIST - gun_kickback, 2)
				draw_muzzle_flash(muzzle_start)
				add_trail(gun_end, angle)
				gun_timeout = 0
			else:
				gun_timeout += gun_firerate
		else:
			gun_dist = gun_interpolate(gun_dist, GUN_DIST, 1)

		# Draw
		particle_draw()
		draw_trail()
		display.blit(player_sprite, (p_tmp_rect.x, p_tmp_rect.y))
		pg.draw.line(display, gun_color, gun_start, gun_end, gun_width)

		screen.blit(pg.transform.scale(display, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
	
	# UI loop
	else:
		ui_surface.fill((0, 0, 0))
		t = tick / 1000.0

		ui_manager.update(t)
		ui_manager.draw_ui(ui_surface)
		screen.blit(ui_surface, (0, 0))

	# Event
	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False

		# Controls
		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				menu_show()
				game = False

			elif event.key == pg.K_w: player_movement["up"]    = True
			elif event.key == pg.K_a: player_movement["left"]  = True
			elif event.key == pg.K_s: player_movement["down"]  = True
			elif event.key == pg.K_d: player_movement["right"] = True

		elif event.type == pg.KEYUP:
			if event.key == pg.K_w: player_movement["up"]      = False
			elif event.key == pg.K_a: player_movement["left"]  = False
			elif event.key == pg.K_s: player_movement["down"]  = False
			elif event.key == pg.K_d: player_movement["right"] = False

		elif event.type == pg.MOUSEBUTTONDOWN:
			if pg.mouse.get_pressed()[0]:
				gun_fire = True
		elif event.type == pg.MOUSEBUTTONUP:
			if not pg.mouse.get_pressed()[0]:
				gun_fire = False

		# UI
		elif event.type == pgui.UI_BUTTON_PRESSED:
			if event.ui_element == start_button:
				menu_hide()
				game = True
			elif event.ui_element == quit_button:
				pg.event.post(pg.event.Event(pg.QUIT))

		ui_manager.process_events(event)

	# Updates
	pg.display.update()


# Cleaup
pg.quit()
