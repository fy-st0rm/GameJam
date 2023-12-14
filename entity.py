import pygame as pg
from typing_extensions import Self
import random
import time

from particle import *
from containers import *
from gmath import *


# Exp
EXP_VAR = 0
EXP_GAIN_NORMAL = 5
EXP_GAIN_BOSS = 20
EXP_MAX = 100         # Increases every level increased
EXP_MAX_GROWTH = 100
LVL = 0

def get_exp_var() -> int:
	return EXP_VAR

def set_exp_var(x: int) -> None:
	global EXP_VAR
	EXP_VAR = x

class EntityType:
	PLAYER = 0
	ENEMY  = 1
	BOSS = 3

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
		speed: float,
		health: float,
		font: pg.font.Font,
		hit_sound: pg.mixer.Sound,
		reset_boss = None
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
		self.font = font
		self.hit_sound = hit_sound

		self.health = health
		self.state = EntityState.IDLE
		self.vel = [0, 0]

		self.trans_rect = self.rect.copy()
		self.org_sprite = self.sprite.copy()
		self.dmg_sprite = self.sprite.copy()
		self.dmg_sprite.fill((90, 0, 0, 0), special_flags = pg.BLEND_ADD)

		self.reset_boss = reset_boss

	def die(self):
		if self.etype == EntityType.BOSS:
			self.reset_boss()
		
		ENTITIES.remove(self)
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
		global EXP_VAR

		self.health -= damage
		self.state = EntityState.DAMAGE

		self.hit_sound.play()

		# damange taken
		damage_text = self.font.render(f"-{damage}", False, (255,0,0))
		DAMAGE_TAKENS.append({
			"pos": [self.rect.x, self.rect.y],
			"damage": damage_text,
			"time": time.time()
		})

		# exp gaining
		if self.etype == EntityType.ENEMY or self.etype == EntityType.BOSS:
			if self.etype == EntityType.BOSS:
				EXP_VAR += EXP_GAIN_BOSS
			else:
				EXP_VAR += EXP_GAIN_NORMAL

		if self.etype == EntityType.ENEMY:
			EXP_VAR += EXP_GAIN_NORMAL
			exp_text = self.font.render(f"+{EXP_GAIN_NORMAL}", False, (0,255,70))
			EXP_GAINS.append({
				"pos": [self.rect.x, self.rect.y],
				"exp": exp_text,
				"time": time.time()
			})

		if self.health <= 0:
			self.die()

	def update_vel(self) -> Self:
		if self.state != EntityState.DAMAGE:
			self.state = EntityState.IDLE
		self.vel = [0, 0]

		if self.movement["left"]:
			self.vel[0] -= self.speed
		if self.movement["right"]:
			self.vel[0] += self.speed
		if self.movement["up"]:
			self.vel[1] -= self.speed
		if self.movement["down"]:
			self.vel[1] += self.speed

		if self.vel[0] or self.vel[1]:
			self.state = EntityState.WALK

		return self

	def update_position(self, dt: float) -> Self:
		self.rect.x += self.vel[0] * dt
		calc_collision_hor(self)
		self.rect.y += self.vel[1] * dt
		calc_collision_vert(self)

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
		surface.blit(self.sprite,
			(
				self.trans_rect.x  - camera[0],
				self.trans_rect.y  - camera[1]
			)
		)


# Collision
def calc_hit_list(target: Entity) -> list[pg.Rect]:
	hit_list = []

	for ent in ENTITIES:
		if ent != target:
			if target.rect.colliderect(ent.rect):
				hit_list.append(ent.rect)

	return hit_list

def calc_collision_hor(ent: Entity):
	hit_list = calc_hit_list(ent)

	for hit in hit_list:
		if ent.vel[0] > 0:
			ent.rect.right = hit.left
		if ent.vel[0] < 0:
			ent.rect.left = hit.right

def calc_collision_vert(ent: Entity):
	hit_list = calc_hit_list(ent)

	for hit in hit_list:
		if ent.vel[1] > 0:
			ent.rect.bottom = hit.top
		if ent.vel[1] < 0:
			ent.rect.top = hit.bottom


