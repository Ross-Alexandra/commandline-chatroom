import socket
import threading
from getpass import getpass
import argparse
import sys

class chatroomClient:
	""" CLASS DEFINITION

		A client that can talk to the host chatroom server.

	"""

	def __init__(self, host: str, port: int):
		""" self.__init__(str, int)

			Connects to a host server over port port.

			Args:
				host(str): The ip address of the server.
				port(int): the TCP that the server talks over.

		"""

		#: Create the client and connect it to the host server.
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect((host, port))

		#: Create a seperate thread to control listening to messages
		#: coming from the server.
		threading.Thread(target=self.listen).start()

		#: Main loop. This allows the user to send messages to the client.
		while True:
			msg = str(input("You: "))
			self.send(msg)

			if msg == "/exit":
				exit()

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
			elif msg == "SD":

				print("This client was closed due to inactivity")
				self.client.close()
				exit()

			#: Otherwise, print the message to the commandline.
			else:
				print('\r' + msg, end='')

				print("\nYou: ", end='')

	def send(self, msg: str):
		""" Sends the message msg to the server to be processed. """
		self.client.send(msg.encode())


if __name__ == "__main__":

	server = 'localhost'
	port = 34343

	chatroomClient(server, port)
