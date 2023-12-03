from engine import *
from scenes.game import Game

WIDTH  = 800
HEIGHT = 600
FPS = 60


class Main:
	def __init__(self, width: int, height: int, fps: int):
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

		self.scene_manager.add("game", Game(self.back_surface, self.ui_manager))
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
			
			self.screen.blit(pygame.transform.scale(self.back_surface, (self.width / self.scale, self.height/ self.scale)), (0, 0))
			self.ui_manager.draw_ui(self.back_surface)
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
	main = Main(WIDTH, HEIGHT, FPS)
	main.run()
	main.quit()
