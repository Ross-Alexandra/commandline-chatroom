import unittest
import socket
import time
import threading

from chatroom.client import chatroomClient
from chatroom.host import chatroomServer

class testClient(unittest.TestCase):

	def testJoin(self):
		"""
			This will test to see if a client can
			successfully connect to the server and
			be registered as connected.
		"""

		print("\n---------- testJoin ----------")

		#: Get basic setup
		client = chatroomClient()

		#: Run the tests.
		client.join('localhost', 12345, silent=True)
		time.sleep(.01) #: Give the server time to update.

		#: Check results.
		self.assertTrue(len(self.server.clientlist) == 1)

		#: Clean up
		client.joined = False
		client.client.close()

	def testQuit(self):
		"""
			Test to see if the quit function will successfully
			sever the connection to the server.
		"""

		print("\n---------- testQuit ----------")

		#: Get basic setup
		client = chatroomClient()
		client.client.connect(('localhost', 12345))

		#: Run the tests
		client.quit(False)
		time.sleep(.01) #: Allow time for the server to update.

		#: Check results:
		#: Ensure that the quit message was sent successfully.
		self.assertEqual(len(self.server.clientlist), 0)
		#: Ensure that the quit command sucessfully closed the socket.
		self.assertEqual(client.client.fileno(), -1)


	def testListen(self):

		print("\n---------- testListen ----------")

		#: Get basic setup.
		client = chatroomClient()
		client.client.connect(('localhost', 12345))
		client.silent = True
		client.listen_thread.start()

		time.sleep(.01) #: Give the server time to update.
		server_cnx = self.server.clientlist[0][0]

		#: Run the tests
		server_cnx.send("close Server Test".encode())
		time.sleep(.01) #: Give the server time to update.

		#: Check results
		#: If a socket's fileno() method returns -1, then
		#: the socket has been disconnected.
		self.assertEqual(client.client.fileno(), -1)

	def testSend(self):
		print("\n---------- testSend ----------")

		#: Get basic setup.
		client = chatroomClient()
		client.client.connect(('localhost', 12345))
		client.silent = True

		#: Run the test
		client.send("TEST")
		time.sleep(.01)

		#: Check results.
		self.assertTrue(any("TEST" in msg[0] for msg in self.server.messages))

		#: Cleanup.
		client.quit(False)

	def setUp(self):
		#: Setup necessary structures.
		self.server = chatroomServer('localhost', 12345)
		self.server.start(inactivity_timeout =5, no_console=True)

	def tearDown(self):
		self.server.stop()
