import socket
import threading
import traceback
import time
import os

"""
TODO:
	- Have commands only executable by users with
	  certain permission levels.

	- Add a host terminal so that admin commands can be run
	  from the host.
"""

class chatroomServer:
	""" CLASS DEFINITION

		A class to control the hosting of the commandline chatroom.
		This class's purpose is to keep track of all of the connected clients
		and to handle messaging between them.

	"""

	def __init__(self, host: str, port: int):
		""" self.__init__(str, int):

			Intialized the server on host, with port port.

			Args:
				host(str): The ip address to host the server on.
				port(int): The TCP port to host on.
		"""

		#: Create a socket.
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#: Bind the socket to the host and port to act as the host.
		self.server.bind((host, port))

		#: Used to hold all the messages that come in on one update.
		self.messages = []

		#: Used to hold the usernames assosiated to addresses.
		self.usrs = {}

		#: A list of connected clients.
		self.clientlist = []

		#: A dictionary relating clients to their controlling threads.
		self.client_threads = {}

		#: Create an internal list of all the commands.
		from server_command_controller import command_list
		self.command_list = command_list

		#: Get a dictionary of the types of permissions availiable.
		from server_permissions import permission_types
		self.permission_types = permission_types

		self.permissions = {}
		for permission_type in self.permission_types.keys():
			with open(permission_type + "s.txt", 'r') as p_file:
				for line in p_file:
					self.permissions[line.strip()] = self.permission_types[permission_type]

		print("Server object initialized.")

	def start(self, max_connections: int = 5, inactivity_timeout: int = 60):
		""" self.listen(int, int):

			The main control method of the server. When this method is run,
			the server boots up, and begins listening for connecting clients,
			and the messages that those clients send.

			Args:
				max_connections(int): The maximum number of allowed clients.
				inactivity_timeout(int): The number of seconds to wait for a
							 client to be considered timed-out.
		"""

		#: Create [max_connections] slots for clients to connect to.
		self.server.listen(max_connections)

		#: Set the private attribute, so that it can be accessed from
		#: another thread.
		self._inactivity_timeout = inactivity_timeout

		#: Allow client connections to be handled by a seperate thread.
		#: Once a client is connected, they are given their own thread
		#: to allow which listens to their messages. If a message is
		#: recieved, then it is appended to self.messages.
		#: This allows the listen connection to simplly watch the contents
		#: of self.messages to know if a message has been recieved.
		threading.Thread(target=self.get_clients).start()

		#: Main loop. This checks the contents of self.messages every
		#: second. If a message exists in self.messages, then send that
		#: message to every user, and clear self.messages.
		while True:

			#: Check if there are any unprocessed messages.
			if len(self.messages) != 0:

				#: If there are, go through each message, and
				#: each connected client, and send that message
				#: to each client in self.clientlist.
				for message in self.messages:
					for client, address in self.clientlist:
						#: If an exception is thrown, then
						#: this client no longer exists, and
						#: should be removed.
						try:
							#: Dont send the message to the client who sent it.
							if message[1] != address or address == "127.0.0.1":
								client.send(message[0].encode())
						except Exception as e:

							traceback.print_exc()

							#: This client is missing, and should be removed.
							self.close_client(client, address, "missing connection")

					#: Log that the message has been sent to each
					#: client to the main server.
					print("Sending message from {} to all".format(message[1]))

				#: Remove all the messages, as they have all now been
				#: processed.
				self.messages = []
			else:

				#: If no messages were recieved, wait one second.
				#: If messages were recieved, then dont wait the
				#: second, as sending a message to each client may
				#: have taken time.
				time.sleep(1)

	def get_clients(self):
		""" self.get_clients

			Watches for attempted connections, and gives them a
			thread to talk over if one is found.

		"""

		while True:
			#: Wait for a connection to be started. When it is,
			#: collect its information.
			client, addr = self.server.accept()

			#: Ignore the connecting port.
			addr = addr[0]

			#: Set the client's timeout time to the server's set
			#: timeout.
			client.settimeout(self._inactivity_timeout)

			#: Append this newly connected client to the client list.
			self.clientlist.append((client, addr))

			print(self.permissions.keys())

			if addr not in self.permissions.keys():
				self.change_permissions(addr, "user")
				self.permissions[addr] = self.permission_types["user"]

			#: Create a thread to handle messaging from this new client,
			#: and pass the client and their address to the thread.
			client_thread = threading.Thread(target=self.manage_client, args=(client, addr))
			self.client_threads[addr] = client_thread

			client_thread.start()

	def handle_commands(self, command: str, client, address):
		""" self.handle_commands(str, socket, tuple)

			Handle's commands sent by the user.


			Args:
				command(str): The command that is to be run.
				client(socket): The client trying to execute the command.
				address(tuple): The ip and port of the client.
		"""

		print("Handling command \"{}\" from {}".format(command, address))

		#: Split the command into its arguments
		command_args = command.split(" ")

		if command_args[0] in self.command_list.keys():
			#: Call the requested command.
			try:
				self.command_list[command_args[0]](self, client, address, command_args)
			except:
				traceback.print_exc()
				client.send("{} is not a valid syntax for the command.".format(command).encode())
		else:
			#: Command was invalid, tell the user.
			client.send("{} is not a valid command.".format(command_args[0]).encode())

	def manage_client(self, client, address):
		""" self.manage_client(socket, tuple)

			Watches for messages to be recieved from the client.
			If the client does not send a message before timeout,
			then close their connection, and remove them from
			the list of connections.

			Args:
				client(socket): The socket to the client.
				address(tuple): A tuple of the client's IP address, and
						their communication port.

		"""

		#: Print to the main server that this user has connected.
		print("Client connected from {}".format(address))

		while True:

			#: Request a username from the new user.
			client.send("Enter a username.".encode())
			usr = client.recv(1024).decode()

			#: Ensure that a username was given, and that it is not already in the room
			if usr.lower() not in [s.lower() for s in self.usrs.values()]\
			   and len(usr) != 0\
			   and usr[0] != '/':

				#: If the username is valid, assign it to the address
				self.usrs[address] = usr

				#: Inform the user that their name was set.
				client.send("Username set to {}.".format(usr).encode())

				#: Inform all other users of their connections.
				self.messages.append(("{} has connected.".format(usr), address))

				#: Break from the get-username loop, as  a valid username was given.
				break
			else:

				#: Otherwise the username was invalid. Inform the user, and get another username.
				client.send("Invalid username. Please try again.".encode())

		#: Loop while the thread is being watched.
		while address in self.client_threads.keys():

			#: Use a try-catch block to tell when the client has
			#: either timed out, or disconnected.
			try:

				#: Wait for a message to be recieved from the
				#: client.
				msg = client.recv(1024).decode()

				#: If the message is not blank, and not a command, then append the message
				#: to the unprocessed messages list, and print to the main
				#: server that this client has sent a message.
				if msg == "":

					#: This message is blank, ignore it.
					continue

				elif msg[0] == "/":

					#: This message is a command, pass it to handle_commands and continue.
					self.handle_commands(msg[1:], client, address)
				else:

					#: Valid message, so append it to the unprocessed messages, and send it along.
					self.messages.append(("({} - {}): {}".format(self.usrs[address], self.permissions[address].permission, msg), address))
					print("Recieved message: \'{}\' from {}".format(msg, address))

			#: All errors that can be produced will result in the
			#: client either being forcefully disconnected.
			except Exception as e:

				traceback.print_exc()
				self.close_client(client, address, "inactivity")

				#: End the thread.
				return False

			finally:

				#: If a message was sent sucessfully, wait one second before
				#: processing another.
				time.sleep(1)

	def close_client(self, client, address, reason: str):
		""" self.close_client(socket, tuple, str)

			Closes the connection to the passed client, and sends a message
			to the server that they have.

			Args:
				client(socket): The client.
				address(tuple): a Tuple of the client's IP address and port.)
				reason(str): The reason for the client to be closed.
		"""

		if reason is None or len(reason) == 0:
			reason = "[NO REASON SPECIFIED]"

		#: Send the shutdown code to the client.
		client.send("close {}".format(reason).encode())

		#: Append a message to the unprocess messages that the client
		#: has disconnected.
		self.messages.append(("{} Has disconnected.".format(self.usrs[address]), address))

		#: Reomve the client from the clients list, and close their
		#: connection.
		print("Removing inactive client {}".format(address))

		#: Stop the client's thread, and remove its entry.
		del self.client_threads[address]

		del self.usrs[address]

		self.clientlist.remove((client, address))
		client.close()

	def change_permissions(self, addr, new_permission):
		"""


			Returns:
				0 if that user is already that permission.
				1 if that user's permissions has successfully been updated.
				-1 if the passed permission is invalid.
		"""

		if addr in self.permissions.keys():
			cur_permission = str(self.permissions[addr]).lower()

			if cur_permission == new_permission:
				return 0

			if new_permission not in self.permission_types.keys():
				return -1

			with open(cur_permission + "s.txt", 'r') as p_file:
				with open("__temp_permission_file__.txt", 'w+') as n_file:
					for line in p_file:
						if line.strip() != addr.strip():
							n_file.write(line)

			os.rename("__temp_permission_file__.txt", cur_permission + "s.txt")

		with open(new_permission + "s.txt", 'a') as user_file:
			user_file.write(str(addr) + '\n')

		self.permissions[addr] = self.permission_types[new_permission]

		return 1

	def get_ip(self, username):
		reverse_dict = {}
		for key, value, in self.usrs.items():
			reverse_dict[value] = key

		return reverse_dict[username]

if __name__ == "__main__":

	#: Creates a public server on port 34343
	host = ''
	port = 34343

	#: Create the chatroom server, and listen for connections.
	chatroomServer(host, port).start(inactivity_timeout=60)

