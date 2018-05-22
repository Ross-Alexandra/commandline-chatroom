""" PURPOSE:

	Each method in this file can be called with /[command] from a client.


	for example, /quit will cause the code in quit to be run.

   USAGE:

	Any command in this file MUST accept a server object, client, address
	and command_args. They need not use them, but they must accept them.

	Thus, this shall act as the docstring for each of those commands:

	Args:
		server_object(socket): The server that is being run. This is here to allow
					access to things in the server.
		command_args(list): A list of the arguments passed with the command.

	Finally, The /help command will show all available commands.
	Further, the docstring of each function will also be shown to the user, so
	that they have a better understanding of what each function does.
"""
def stop(server_object, command_args):
	""" Stops the server. """

	import os

	server_object.stop()

	#: Exit.
	#os._exit(0)

def change_permission(server_object, command_args):
	"""
		Changes the permissions of a specified user to a specified permission level.
		eg) promote_user Bob admin
	"""

	#: Get the user's IP address
	addr = server_object.get_ip(command_args[1])

	#: Get the new permission's name.
	new_permission = command_args[2]

	#: Attempt to change the permssion and get the return code.
	code = server_object.change_permissions(addr, new_permission)

	#: Handle different codes.
	if code == 1:
		print("Successfully changed permissions.")
	elif code == 0:
		print("User is already {}".format(new_permission))
	else:
		print("{} is an invalid permission type.".format(new_permissions))

def cp(server_object, command_args):
	"""
		Shortcut for change_permission command.
	"""
	change_permission(server_object, command_args)

def say(server_object, command_args):
	"""
		Sends a message to the server
	"""

	#: Join the args into a message
	msg = " ".join(command_args[1:])

	#: Send the message.
	server_object.send_all(msg)
