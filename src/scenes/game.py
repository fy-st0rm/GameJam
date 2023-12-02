from engine import *
from characters.player import *
from characters.selection_box import *

class Game(Scene):
	def __init__(self, surface: pygame.Surface, ui_manager: pygame_gui.UIManager):
		self.ui_manager = ui_manager
		self.surface = surface
		self.player = Player(surface)
		self.selection_box = SBox(surface)
		

	def on_entry(self):
		# ! FIX UI BUGGED OUT
		self.file_dialog = UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                                    self.ui_manager,
                                                    window_title='Load Image...',
                                                    initial_file_path='data/images/',
                                                    allow_picking_directories=True,
                                                    allow_existing_files_only=True,
                                                    allowed_suffixes={""})
		print("Entered game")

	def on_exit(self):
		print("Game exited")

	def on_event(self, event: pygame.event.Event):
		self.player.poll_event(event)
		self.selection_box.poll_event(event)

	def on_update(self, dt: float):
		self.surface.fill((66,66,66))
		self.player.update(dt)
		self.selection_box.update(dt)

