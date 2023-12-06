import pygame as pg
import pygame_gui as pgui
import time
import math
import random
from dataclasses import dataclass


# Configs
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600

DISPLAY_WIDTH  = WINDOW_WIDTH / 3
DISPLAY_HEIGHT = WINDOW_HEIGHT / 3

BG_COLOR = (0, 165, 165)

SPRITE_SHEET = "assets/sprites.png"
SPRITE_COLOR_KEY = (255, 0, 255)
SPRITE_SIZE = 16
FPS = 60


# Inits
pg.init()

screen     = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display    = pg.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
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


# Particle
@dataclass
class Particle:
	pos: list[float, float]
	vel: list[float, float]
	col: list[float, float, float]
	time: float

particles: list[Particle] = []

def particle_add(
	pos: list[float, float],
	col: list[float, float, float],
	vel: list[float, float],
	time: float,
	amt: int
):
	for i in range(amt):
		particles.append(Particle( pos, vel, col, time))

def particle_draw():
	for p in particles:
		p.pos[0] += p.vel[0]
		p.pos[1] += p.vel[1]
		p.time -= 0.1

		pg.draw.circle(display, p.col, p.pos, p.time)
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


# Math
def walk_curve(amp: float, freq: float, t: float) -> float:
	return amp * math.sin(freq * math.radians(t))


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

		if vel[0] or vel[1]:
			player_walk_curve = walk_curve(1.5, 15, player_tick)
			player_tick += 1

			feet = [player_rect.x + player_rect.w / 2, player_rect.y + player_rect.h]
			particle_add(
				feet, (165, 165, 165),
				[random.randint(-1, 1), random.randint(-1, 1)],
				3, random.randint(0, 1)
			)
		else:
			player_tick = 0
			player_walk_curve = 0

		display.blit(player_sprite, (player_rect.x, player_rect.y + player_walk_curve))

		# Particles
		particle_draw()

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
