import socket
import threading
import traceback
import time
import argparse
import os

"""
TODO:
	- Create GUI interface for both the client and host

	- Create testing suite
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

		import commands
		import permissions

		#: Store the server information.
		self.host = host
		self.port = port

		#: Create a socket.
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#: Bind the socket to the host and port to act as the host.
		self.server.bind((host, port))

		#: Used to hold all the messages that come in on one update.
		self.messages = []

		#: Used to hold the usernames assosiated to addresses.
		self.usrs = {'': "Server"}

		#: A list of connected clients.
		self.clientlist = []

		#: A dictionary relating clients to their controlling threads.
		self.client_threads = {}

		#: Create an internal list of all the client commands.
		self.client_command_list = commands.client_command_list

		#: Create an internal list of all the server commands.
		self.server_command_list = commands.server_command_list

		#: Get a dictionary of the types of permissions availiable.
		self.permission_types = permissions.permission_types

		#: Read from the relevant permissions files to create a dictionary
		#: of addresses relating to their respective permission levels.
		self.permissions = {}
		for permission_type in self.permission_types.keys():

			p_type = self.permission_types[permission_type]

			#: For each IP assosiated with this permission
			#: level, create a dictionary entry with the
			#: IP as the key, and the permission level as
			#: the value.
			for client_addr in p_type.get_clients():
				self.permissions[client_addr] = p_type

		#: Allow threads to start when created.
		self.running = True

		print("Server object initialized.")

	def start(self, max_connections: int = 5, inactivity_timeout: int = 60, no_client: bool= False):
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
		self.get_clients_thread = threading.Thread(target=self.get_clients).start()

		#: Create a thread that checks if any messages have been sent.
		#: If a message has been sent, then this thread will handle sending
		#: the message to all other users.
		self.handle_messaging_thread = threading.Thread(target=self.handle_messaging).start()

		while self.running and not no_client:
			cmd = str(input())

			cmd_args = cmd.split(" ")

			try:
				self.server_command_list[cmd_args[0].replace('!', '')](self, cmd_args)
			except:

				#: For debugging use, if a ! is in a command,
				#: a traceback will be printed if errors occur.
				if '!' in cmd_args[0]:
					traceback.print_exc()

				print("Invalid command, please try again. Append '!' to the command for more info.")


	def handle_messaging(self):
		""" self.handle_messaging()

			Handles sending messages to the clients.
		"""
		#: Main loop. This checks the contents of self.messages every
		#: second. If a message exists in self.messages, then send that
		#: message to every user, and clear self.messages.
		while self.running:

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
							#: Unless this is the address is the host (for testing
							#: purposes.)
							if message[1] != address or address == "127.0.0.1":
								client.send(message[0].encode())
						except Exception as e:

							#: Print the exeption's stacktrace.
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

		while self.running:
			#: Wait for a connection to be started. When it is,
			#: collect its information.
			try:
				client, addr = self.server.accept()

			#: OSError will be thrown when self.server.stop
			#: is run. Catch this error and if the server is
			#: shutting down (ie self.runnning is False) then
			#: ignore it and exit, otherwise log the error..
			except OSError:
				if not self.running:
					exit()
				else:
					traceback.print_exc()

			#: Ignore the connecting port.
			addr = addr[0]

			#: Set the client's timeout time to the server's set
			#: timeout.
			client.settimeout(self._inactivity_timeout)

			#: Append this newly connected client to the client list.
			self.clientlist.append((client, addr))

			#: If this IP address has not connected before, then
			#: it's address wont be in any of the permissions
			#: files. This means that we have to create a user entry
			#: for them.
			if addr not in self.permissions.keys():

				#: Change this address's permission level to user
				self.change_permissions(addr, "user")

			#: Create a thread to handle messaging from this new client,
			#: and pass the client and their address to the thread.
			client_thread = threading.Thread(target=self.manage_client, args=(client, addr))
			self.client_threads[addr] = client_thread

			client_thread.start()

	def handle_commands(self, command: str, client, address):
		""" self.handle_commands(str, socket, str)

			Handle's commands sent by the user.


			Args:
				command(str): The command that is to be run.
				client(socket): The client trying to execute the command.
				address(str): The ip of the client.
		"""

		print("Handling command \"{}\" from {}".format(command, address))

		#: Split the command into its arguments
		command_args = command.split(" ")

		#: if the command is a valid command
		if command_args[0] in self.client_command_list.keys():
			try:

				#: Get the user's permission level, and the command's
				#: permission level.
				client_permissions = self.permissions[address].level
				min_permission = self.client_command_list[command_args[0]][1]

				#: If the user may run this command (ie their permission_level is
				#: equal to or greater than that of the command) then run the command.
				if client_permissions >= min_permission:
					self.client_command_list[command_args[0]][0](self, client, address, command_args)

				else:
					#: If the user may not run the command, then inform them of that.
					client.send("You do not have permission to use that command.".encode())

			except:
				traceback.print_exc()
				client.send("{} is not a valid syntax for the command.".format(command).encode())
		else:
			#: Command was invalid, tell the user.
			client.send("{} is not a valid command.".format(command_args[0]).encode())

	def manage_client(self, client, address):
		""" self.manage_client(socket, str)

			Watches for messages to be recieved from the client.
			If the client does not send a message before timeout,
			then close their connection, and remove them from
			the list of connections.

			Args:
				client(socket): The socket to the client.
				address(str): The client's IP address.

		"""

		#: Print to the main server that this user has connected.
		print("Client connected from {}".format(address))

		while self.running:

			#: try-except in case user quits while prompted to enter a username.
			try:
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
			except:
				self.close_client(client, address, "inactivity")
				return

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
		""" self.close_client(socket, str, str)

			Closes the connection to the passed client, and sends a message
			to the server that they have.

			Args:
				client(socket): The client.
				address(str): The client's IP address
				reason(str): The reason for the client to be closed.
		"""

		if reason is None or len(reason) == 0:
			reason = "[NO REASON SPECIFIED]"

		#: Send the shutdown code to the client.
		try:
			client.send("close {}".format(reason).encode())
		except:
			#: User is already gone.
			pass

		#: Append a message to the unprocess messages that the client
		#: has disconnected. Only do this if that user didn't
		#: quit before selecting a username.
		if address in self.usrs.keys():
			self.messages.append(("{} Has disconnected.".format(self.usrs[address]), address))

			#: Remove this user's address from the list of taken names.
			del self.usrs[address]

		#: Reomve the client from the clients list, and close their
		#: connection.
		print("Removing client {} for {}".format(address, reason))

		#: Stop the client's thread, and remove its entry.
		#: if they have a thread.
		if address in self.client_threads.keys():
			del self.client_threads[address]

		#: Remove this client from the list of active clients, and
		#: close the server's connection to the client.
		if (client, address) in self.clientlist:
			self.clientlist.remove((client, address))
		client.close()

	def change_permissions(self, addr, new_permission):
		""" change_permissions(str, str)
			Changes the permission level assosiated with the passed IP address.

			Args:
				addr(str): The IP address of the client to have its permissinon level changed.
				new_permission(str): The new permission level to set the client to.

			Returns:
				0 if that user is already that permission.
				1 if that user's permissions has successfully been updated.
				-1 if the passed permission is invalid.
		"""

		#: If the requested permission is not a valid permission type,
		#: return -1
		if new_permission not in self.permission_types.keys():
			return -1

		#: If the passed IP address already has a permission level assosiated with
		#: them.
		if addr in self.permissions.keys():

			#: Get their current permission level.
			cur_permission = self.permissions[addr]

			#: If their current permission level is the same as their old one,
			#: return 0.
			if cur_permission == new_permission:
				return 0

			else:
				#: Remove the client from the permission's file.
				cur_permission.remove_client(addr)

		#: Open the file pertaining to the permission level that the IP address is being set to
		#: and append the IP address there so that the server will remember this IP
		#: address as having this permission level.
		self.permission_types[new_permission].add_client(addr)

		#: Update the internal permissions list to reflect the change.
		self.permissions[addr] = self.permission_types[new_permission]

		#: Exit success.
		return 1

	def get_ip(self, username):
		""" self.get_ip(str):

			Returns the ip address assosiated with the passed username.

			Args:
				username(str): The username assosiated with the IP address.

		"""

		#: Reverse the usrs dictionary so we can lookup usernames against IP addresses,
		#: and return the IP address.
		reverse_dict = {}
		for key, value, in self.usrs.items():
			reverse_dict[value] = key

		return reverse_dict[username]

	def send_all(self, msg: str):
		"""
			Sends a message to all clients

			Args:
				msg(str): The message to send to all clients.
		"""

		#: Append the message to the messages list to be later
		#: processed.
		self.messages.append(("(server): {}".format(msg), ""))

if __name__ == "__main__":

	#: Create an argument parser.
	parser = argparse.ArgumentParser(description='Starts hosting a chatroom server.')

	#: Add an argument to get the host IP.
	#: Due to how sockets work, it is not reccommended to
	#: supply a --host flag if you dont know what you're doing.
	parser.add_argument('--host', type=str,
			   help='The IP to host the server on (only'
				 'specify this if you know what you\'re doing'
			   )

	#: Add an argument to get the host port.
	parser.add_argument('-p', '--port', type=int, help='The port to host on (Default: 34343).')

	#: Add an argument to get the timeout for each client
	parser.add_argument('-t', '--timeout', type=int,
		             help='The number of seconds for an unresponsive client to be removed')

	parser.add_argument('-c', '--connections', type=int,
			     help='The maximum number of simultanious connected clients.')

	#: Parse the arguments
	args = parser.parse_args()

	#: Get the information passed by the argument parser and store it.
	if args.host is None:
		host = ''
	else:
		host = args.host

	if args.port is None:
		port = 34343
	else:
		port = args.port

	if args.timeout is None:
		timeout = 60
	else:
		timeout = args.timeout

	if args.connections is None:
		connections = 5
	else:
		connections = args.connections

	#: Create the chatroom server, and listen for connections.
	chatroomServer(host, port).start(inactivity_timeout=timeout, max_connections=connections)

