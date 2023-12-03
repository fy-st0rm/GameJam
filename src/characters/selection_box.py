from engine import *

class SBox:
	def __init__(self, surface: pygame.Surface, open_file, new_file_name):
		
		# DEF VALS
		self.open_map_data = None
		self.img_tex = []
		self.textures = []
		self.map_grid = []
		self.open_file = open_file
		self.new_file_name = new_file_name
		self.map_name = None
		self.surface = surface
		self.current_tex = 0
		self.map_w = 0
		self.map_h = 0
		self.drawing = False
		self.erasing = False


		# PARSING MAP
		if self.new_file_name == "":
			try:
				with open(f"{self.open_file}","r") as map_file:
					self.open_map_data = json.load(map_file)
				
				# LOADING MAP_NAME
				self.map_name = self.open_map_data["map_name"]

				# LOADING TEXTURES
				for i in range(len(self.open_map_data["map_textures"])):
					self.textures.append(os.path.dirname(self.open_file) +"\\"+self.open_map_data["map_textures"][str(i)])
				
				# LOADING MAP_GRID
				self.map_grid = self.open_map_data["map_data"]

			except Exception as e:
				print("Error loading file")
				print(e)
		else:
			
			# NEW MAP GENERATION
			self.map_h = int(input("MAP_HEIGHT?: "))
			self.map_w = int(input("MAP_WIDTH?: "))
			self.map_grid = [[0 for i in range(self.map_w)] for y in range(self.map_h)]

			# TODO Find a better way to use and load textures
			self.textures = glob.glob('src\\characters\\textures\\*.png')
			self.map_name = self.new_file_name
		
		# LOADING TEXTURES
		for texture in self.textures:
			try:
				self.img_tex.append(pygame.image.load(texture).convert_alpha())
			except Exception as e:
				self.img_tex.append(pygame.image.load("src/characters/textures/def/error.png").convert_alpha())
				print(e)

		# 16 x 16 box
		self.rect = pygame.Rect(0, 0, 16, 16)

		# LOADING MAP_EDITOR TEXTURES
		self.emptybox_sprite = pygame.image.load("src/characters/textures/def/empty_box.png").convert_alpha()
		self.error_sprite = pygame.image.load("src/characters/textures/def/error.png").convert_alpha()
		
	def update(self, dt: float, scale):
		mouseX = pygame.mouse.get_pos()[0]
		mouseY = pygame.mouse.get_pos()[1]

		# GRID STUFF
		self.px = int((mouseX*scale)/16)
		self.py = int((mouseY*scale)/16)
		self.rect.x = self.px*scale*scale
		self.rect.y = self.py*scale*scale

		self.render()

	def poll_event(self, event: pygame.event.Event):
		
		if event.type == pygame.KEYDOWN and event.unicode.isdigit():
			self.current_tex = (int(event.unicode) - 1 )

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_s:
				if event.mod & pygame.KMOD_CTRL:
					# MAP_SAVE_PROCESS
					os.mkdir(f"{self.map_name}")
					tex = {}
					
					for ID, texture in enumerate(self.textures):
						tmp_tex_name = texture.split("\\")[-1]
						shutil.copy(texture,  f"{self.map_name}/{tmp_tex_name}")
						tex.update({ID: tmp_tex_name})

					map_metadata = {
						"map_name": self.map_name,
						"map_textures": tex,
						"map_width": self.map_w,
						"map_height": self.map_h,
						"map_data": self.map_grid
					}

					with open(f"{self.map_name}/{self.map_name}.mp", "w") as out_file:
						json.dump(map_metadata, out_file)
					
					print(f"saved as {self.map_name}/{self.map_name}.mp")
		
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				self.drawing = True
				self.erasing = False
				self.change_map_grid(self.current_tex + 1)
			elif event.button == 3:
				self.drawing = False
				self.erasing = True
				self.change_map_grid(0)

		elif event.type == pygame.MOUSEBUTTONUP:
			self.drawing = False
			self.erasing = False
		elif event.type == pygame.MOUSEMOTION:
			if self.drawing:
				self.change_map_grid(self.current_tex + 1)
			if self.erasing:
				self.change_map_grid(0)
	
	# MAP_GRID STUFF
	def change_map_grid(self,value):
		try:
			self.map_grid[self.px][self.py] = value
		except IndexError:
			print("Out of map bounds")


	def render(self):
		pygame.draw.rect(self.surface, (74, 74, 74, 100), self.rect)

		# RENDERING STUFF
		for r in range(len(self.map_grid)):
			for c in range(len(self.map_grid[r])):
				if self.map_grid[c][r] != 0:
					self.block = self.rect = pygame.Rect(c*16, r*16, 16, 16)
					try:
						self.surface.blit(self.img_tex[self.map_grid[c][r] - 1], self.block)
					except IndexError:
						self.surface.blit(self.error_sprite, self.block)
				elif self.map_grid[c][r] == 0:
					self.empty_box = self.emptybox_sprite.get_rect()
					self.empty_box.x = c*16
					self.empty_box.y = r*16
					self.surface.blit(self.emptybox_sprite, self.empty_box)


					