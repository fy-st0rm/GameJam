from typing_extensions import Self
import random

from particle import *
from entity import *
from gmath import *

GUN_DIST = 15
GUN_LEN  = 10
GUN_WIDTH = 1
GUN_RANGE = 1000
GUN_DAMAGE = 100
GUN_KICKBACK = 5
GUN_MAX_TIMEOUT = 5
GUN_FIRERATE = 0.5
GUN_COLOR = (0, 180, 180)
GUN_LIFETIME = 0


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
	lifetime: float

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
		for ent in ENTITIES:
			if ent.etype == EntityType.ENEMY or ent.etype == EntityType.BOSS:
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

	def generate_trails(self):
		assert(False, "Generate trail hasnt been implemented")

	def update_trigger(self, shoot_sound: pg.mixer.Sound) -> Self:
		if self.fire:
			if self.conf.timeout >= GUN_MAX_TIMEOUT:
				shoot_sound.play()
				self.conf.timeout = 0
				self.conf.dist = interpolate(self.conf.dist, GUN_DIST - self.conf.kickback, 2)
				self.draw_muzzle_flash(self.muzzle_start)
				self.generate_trails()
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

