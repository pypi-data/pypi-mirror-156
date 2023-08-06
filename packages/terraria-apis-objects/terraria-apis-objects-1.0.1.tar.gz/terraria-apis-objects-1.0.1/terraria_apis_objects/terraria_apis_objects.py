from datetime import timedelta


class Color:
	red = 0
	green = 0
	blue = 0

	def __init__(self, red: int = 0, green: int = 0, blue: int = 0):
		for variable, value in locals().items():
			if variable == "self":
				continue
			if not isinstance(value, int):
				raise TypeError(f"{variable} must be an integer.")
			if value > 255:
				raise ValueError(f"{variable} may not be above 255.")
			if value < 0:
				raise ValueError(f"{variable} may not be negative number.")
		self.red = red
		self.green = green
		self.blue = blue


class Item:
	id = 0
	stack = 0
	prefix = 0

	def __init__(self, id: int = 0, stack: int = 0, prefix: int = 0):
		if not isinstance(id, int):
			raise TypeError(f"id must be an integer.")
		if not isinstance(stack, int):
			raise TypeError(f"stack must be an integer.")
		if not isinstance(prefix, int):
			raise TypeError(f"prefix must be an integer.")

		self.id = id
		self.stack = stack
		self.prefix = prefix


class Buff:
	id = 0
	time = timedelta()

	def __init__(self, id: int = 0, time: timedelta = timedelta()):
		if not isinstance(id, int):
			raise TypeError(f"id must be an integer.")
		if not isinstance(time, timedelta):
			raise TypeError(f"time must be an timedelta.")

		self.id = id
		self.time = time


class SpawnPoint:
	x = 0
	y = 0
	world_id = 0
	world_name = ""

	def __init__(self, x: int = 0, y: int = 0, world_id: int = 0, world_name: str = ""):
		if not isinstance(x, int):
			raise TypeError("x must be an integer.")
		if not isinstance(y, int):
			raise TypeError("y must be an integer.")
		if not isinstance(world_id, int):
			raise TypeError("world_id must be an integer.")
		if not isinstance(world_name, str):
			raise TypeError("world_name must be a string.")

		self.x = x
		self.y = y
		self.world_id = world_id
		self.world_name = world_name
