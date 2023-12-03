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

		self.mode_manager = ModeManager()
		self.mode_manager.add(base_mode(), default = True)

		self.player_sprite = SpriteSheet("assets/player.png")

		self.animator = Animator()
		self.animator.add("idle", self.player_sprite.load_strip([0, 0, 16, 16], 2), 0.5)
		self.animator.add("walk", self.player_sprite.images_at([
			[0, 32, 16, 16], [16, 32, 16, 16], [0, 48, 16, 16]
		]), 1)

	def update(self, dt: float):
		self.mode_manager.update()
		curr_mode = self.mode_manager.get()

		vel = [0, 0]
		if self.dirs["up"]:
			vel[1] -= curr_mode.speed * dt
			self.animator.switch("walk")
		if self.dirs["down"]:
			vel[1] += curr_mode.speed * dt
			self.animator.switch("walk")
		if self.dirs["left"]:
			vel[0] -= curr_mode.speed * dt
			self.animator.switch("walk")
		if self.dirs["right"]:
			vel[0] += curr_mode.speed * dt
			self.animator.switch("walk")

		if not self.dirs["up"] and not self.dirs["down"] and not self.dirs["left"] and not self.dirs["right"]:
			self.animator.switch("idle")

		self.rect.x += vel[0]
		self.rect.y += vel[1]

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
		frame = self.animator.get()
		self.surface.blit(frame, (self.rect.x, self.rect.y))
