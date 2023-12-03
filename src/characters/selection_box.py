from engine import *

class SBox:
	def __init__(self, surface: pygame.Surface):
		self.surface = surface

		# player
		self.rect = pygame.Rect(0, 0, 16, 16)

		self.dirs = {
			"left" : False,
			"right": False,
			"up"   : False,
			"down" : False
		}

		self.mode_manager = ModeManager()
		self.mode_manager.add(base_mode(), default = True)

		self.map_w = 100
		self.map_h = 100

		self.map_grid = [[0 for i in range(self.map_w)] for y in range(self.map_h)]
		self.drawing = False
		self.erasing = False

		# empty box sprite
		self.emptybox_sprite = pygame.image.load("src/characters/textures/empty_box.png").convert_alpha()
		



	def update(self, dt: float, scale):
		mouseX = pygame.mouse.get_pos()[0]
		mouseY = pygame.mouse.get_pos()[1]

		self.px = int((mouseX*scale)/16)
		self.py = int((mouseY*scale)/16)
		self.rect.x = self.px*scale*scale
		self.rect.y = self.py*scale*scale

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
		
		elif event.type == pygame.MOUSEBUTTONDOWN:
			print(event.button)
			if event.button == 1:
				self.drawing = True
				self.erasing = False
				self.change_map_grid(1)
			elif event.button == 3:
				self.drawing = False
				self.erasing = True
				self.change_map_grid(0)

		elif event.type == pygame.MOUSEBUTTONUP:
			self.drawing = False
			self.erasing = False
		elif event.type == pygame.MOUSEMOTION:
			if self.drawing:
				self.change_map_grid(1)
			if self.erasing:
				self.change_map_grid(0)
			
			
	def change_map_grid(self,value):
		try:
			self.map_grid[self.px][self.py] = value
		except IndexError:
			print("Out of map bounds")


	def render(self):
		pygame.draw.rect(self.surface, (74, 74, 74, 100), self.rect)

		for r in range(len(self.map_grid)):
			for c in range(len(self.map_grid[r])):
				if self.map_grid[c][r] == 1:
					self.block = self.rect = pygame.Rect(c*16, r*16, 16, 16)
					pygame.draw.rect(self.surface, (255, 0, 0, 100), self.block)
				elif self.map_grid[c][r] == 0:
					self.empty_box = self.emptybox_sprite.get_rect()
					self.empty_box.x = c*16
					self.empty_box.y = r*16
					self.surface.blit(self.emptybox_sprite, self.empty_box)


					