from engine import *

class Player:
	def __init__(self, surface: pygame.Surface):
		self.surface = surface

		self.rect = pygame.Rect(0, 0, 100, 100)
		self.dirs = {
			"left" : False,
			"right": False,
			"up"   : False,
			"down" : False
		}

		self.modes: dict[str, Mode] = {}
		self.modes.update({ MODE_BASE: base_mode() })

		self.curr_mode: Mode = self.modes[MODE_BASE]

	def update(self, dt: float):
		vel = [0, 0]
		if self.dirs["up"]:
			vel[1] -= self.curr_mode.speed * dt
		if self.dirs["down"]:
			vel[1] += self.curr_mode.speed * dt
		if self.dirs["left"]:
			vel[0] -= self.curr_mode.speed * dt
		if self.dirs["right"]:
			vel[0] += self.curr_mode.speed * dt

		self.rect.x += vel[0] * dt
		self.rect.y += vel[1] * dt

		self.render()

	def poll_event(self, event: pygame.event.Event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w: self.dirs["up"]    = True
			if event.key == pygame.K_a: self.dirs["left"]  = True
			if event.key == pygame.K_s: self.dirs["down"]  = True
			if event.key == pygame.K_d: self.dirs["right"] = True

		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_w: self.dirs["up"]    = False
			if event.key == pygame.K_a: self.dirs["left"]  = False
			if event.key == pygame.K_s: self.dirs["down"]  = False
			if event.key == pygame.K_d: self.dirs["right"] = False

	def render(self):
		pygame.draw.rect(self.surface, (255, 0, 0, 255), self.rect)
