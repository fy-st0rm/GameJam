from gun import *

@dataclass
class GunType:
	DEFAULT = "DEFAULT"
	SHAWTY = "SHAWTY"
	GOINGBANANAS = "GOINGBANANAS"
	GRENADE_LAUNCHER = "GRENADE_LAUNCHER"


DEFAULT_CONF = GunConf(
	GUN_DIST,
	GUN_LEN,
	GUN_WIDTH,
	GUN_COLOR,
	GUN_RANGE,
	GUN_DAMAGE,
	GUN_KICKBACK,
	GUN_MAX_TIMEOUT,
	GUN_FIRERATE,
	GUN_LIFETIME
)

class Default(Gun):
	def __init__(self):
		self.type = GunType.DEFAULT
		super().__init__(DEFAULT_CONF)

	def generate_trails(self):
		trail_start = self.gun_end
		trail_end = [
			trail_start[0] + self.conf.range * math.cos(math.radians(self.angle)),
			trail_start[1] + self.conf.range * math.sin(math.radians(self.angle))
		]
		add_trail(trail_start, trail_end, self.angle)
		self.check_hit(trail_start, trail_end)


class Shawty(Gun):
	def __init__(self):
		self.type = GunType.SHAWTY
		self.conf: GunConf = GunConf(
			dist = GUN_DIST,
			len  = 8,
			width = 2,
			color = (10, 10, 10),
			range = 100,
			damage = 90,
			kickback = 5,
			timeout = 5,
			firerate = 0.5,
			lifetime = 10
		)
		super().__init__(self.conf)

	def generate_trails(self):
		trail_start = self.gun_end
		trail_end = [
			trail_start[0] + self.conf.range * math.cos(math.radians(self.angle)),
			trail_start[1] + self.conf.range * math.sin(math.radians(self.angle))
		]
		add_trail(trail_start, trail_end, self.angle)
		self.check_hit(trail_start, trail_end)

		trail_end = [
			trail_start[0] + self.conf.range * math.cos(math.radians(self.angle + 5)),
			trail_start[1] + self.conf.range * math.sin(math.radians(self.angle + 5))
		]
		add_trail(trail_start, trail_end, self.angle + 5)
		self.check_hit(trail_start, trail_end)

		trail_end = [
			trail_start[0] + self.conf.range * math.cos(math.radians(self.angle - 5)),
			trail_start[1] + self.conf.range * math.sin(math.radians(self.angle - 5))
		]
		add_trail(trail_start, trail_end, self.angle - 5)
		self.check_hit(trail_start, trail_end)


class GoingBananas(Gun):
	def __init__(self):
		self.type = GunType.GOINGBANANAS
		self.conf: GunConf = GunConf(
			dist = GUN_DIST,
			len  = 13,
			width = 1,
			color = (180, 180, 10),
			range = 500,
			damage = 70,
			kickback = 5,
			timeout = 5,
			firerate = 2,
			lifetime = 10
		)
		super().__init__(self.conf)

	def generate_trails(self):
		trail_start = self.gun_end
		trail_end = [
			trail_start[0] + self.conf.range * math.cos(math.radians(self.angle)),
			trail_start[1] + self.conf.range * math.sin(math.radians(self.angle))
		]
		add_trail(trail_start, trail_end, self.angle)
		self.check_hit(trail_start, trail_end)


class GrenadeLauncher(Gun):
	def __init__(self):
		self.type = GunType.GRENADE_LAUNCHER
		self.conf: GunConf = GunConf(
			dist = GUN_DIST,
			len  = 9,
			width = 3,
			color = (10, 10, 10),
			range = 100,
			damage = 30,
			kickback = 5,
			timeout = 5,
			firerate = 0.3,
			lifetime = 10
		)
		super().__init__(self.conf)

	def generate_trails(self):
		trail_start = self.gun_end
		trail_end = [
			trail_start[0] + self.conf.range * math.cos(math.radians(self.angle)),
			trail_start[1] + self.conf.range * math.sin(math.radians(self.angle))
		]
		self.check_hit(trail_start, trail_end)
