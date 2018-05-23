import socket
import threading
from getpass import getpass
import argparse
import sys
import os
import time

class chatroomClient:
	""" CLASS DEFINITION

		A client that can talk to the host chatroom server.

	"""

	def __init__(self):
		""" self.__init__(str, int)

			Connects to a host server over port port.

			Args:
				host(str): The ip address of the server.
				port(int): the TCP that the server talks over.

		"""

		#: Create the client and connect it to the host server.
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#: Create a seperate thread to control listening to messages
		#: coming from the server.
		self.listen_thread = threading.Thread(target=self.listen)

		#: Create a seperate thread to control displaying messages.
		#: Handling this seperatedly from listening for messages
		#: ensures that messages aren't lost in the time it takes
		#: for a message to be displayed.
		self.messages = []
		self.display_thread = threading.Thread(target=self.display_messages)

		self.joined = True

		#: Used to ensure you: doesnt appear twice.
		self.displayed_you = False

	def join(self, host: str, port: int, silent: bool = False):
		""" self.join(str, int)

			Join the chatroom hosted on host port port.

			Args:
				host(str): The IP address of the host.
				port(int): The port that the chatroom is hosted on.
				silent(bool): If True then this client does not run
					      the message sending loop.

		"""


		#: Connect to the room.
		self.client.connect((host, port))

		self.silent = silent

		self.listen_thread.start()

		self.display_thread.start()

		#: Main loop. This allows the user to send messages to the client.
		while self.joined and not silent:

			#: If a "you: " was displayed by a new message,
			#: Then dont append one now.
			if not self.displayed_you:
				msg = str(input("You: "))
			else:
				self.displayed_you = False
				msg = str(input())

			#: If the client is a part of the server, send
			#: the message.
			if self.joined:
				self.send(msg)

			if msg == "/quit":
				self.quit(True)

			#: Server waits .25s after a recieved message.
			#: This ensures that a user's message will not be
			#: concatinated if they send them too quickly.
			#: No security risk, if this is changed, only
			#: lost UX.
			#: This may fail with a ping higher than 250.
			time.sleep(.5)

	def quit(self, server_alerted: bool):
		""" Close the connection to the server."""

		#: Ensure the server know's that we're quitting.
		if not server_alerted:
			try:
				self.send("/quit")
			except:
				#: If this fails then no
				#: connection is possible, so continue
				#: to clean up.
				pass

		#: Close down the threads and the connection.
		self.joined = False
		self.client.close()

	def display_messages(self):
		"""
			Displays recieved messages.
			This ensures that recieved messages dont get lost
			by the time this display takes.
		"""

		while self.joined:
			if len(self.messages) != 0:
				for msg in self.messages:
					#: If the message is empty, ignore it.
					if msg == "":
						continue

					#: If the message is close", then the server has told the client
					#: to shut down, so it will. This is not an issue, as users
					#: messages will always have an identifier and : before their
					#: message, thus,the only messages that don't include an
					#: identifier will be from the server itself.
					elif msg[:5] == "close":

						reason = msg[6:]

						print("This client was closed due to {}.".format(reason))
						self.quit(True)

					#: Otherwise, print the message to the commandline.
					elif not self.silent:
						print('\r' + msg, end='')

						print("\nYou: ", end='')
						self.displayed_you = True

					#: Remove the processed message
					self.messages.remove(msg)

	def listen(self):
		"""
			Listens for messages having come from the host.
		"""

		print("Connected to the room")

		#: Watch for messages coming from the server.
		while self.joined:

			#: Wait for a message to be recieved from the server.
			try:
				self.messages.append(self.client.recv(1024).decode())
			except OSError:
				print("Connection to the server has been lost.")

				#: Quit from the server to do cleanup.
				self.quit(False)

	def send(self, msg: str):
		""" Sends the message msg to the server to be processed. """
		self.client.send(msg.encode())


if __name__ == "__main__":

	#: Create an argument parser.
	parser = argparse.ArgumentParser(description='Connects to a chatroom server.')

	#: Add an argument to get the host IP.
	#: Due to how sockets work, it is not reccommended to
	#: supply a --host flag if you dont know what you're doing.
	parser.add_argument('-s', '--server', type=str,
			   help='The IP the server is hosted on.')

	#: Add an argument to get the host port.
	parser.add_argument('-p', '--port', type=int, help='The port the server is on.')

	#: Parse the arguments
	args = parser.parse_args()

	#: Get the information passed by the argument parser and store it.
	if args.server is None:
		server = str(input("Please enter the IP address to connect to: "))
	else:
		server = args.server

	if args.port is None:
		port = str(input("Please enter the port to connect to: "))
	else:
		port = args.port

	if server == "":
		server = "localhost"
	if port == "":
		port = 34343
	else:
		port = int(port)

	client = chatroomClient()
	client.join(server, port)
