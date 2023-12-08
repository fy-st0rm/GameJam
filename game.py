import pygame as pg
import pygame_gui as pgui
import time
import math
import random
from dataclasses import dataclass
from typing_extensions import Self


# Configs
WINDOW_WIDTH  = 800
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
GUN_DAMAGE = 100
GUN_KICKBACK = 5
GUN_MAX_TIMEOUT = 5
GUN_FIRERATE = 0.5
GUN_COLOR = (255, 0, 0)

ENEMY_SPAWN_VERTICES = [(0,0),(0,0),(0,0),(0,0)]


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

def sin_wave(amp: float, freq: float, t: float) -> float:
	return amp * math.sin(freq * math.radians(t))

def interpolate(src: float, dest: float, speed: float) -> float:
	if src == dest: return src

	if src < dest:
		src += speed
	elif src > dest:
		src -= speed

	return src

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
		if end_pos[0] < start_pos[0] and end_pos[1] < start_pos[1]:
			angle = 180 + angle
		elif end_pos[0] < start_pos[0] and end_pos[1] > start_pos[1]:
			angle = 180 - angle
		elif end_pos[0] > start_pos[0] and end_pos[1] < start_pos[1]:
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

def particle_draw(camera: list[float, float]):
	for p in particles:
		p.pos[0] += p.vel[0]
		p.pos[1] += p.vel[1]
		p.time -= 0.1
		p.radius -= 0.1

		pg.draw.circle(display, p.col, (p.pos[0] - camera[0], p.pos[1] - camera[1]), p.radius)
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


# Camera
camera: list[float, float] = [0, 0]


# Entity
class EntityType:
	PLAYER = 0
	ENEMY  = 1

class EntityState:
	IDLE = 0
	WALK = 1
	DAMAGE = 2
	DEAD = 3

class Entity:
	def __init__(
		self,
		etype: EntityType,
		sprite: pg.Surface,
		rect: pg.Rect,
		speed: float
	):
		self.etype = etype
		self.sprite = sprite
		self.rect = rect
		self.speed = speed
		self.tick = 0
		self.walk_curve = 0
		self.movement = {
			"left" : False,
			"right": False,
			"up"   : False,
			"down" : False
		}

		self.health = 100
		self.state = EntityState.IDLE
		self.vel = [0, 0]
		self.trans_rect = self.rect.copy()
		self.org_sprite = self.sprite.copy()
		self.dmg_sprite = self.sprite.copy()
		self.dmg_sprite.fill((90, 0, 0, 0), special_flags = pg.BLEND_ADD)

	def die(self):
		entities.remove(self)
		pos = [self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2]

		particle_add(
			pos,
			(165, 165, 165),
			[random.choice([-0.01, 0.01]), random.choice([-0.01, -0.1, -0.05])],
			4, 6, 4
		)
		particle_add(
			pos,
			(165, 165, 165),
			[random.choice([-0.01, 0.01]), random.choice([-0.01, -0.1, -0.05])],
			3, 6, 3
		)
		particle_add(
			pos,
			(165, 165, 165),
			[random.choice([-0.01, 0.01]), random.choice([-0.01, -0.1, -0.05])],
			5, 6, 5
		)

	def take_damage(self, damage: float):
		self.health -= damage
		self.state = EntityState.DAMAGE

		if self.health <= 0:
			self.die()

	def update_movement(self, dt: float) -> Self:
		if self.state != EntityState.DAMAGE:
			self.state = EntityState.IDLE
		self.vel = [0, 0]

		if self.movement["left"]:
			self.vel[0] -= self.speed * dt
		if self.movement["right"]:
			self.vel[0] += self.speed * dt
		if self.movement["up"]:
			self.vel[1] -= self.speed * dt
		if self.movement["down"]:
			self.vel[1] += self.speed * dt

		if self.vel[0] or self.vel[1]:
			self.state = EntityState.WALK

		self.rect.x += self.vel[0]
		self.rect.y += self.vel[1]

		return self

	def update_animation(self) -> Self:
		self.trans_rect = self.rect.copy()

		match self.state:
			case EntityState.WALK:
				self.walk_curve = sin_wave(1.5, 15, self.tick)
				self.tick += 1

				if self.vel[0]:
					self.trans_rect.y += self.walk_curve
				elif self.vel[1]:
					self.trans_rect.x += self.walk_curve

				feet = [self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h - 2]

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

			case EntityState.DAMAGE:
				self.sprite = self.dmg_sprite
				self.tick += 0.1

				if self.tick >= 5:
					self.sprite = self.org_sprite
					self.state = EntityState.IDLE

			case default:
				self.tick = 0
				self.walk_curve = 0

		return self

	def draw(self, surface: pg.Surface, camera: list[float, float]):
		surface.blit(self.sprite, (self.trans_rect.x - camera[0], self.trans_rect.y - camera[1]))


# Entity init
entities: list[Entity] = []


# Player
player = Entity(
	EntityType.PLAYER,
	sprite_sheet_get(pg.Rect(2, 0, SPRITE_SIZE, SPRITE_SIZE)),
	pg.Rect(0, 0, SPRITE_SIZE, SPRITE_SIZE),
	2
)
entities.append(player)


# Enemy
enemy = Entity(
	EntityType.ENEMY,
	sprite_sheet_get(pg.Rect(0, 0, SPRITE_SIZE, SPRITE_SIZE)),
	pg.Rect(10, 10, SPRITE_SIZE, SPRITE_SIZE),
	2
)
entities.append(enemy)

def spawn_enemy(positions: list[tuple[int,int]]):
	pos = random.choice(positions)
	enemy = Entity(
		EntityType.ENEMY,
		sprite_sheet_get(pg.Rect(0, 0, SPRITE_SIZE, SPRITE_SIZE)),
		pg.Rect(pos[0], pos[1], SPRITE_SIZE, SPRITE_SIZE),
		2
	)
	entities.append(enemy)


# Enemy Spawn Area
enemy_spawn_area = pg.Rect(
	0,0,
	400,400
)


# Trail
@dataclass
class Trail:
	angle: float
	start_pos: list[float, float]
	end_pos: list[float, float]
	color: tuple[float, float, float]

trails: list[Trail] = []

def add_trail(trail_start: list[float, float], trail_end: list[float, float], angle: float):
	trails.append(Trail(angle, trail_start, trail_end, (255, 255, 255)))

def draw_trail(camera: list[float, float]):
	for trail in trails:
		pg.draw.line(
			display, trail.color,
			(trail.start_pos[0] - camera[0], trail.start_pos[1] - camera[1]),
			(trail.end_pos[0] - camera[0], trail.end_pos[1] - camera[1]), 1
		)
		trail.start_pos = [
			trail.start_pos[0] + 5 * math.cos(math.radians(trail.angle)),
			trail.start_pos[1] + 5 * math.sin(math.radians(trail.angle))
		]

		if dist(trail.start_pos, trail.end_pos) < 10:
			trails.remove(trail)


# Gun
@dataclass
class GunConf:
	dist: float
	len: float
	width: float
	color: tuple[int, int, int]
	range: float
	damage: float
	kickback: float
	timeout: float
	firerate: float

class Gun:
	def __init__(self, conf: GunConf):
		self.conf = conf
		self.fire = False
		self.parent: Entity = None

	def draw_muzzle_flash(self, position: list[float, float]):
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

	def check_hit(self, trail_start: list[float, float], trail_end: list[float, float]):
		for ent in entities:
			if ent.etype == EntityType.ENEMY:
				if ent.rect.clipline(trail_start, trail_end):
					ent.take_damage(self.conf.damage);

	def attach_onto(self, ent: Entity) -> Self:
		self.parent = ent
		return self

	def update_position(self, camera: list[float, float]) -> Self:
		mp = get_mouse_pos()
		center = [
			(self.parent.rect.x) - camera[0] + self.parent.rect.w / 2,
			(self.parent.rect.y) - camera[1] + self.parent.rect.h / 2
		]
		self.angle = calc_angle(center, mp)
		center = [
			self.parent.rect.x + self.parent.rect.w / 2,
			self.parent.rect.y + self.parent.rect.h / 2
		]

		# Calculating gun and muzzle position
		self.gun_start = [
			center[0] + self.conf.dist * math.cos(math.radians(self.angle)),
			center[1] + self.conf.dist * math.sin(math.radians(self.angle))
		]

		self.gun_end = [
			self.gun_start[0] + self.conf.len * math.cos(math.radians(self.angle)),
			self.gun_start[1] + self.conf.len * math.sin(math.radians(self.angle))
		]

		self.muzzle_start = [
			self.gun_start[0] + 3 + self.conf.len * math.cos(math.radians(self.angle)),
			self.gun_start[1] + 3 + self.conf.len * math.sin(math.radians(self.angle))
		]

		return self

	def update_trigger(self) -> Self:
		if self.fire:
			if self.conf.timeout >= GUN_MAX_TIMEOUT:
				self.conf.timeout = 0

				self.conf.dist = interpolate(self.conf.dist, GUN_DIST - self.conf.kickback, 2)

				self.draw_muzzle_flash(self.muzzle_start)

				trail_start = self.gun_end
				trail_end = [
					trail_start[0] + self.conf.range * math.cos(math.radians(self.angle)),
					trail_start[1] + self.conf.range * math.sin(math.radians(self.angle))
				]
				add_trail(trail_start, trail_end, self.angle)

				self.check_hit(trail_start, trail_end)
			else:
				self.conf.timeout += self.conf.firerate
		else:
			self.conf.dist = interpolate(self.conf.dist, GUN_DIST, 1)
		return self

	def draw(self, surface: pg.Surface, camera: list[float, float]):
		pg.draw.line(
			surface, self.conf.color,
			(self.gun_start[0] - camera[0], self.gun_start[1] - camera[1]),
			(self.gun_end[0] - camera[0], self.gun_end[1] - camera[1]),
			self.conf.width
		)


# Gun init
DEFAULT_CONF = GunConf(
	GUN_DIST,
	GUN_LEN,
	GUN_WIDTH,
	GUN_COLOR,
	GUN_RANGE,
	GUN_DAMAGE,
	GUN_KICKBACK,
	GUN_MAX_TIMEOUT,
	GUN_FIRERATE
)

gun = Gun(DEFAULT_CONF)


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

		# Updating camera
		camera[0] += (player.rect.x - camera[0] - DISPLAY_WIDTH  / 2) / 10
		camera[1] += (player.rect.y - camera[1] - DISPLAY_HEIGHT / 2) / 10

		# Enemy Spawn Area
		center = [
			(player.rect.x + player.rect.w / 2) - enemy_spawn_area.w / 2,
			(player.rect.y + player.rect.h / 2) - enemy_spawn_area.h / 2
		]

		enemy_spawn_area.x = center[0]
		enemy_spawn_area.y = center[1]

		ENEMY_SPAWN_VERTICES[0] = (enemy_spawn_area.x, enemy_spawn_area.y)
		ENEMY_SPAWN_VERTICES[1] = (enemy_spawn_area.x + enemy_spawn_area.width, enemy_spawn_area.y)
		ENEMY_SPAWN_VERTICES[2] = (enemy_spawn_area.x + enemy_spawn_area.width, enemy_spawn_area.y + enemy_spawn_area.height)
		ENEMY_SPAWN_VERTICES[3] = (enemy_spawn_area.x, enemy_spawn_area.y + enemy_spawn_area.height)

		# spawn_enemy(ENEMY_SPAWN_VERTICES)

		particle_draw(camera)


		# Updating entities
		for ent in entities:
			(
				ent
					.update_movement(dt)
					.update_animation()
					.draw(display, camera)
			)

		# Updaing gun
		(
			gun
				.attach_onto(player)
				.update_position(camera)
				.update_trigger()
				.draw(display, camera)
		)

		draw_trail(camera)

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

			elif event.key == pg.K_w: player.movement["up"]    = True
			elif event.key == pg.K_a: player.movement["left"]  = True
			elif event.key == pg.K_s: player.movement["down"]  = True
			elif event.key == pg.K_d: player.movement["right"] = True

		elif event.type == pg.KEYUP:
			if event.key == pg.K_w: player.movement["up"]      = False
			elif event.key == pg.K_a: player.movement["left"]  = False
			elif event.key == pg.K_s: player.movement["down"]  = False
			elif event.key == pg.K_d: player.movement["right"] = False

		elif event.type == pg.MOUSEBUTTONDOWN:
			if pg.mouse.get_pressed()[0]:
				gun.fire = True
		elif event.type == pg.MOUSEBUTTONUP:
			if not pg.mouse.get_pressed()[0]:
				gun.fire = False

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
