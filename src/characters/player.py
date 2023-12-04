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

		# Player sprite
		self.player_width = 32
		self.player_height = 32
		self.player_sprite = SpriteSheet("assets/player.png")

		self.animator = Animator()
		self.anime_speed = 1
		self.animator.add("back", "idle", self.player_sprite.load_strip(pygame.Rect(0, 0, self.player_width, self.player_height), 6), self.anime_speed)
		self.animator.add("back", "walk", self.player_sprite.load_strip(pygame.Rect(0, 1, self.player_width, self.player_height), 8), self.anime_speed)
		self.animator.add("front", "idle", self.player_sprite.load_strip(pygame.Rect(0, 2, self.player_width, self.player_height), 6), self.anime_speed)
		self.animator.add("front", "walk", self.player_sprite.load_strip(pygame.Rect(0, 3, self.player_width, self.player_height), 8), self.anime_speed)

		self.dir = "front"
		self.state = "idle"

	def update(self, dt: float):
		self.mode_manager.update()
		curr_mode = self.mode_manager.get()

		vel = [0, 0]
		if self.dirs["up"]:
			vel[1] -= curr_mode.speed * dt
			self.dir = "back"
			self.state = "walk"
		if self.dirs["down"]:
			vel[1] += curr_mode.speed * dt
			self.dir = "front"
			self.state = "walk"
		if self.dirs["left"]:
			vel[0] -= curr_mode.speed * dt
			self.state = "walk"
		if self.dirs["right"]:
			vel[0] += curr_mode.speed * dt
			self.state = "walk"

		if not self.dirs["up"] and not self.dirs["down"] and not self.dirs["left"] and not self.dirs["right"]:
			self.state = "idle"

		self.animator.switch(self.dir, self.state)

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
