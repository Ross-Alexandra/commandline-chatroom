import socket
import threading
import time

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

		#: A list of connected clients.
		self.clientlist = []


	def listen(self, max_connections: int = 5, inactivity_timeout: int = 60):
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
							if message[1] != address:
								client.send(message[0].encode())
						except:
							print("Removing missing client {}".format(address))
							self.clientlist.remove((client, address))
							client.close()

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

			#: Set the client's timeout time to the server's set
			#: timeout.
			client.settimeout(self._inactivity_timeout)

			#: Append this newly connected client to the client list.
			self.clientlist.append((client, addr))

			#: Create a thread to handle messaging from this new client,
			#: and pass the client and their address to the thread.
			threading.Thread(target=self.manage_client, args=(client, addr)).start()

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

			#: Use a try-catch block to tell when the client has
			#: either timed out, or disconnected.
			try:

				#: Wait for a message to be recieved from the
				#: client.
				msg = client.recv(1024).decode()

				#: If the message is not blank, then append the message
				#: to the unprocessed messages list, and print to the main
				#: server that this client has sent a message.
				if msg == "":
					continue
				elif msg == "/exit":
					raise Error("Disconnect")
				else:
					self.messages.append(("{}: {}".format(address, msg), address))
					print("Recieved message: \'{}\' from {}".format(msg, address))

			#: All errors that can be produced will result in the
			#: client either being forcefully disconnected.
			except:

				#: Send the shutdown code to the client.
				client.send("SD".encode())

				#: Append a message to the unprocess messages that the client
				#: has disconnected.
				self.messages.append(("{} Has disconnected.".format(address), address))

				#: Reomve the client from the clients list, and close their
				#: connection.
				print("Removing inactive client {}".format(address))
				self.clientlist.remove((client, address))
				client.close()

				#: End the thread.
				return False

			finally:

				#: If a message was sent sucessfully, wait one second before
				#: processing another.
				time.sleep(1)


if __name__ == "__main__":

	#: Creates a public server on port 34343
	host = ''
	port = 34343

	chatroomServer(host, port).listen(inactivity_timeout=300)
