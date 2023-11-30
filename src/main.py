from engine import *
from scenes.game import Game
from scenes.menu import Menu

WIDTH  = 800
HEIGHT = 600
FPS = 60


class Main:
	def __init__(self, width: int, height: int, fps: int):
		self.width  = width
		self.height = height
		self.fps    = fps

		self.screen = pygame.display.set_mode((self.width, self.height))

		self.running = True
		self.clock = pygame.time.Clock()

		self.ui_manager = pygame_gui.UIManager((self.width, self.height))

		self.scene_manager = SceneManager()
		self.scene_manager.add("menu", Menu(self.screen, self.ui_manager, self.scene_manager))
		self.scene_manager.add("game", Game(self.screen, self.scene_manager))
		self.scene_manager.switch("menu")

	def run(self):
		last_time = time.time()
		while self.running:

			# Calculating delta time
			dt = time.time() - last_time
			dt *= self.fps
			last_time = time.time()

			self.screen.fill((0, 0, 0))

			self.poll_events()

			t = self.clock.tick(self.fps) / 1000.0

			self.scene_manager.update(dt)
			self.ui_manager.update(t)
			self.ui_manager.draw_ui(self.screen)

			pygame.display.update()

	def poll_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

			self.scene_manager.poll_event(event)
			self.ui_manager.process_events(event)

	def quit(self):
		self.scene_manager.quit()


if __name__ == "__main__":
	pygame.init()
	main = Main(WIDTH, HEIGHT, FPS)
	main.run()
	main.quit()
