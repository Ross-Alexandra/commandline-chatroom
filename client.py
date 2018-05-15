import socket
import threading
from getpass import getpass
import argparse
import sys
import os

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

	def join(self, host: str, port: int):
		""" self.join(str, int)

			Join the chatroom hosted on host port port.

			Args:
				host(str): The IP address of the host.
				port(int): The port that the chatroom is hosted on.

		"""


		#: Connect to the room.
		self.client.connect((host, port))

		self.listen_thread.start()

		#: Main loop. This allows the user to send messages to the client.
		while True:
			msg = str(input("You: "))
			self.send(msg)

			if msg == "/quit":
				os._exit(0)

	def listen(self):

		print("Connected to the room")

		#: Watch for messages coming from the server.
		while True:

			#: Wait for a message to be recieved from the server.
			msg = self.client.recv(1024).decode()

			#: If the message is empty, ignore it.
			if msg == "":
				continue

			#: If the message is SD, then the server has told the client
			#: to shut down, so it will. This is not an issue, as users
			#: messages will always have an identifier and : before their
			#: message, thus,the only messages that don't include an
			#: identifier will be from the server itself.
			elif msg[:5] == "close":

				reason = msg[6:]

				print("This client was closed due to {}.".format(reason))
				self.client.close()
				os._exit(0)

			#: Otherwise, print the message to the commandline.
			else:
				print('\r' + msg, end='')

				print("\nYou: ", end='')

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
		server = 'localhost'
	else:
		server = args.server

	if args.port is None:
		port = 34343
	else:
		port = args.port

	client = chatroomClient()
	client.join(server, port)
