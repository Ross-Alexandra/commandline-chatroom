class Permissions:

	def __init__(self, name: str, permission_level: int):
		self.permission = name
		self.level = permission_level

	def __str__(self):
		return str(self.permission)
