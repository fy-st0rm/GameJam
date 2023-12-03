from engine import *
from characters.player import *

class Game(Scene):
	def __init__(self, surface: pygame.Surface, scene_manager: SceneManager):
		self.surface = surface
		self.scene_manager = scene_manager

		self.game_surface = pygame.Surface((300, 188))

		self.player = Player(self.game_surface)

	def on_entry(self):
		print("Entered game")

	def on_exit(self):
		print("Game exited")

	def on_event(self, event: pygame.event.Event):
		self.player.poll_event(event)

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.scene_manager.switch("menu")

	def on_update(self, dt: float):
		self.game_surface.fill((165, 165, 165))
		self.player.update(dt)

		self.surface.blit(
			pygame.transform.scale(
				self.game_surface,
				(self.surface.get_width(), self.surface.get_height())
			),
			(0, 0)
		)

