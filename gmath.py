import pygame as pg
import math

from config import *

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

