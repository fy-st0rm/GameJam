from inc import *
from engine.scene_manager import *

from scenes.game import Game

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

		self.scene_manager = SceneManager()
		self.scene_manager.add("game", Game())
		self.scene_manager.switch("game")

	def run(self):
		while self.running:
			self.screen.fill((165, 165, 165))

			self.poll_events()

			self.scene_manager.update(0.0)

			self.clock.tick(self.fps)
			pygame.display.update()

	def poll_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

			self.scene_manager.poll_event(event)

	def quit(self):
		self.scene_manager.quit()


if __name__ == "__main__":
	main = Main(WIDTH, HEIGHT, FPS)
	main.run()
	main.quit()
