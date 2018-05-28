import unittest
import socket
import time
import traceback
import threading

from chatroom.client import chatroomClient
from chatroom.host import chatroomServer
from chatroom.permissions.permissions import Permissions

class testHost(unittest.TestCase):

	def testStartFunctionality(self):

		print("--------- testStartFunctionality ---------")

		#: Attempt to start the server.
		self.server.start(no_console=True)

		#: If the server did not startup correctly, then
		#: a connection refused error would be thrown by this.
		self.client.join('localhost', 12345, silent=True)

	def testStopFunctionality(self):

		print("--------- testStopFunctionality ----------")

		self.server.start(no_console=True)
		self.server.stop()

		try:
			self.client.join('localhost', 12345, silent=True)
		except ConnectionRefusedError:
			#: Expect a ConnectionRefusedError.
			#: If one is not raised, then there is an issue.
			return
		except:
			print("Wrong error recieved")
			traceback.print_exc()

		#: If we get here, then there is an issue.
		self.assertTrue(False)

	def testHandleMessagingFunctionality(self):

		print("---------- testHandleMessagingFunctionality ---------")

		#: Setup the basics
		self.server.start(no_console = True)

		#: When a client joins, a message is appended once the user has
		#: set a username. Check that this happens.
		self.client.join('localhost', 12345, silent=True)
		self.client.send("t_user")
		time.sleep(.1) #: Allow the server time to send the message,
				#: and for the message to be recieved.

		#: Ensure that the client got a message, and that they only
		#: have one message.
		self.assertEqual(self.client.most_recent_message, "Username set to t_user.")

	def testGetClientsFunctionality(self):
		print("---------- testGetClientsFunctionality ----------")

		#: Setup
		self.server.start(no_console=True)

		#: Have a client connect, if they appear in the clientlist then
		#: get_clients is successfully getting clients.
		self.client.join('localhost', 12345, silent=True)
		time.sleep(.01) #: allow the server time to update.

		#: Check that there is one user in the list.
		self.assertEqual(len(self.server.clientlist), 1)

	def testHandleCommandsFunctionality(self):
		print("---------- testHandleCommandsFunctionality ----------")

		#: Setup
		self.server.start(no_console=True)
		#: Note, if a custom client command "TESTCOMMAND" is created, then
		#: this test will fail.
		test_cmd = '/TESTCOMMAND this is a test'

		#: Have a client connect, and send across a username, then command.
		#: ensure that server's messages have nothing appended when using
		#: an invalid command. This ensures that commands are not treated as
		#: messages.
		self.client.join('localhost', 12345, silent=True)
		self.client.send('t_user')

		time.sleep(0.15)
		self.server.messages = []
		self.client.send(test_cmd)
		time.sleep(.51) #: Wait for the server to see the command.

		print(self.server.messages)
		#: Ensure that there are no messages queued.
		self.assertEqual(len(self.server.messages), 0)
		#: Ensure that the client was told that the command is invalid.
		invalid_msg = "/TESTCOMMAND is not a valid command."
		self.assertEqual("/" + self.client.most_recent_message, invalid_msg)

	def testCloseClientFunctionality(self):
		print("---------- testCloseClientFunctionality ----------")

		#: Setup
		self.server.start(no_console=True)
		self.client.join('localhost', 12345, silent=True)
		time.sleep(0.01) #: Allow time for server to see connection.

		#: Attempt to close the client.
		client, addr = self.server.clientlist[0][0], self.server.clientlist[0][1]
		self.server.close_client(client, addr, "Test")
		time.sleep(0.51) #: Allow time for the server to send message.

		#: Check whether the client AND server agree of a disconnection.
		self.assertNotIn(addr, self.server.client_threads.keys())
		self.assertEqual(self.client.client.fileno(), -1)

	def testChangePermissionsFunctionality(self):
		print("---------- testChangePermissionsFunctionality ----------")

		self.server.permission_types["TEST"] = Permissions('TEST', -1)

		#: Setup
		self.server.start(no_console=True)
		self.client.join('localhost', 12345, silent=True)
		time.sleep(0.01) #: Allow time for the server to send message.

		#: Get the original permission level of the server.
		addr = self.server.clientlist[0][1]
		orig_perm = self.server.permissions[addr]

		#: Change their permission level to a test permission level.
		self.server.change_permissions(addr, 'TEST')
		new_perm = self.server.permissions[addr]

		#: Restore the permission level
		self.server.change_permissions(addr, orig_perm.permission)

		#: Ensure that the permission was changed back and forth.
		self.assertEqual(self.server.permissions[addr], orig_perm)
		self.assertEqual(new_perm, self.server.permission_types['TEST'])

	def testGetIpFunctionality(self):
		print("---------- testGetIpFunctionality ----------")

		#: Setup
		self.server.start(no_console=True)
		self.client.join('localhost', 12345, silent=True)
		time.sleep(0.01) #: Allow time for the server to send message.
		self.client.send("t_user")
		time.sleep(.1) #: Allow time for server to see the message.

		#: Default host ip.
		host_ip = "127.0.0.1"

		addr = self.server.clientlist[0][1]

		self.assertEqual(host_ip, self.server.get_ip("t_user"))

	def testSendAllFunctionality(self):
		print("---------- testSendAllFunctionality ----------")
		spare_client = chatroomClient()

		self.server.start(no_console=True)
		self.client.join('localhost', 12345, silent=True)
		spare_client.join('localhost', 12345, silent=True)
		time.sleep(0.01) #: Give server time to catch up.

		self.server.send_all('test')
		time.sleep(1) #: Allow time for both clients to recieve the message.
			       #: 4 messages need to be sent at a .25s delay

		#: Cleanup
		spare_client.quit(False)

		#: Ensure that the message is recieved by both.
		self.assertEqual(self.client.most_recent_message, "(server): test")
		self.assertEqual(spare_client.most_recent_message, "(server): test")


	def setUp(self):
		print("\n")
		self.server = chatroomServer('localhost', 12345)
		self.client = chatroomClient()

	def tearDown(self):
		self.client.quit(False)
		self.server.stop()

