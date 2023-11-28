from engine import *
from characters.player import *

class Game(Scene):
	def __init__(self, surface: pygame.Surface):
		self.player = Player(surface)

	def on_entry(self):
		print("Entered game")

	def on_exit(self):
		print("Game exited")

	def on_event(self, event: pygame.event.Event):
		self.player.poll_event(event)

	def on_update(self, dt: float):
		self.player.update(dt)

