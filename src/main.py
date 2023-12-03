from engine import *
from scenes.game import Game

WIDTH  = 1280
HEIGHT = 720
FPS = 60


class Main:
	def __init__(self, width: int, height: int, fps: int, open_file: str, new_map_name: str):
		pygame.init()
		self.width  = width
		self.height = height
		self.fps    = fps

		self.scale = 4

		self.screen = pygame.display.set_mode((self.width, self.height))
		
		self.running = True
		self.clock = pygame.time.Clock()

		self.scene_manager = SceneManager()
		self.ui_manager = pygame_gui.UIManager((self.width, self.height))

		self.back_surface = pygame.Surface((self.width,self.height))

		self.ui_surface = pygame.Surface((self.width,self.height))

		self.scene_manager.add("game", Game(self.back_surface, self.ui_manager, open_file, new_map_name))
		self.title = pygame_gui.elements.UILabel(
			relative_rect = pygame.Rect(self.width - 200, 0, 200, 50),
			text = "Arsenic Editor v0.0.1",
			manager = self.ui_manager
		)
		self.scene_manager.switch("game")

	def run(self):
		last_time = time.time()
		while self.running:
			
			self.screen.fill((0,0,0,0))
			

			# Calculating delta time
			dt = time.time() - last_time
			dt *= self.fps
			last_time = time.time()
			self.poll_events()

			self.scene_manager.update(dt,self.scale)
			self.ui_manager.update(dt)

			self.clock.tick(self.fps)
			self.ui_surface.fill((0,0,0,100))
			self.ui_manager.draw_ui(self.ui_surface)
			self.screen.blit(self.ui_surface, (0, 0))
			
			
			self.screen.blit(pygame.transform.scale(self.back_surface, (self.width / self.scale, self.height/ self.scale)), (0, 0))
			pygame.display.update()

	def poll_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.MOUSEWHEEL:
				if event.y > 0:
					self.scale = self.scale / 2
					
				if event.y < 0:
					self.scale = self.scale * 2
					
			self.scene_manager.poll_event(event)
			self.ui_manager.process_events(event)

	def quit(self):
		self.scene_manager.quit()

if __name__ == "__main__":
	open_file = ""
	new_map_name = ""
	try:
		opts, args = getopt.getopt(sys.argv[1:],"ho:n:", ["ofile=","nfile="])
		for opt, arg in opts:
			if opt == "-h":
				print('-n [NEW_MAP_NAME]')
				print('-o [OPEN_MAP_FILE].mp')
				exit()
			elif opt in ("-o", "--ofile"):
				open_file = arg
			elif opt in ("-n", "--nfile"):
				new_map_name = arg
	except Exception as e:
		print("TYPE -h FOR HELP")
		exit()
	
		
	
	main = Main(WIDTH, HEIGHT, FPS, open_file, new_map_name)
	main.run()
	main.quit()