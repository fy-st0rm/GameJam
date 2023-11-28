from engine import *

MODE_BASE = "BASE"


class Mode:
	def __init__(self, name):
		self.name       = name
		self.health     = 100
		self.attack_dmg = 100
		self.speed      = 5
		self.time       = 0    # 0 = infinity

	def __str__(self) -> str:
		return f"""
{self.name} {{
  health    : {self.health}
  attack_dmg: {self.attack_dmg}
  speed     : {self.speed}
  time      : {self.time}
}}
"""

	def change_health_by(self, percent: float) -> Self:
		self.health += (percent / 100) * self.health
		return self

	def change_attack_dmg_by(self, percent: float) -> Self:
		self.attack_dmg += (percent / 100) * self.attack_dmg
		return self

	def change_speed_by(self, percent: float) -> Self:
		self.speed += (percent / 100) * self.speed
		return self

	def set_time(self, time: float) -> Self:
		self.time = time
		return self


def base_mode() -> Mode:
	return (
		Mode(MODE_BASE)
			.change_health_by(0)
			.change_attack_dmg_by(0)
			.change_speed_by(0)
	)


