from inc import *
from engine.scene_manager import *


class Game(Scene):
	def __init__(self):
		pass

	def on_create(self):
		print("Create game")

	def on_entry(self):
		print("Entered game")

	def on_exit(self):
		print("Game exited")

	def on_event(self, event: pygame.event.Event):
		print("Game event")

	def on_update(self, dt: float):
		print("Game update")

