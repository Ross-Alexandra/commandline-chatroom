class Permissions:
	""" A class to contain basic information and functions
	    surrounding every permission type.
	"""

	def __init__(self, name: str, permission_level: int):
		""" Initializes the permission """

		#: Sets the permission's name
		self.permission = name.lower()

		#: Set the permission's permission level.
		self.level = permission_level

		#: Set the filename for the permissions file.
		self.permission_file = name.lower() + "s.perm"

		#: Create the permission file if it doesn't already exist.
		with open(self.permission_file, 'a+') as p_file:
			pass

	def __str__(self):
		""" Return the name of the permission """
		return self.permission

	def get_clients(self):

		clients = []

		#: Open the permission's permission file and get each
		#: address from within.
		with open(self.permission_file, 'r') as p_file:

			#: Each line in the file contains a seperate IP.
			for line in p_file:

				#: Append this IP to the list
				clients.append(line.strip())

		return clients

	def add_client(self, address):
		"""
			Gives a client this permission level.

			Args:
				address(str): The IP address of the client.
		"""

		with open(self.permission_file, 'a+') as p_file:
			p_file.write(str(address) + '\n')


	def remove_client(self, address):
		"""

			Revokes this permission level from the address.

			Args:
				address(str): The IP address of the client.

		"""

		import os

		#: Unassosiate this IP address with its old permission level
		#: by removing it from its old permission level's file.
		with open(self.permission_file, 'r') as p_file:

			#: Create a temp file to reconstruct the file without the
			#: IP address in it.
			with open("__temp_permission_file__.perm", 'w+') as n_file:
				for line in p_file:

					#: If this is not the IP address whose permission is
					#: changing, then write this IP address to the temp file.
					if line.strip() != address.strip():
						n_file.write(line)

		#: Replace the old permission file with the temp file, as the temp file
		#: is exactly the same, but missing the IP address whose permission level
		#: is chaning.
		os.rename("__temp_permission_file__.perm", self.permission_file)
