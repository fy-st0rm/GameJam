import pygame as pg
from dataclasses import dataclass
import math
import time

from containers import *
from gmath import *
# Particle system

@dataclass
class Particle:
	pos: list[float, float]
	vel: list[float, float]
	col: list[float, float, float]
	time: float
	radius: float

def particle_add(
	pos: list[float, float],
	col: list[float, float, float],
	vel: list[float, float],
	time: float,
	amt: int,
	radius: float
):
	for i in range(amt):
		PARTICLES.append(Particle(pos, vel, col, time, radius))

def particle_draw(surface: pg.Surface, camera: list[float, float]):
	for p in PARTICLES:
		p.pos[0] += p.vel[0]
		p.pos[1] += p.vel[1]
		p.time -= 0.1
		p.radius -= 0.1

		pg.draw.circle(surface, p.col, (p.pos[0] - camera[0], p.pos[1] - camera[1]), p.radius)
		if p.time <= 0:
			PARTICLES.remove(p)


# Trail system
@dataclass
class Trail:
	angle: float
	start_pos: list[float, float]
	end_pos: list[float, float]
	color: tuple[float, float, float]

def add_trail(trail_start: list[float, float], trail_end: list[float, float], angle: float):
	TRAILS.append(Trail(angle, trail_start, trail_end, (255, 255, 255)))

def draw_trail(surface: pg.Surface, camera: list[float, float]):
	for trail in TRAILS:
		pg.draw.line(
			surface, trail.color,
			(trail.start_pos[0] - camera[0], trail.start_pos[1] - camera[1]),
			(trail.end_pos[0] - camera[0], trail.end_pos[1] - camera[1]), 1
		)
		trail.start_pos = [
			trail.start_pos[0] + 5 * math.cos(math.radians(trail.angle)),
			trail.start_pos[1] + 5 * math.sin(math.radians(trail.angle))
		]

		if dist(trail.start_pos, trail.end_pos) < 10:
			TRAILS.remove(trail)


# Grenade system
@dataclass
class Grenade:
	angle: float
	start_pos: list[float, float]
	end_pos: list[float, float]


def draw_dmg(surface: pg.Surface, camera: list[float, float]):
	for index, damage in enumerate(DAMAGE_TAKENS):
			surface.blit(damage["damage"], (damage["pos"][0] - camera[0], damage["pos"][1] - camera[1]))
			if (time.time() - damage["time"]) > DAMAGE_DISPLAY_TIME:
				DAMAGE_TAKENS.pop(index)
			else:
				damage["pos"][1] -= 3

def draw_exp(surface: pg.Surface, camera: list[float, float]):
	for index, exp in enumerate(EXP_GAINS):
			surface.blit(exp["exp"], (exp["pos"][0] - camera[0] - 20, exp["pos"][1] - camera[1]))
			if (time.time() - exp["time"]) > DAMAGE_DISPLAY_TIME:
				EXP_GAINS.pop(index)
			else:
				exp["pos"][1] -= 3

