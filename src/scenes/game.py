from engine import *
from characters.selection_box import *

class Game(Scene):
	def __init__(self, surface: pygame.Surface, ui_manager: pygame_gui.UIManager):
		self.ui_manager = ui_manager
		self.surface = surface
		self.selection_box = SBox(surface)
		

	def on_entry(self):
		print("Entered game")

	def on_exit(self):
		print("Game exited")

	def on_event(self, event: pygame.event.Event):
		self.selection_box.poll_event(event)

	def on_update(self, dt: float, scale):
		self.surface.fill((66,66,66))
		self.selection_box.update(dt, scale)

