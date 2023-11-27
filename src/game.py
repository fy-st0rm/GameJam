from inc import *


class Game:
	def __init__(self, width: int, height: int, fps: int):
		self.width  = width
		self.height = height
		self.fps    = fps

		self.screen = pygame.display.set_mode((self.width, self.height))

		self.running = True
		self.clock = pygame.time.Clock()

	def run(self) -> None:
		while self.running:
			self.poll_events()

	def poll_events(self) -> None:
		self.screen.fill((165, 165, 165))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

		self.clock.tick(self.fps)
		pygame.display.update()
