from engine import *


class AnimationFrame:
	def __init__(self, name: str, speed: float, frames: list[pygame.Surface]):
		self.name = name
		self.speed = speed
		self.frames = frames

		self.index = 0

	def reset(self):
		self.index = 0

	def get(self):
		self.index += 1
		if self.index >= len(self.frames):
			self.index = 0

		return self.frames[self.index]


class Animator:
	def __init__(self):
		self.frames: dict[str, AnimationFrame] = {}
		self.curr_frame: AnimationFrame = None
		self.frame_index = 0

	def add(self, name: str, images: list[pygame.Surface], speed: float):
		length = len(images)
		speed = speed / 10
		frames = []

		for i in np.arange(0, length, speed):
			frames.append(images[int(i)])

		self.frames.update({ name: AnimationFrame(name, speed, frames) })

	def switch(self, name: str):
		if self.curr_frame:
			if self.curr_frame.name == name:
				return

		self.curr_frame = self.frames[name]
		self.curr_frame.reset()

	def get(self):
		return self.curr_frame.get()

