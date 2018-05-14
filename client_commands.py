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
		client(socket): The client that made the command request.
		address(str): The IP address of the client..
		command_args(list): A list of the arguments passed with the command.

	The docstring for any defined command here must have 2 parts:
		1) A description for what the command will do.
		2) "Permission_level = " and a number defining the minimum permission
		    level needed to run the command.

	Finally, The /command command will show the client all available commands.
	Further, the docstring of each function will also be shown to the user, so
	that they have a better understanding of what each function does.
"""

def quit(server_object, client, address, command_args):
	"""
		Closes the connection to the chatroom.

		Permission_level = 0
	"""

	#: Close the server's connection to the client.
	server_object.close_client(client, address, "quit command")

def commands(server_object, client, address, command_args):
	"""
		Lists out all of the commands for the client.

		Permission_level = 0
	"""

	#: Import inspect so that we can get the docstring.
	import inspect

	msg = ""

	#: Create a formatted string of all the commands, and what they do.
	for command in server_object.client_command_list.keys():

		msg += "\n/" + command + " - "

		#: Get the docstring
		docstring = inspect.getdoc(server_object.client_command_list[command][0])

		#: Ignore the portion containing the permission level.
		docstring = docstring[:docstring.index("Permission_level")]

		msg += docstring.strip()
		msg += "\n"

	client.send(msg.encode())

def promote_user(server_object, client, address, command_args):
	"""
		Changes the permissions of the passed user to the passed permission level.
		eg) /promote_user Bob admin

		Permission_level = 1
	"""

	#: Get the information for who's changing the permission of whose client,
	#: and to what permission.
	changer = server_object.usrs[address]
	changee = command_args[1]
	new_permission = command_args[2]

	#: Get the client's current permissino level.
	cur_permission = server_object.permissions[server_object.get_ip(changee)].permission

	#: Log to the server console that the client's permission has been changed.
	print("{} has changed {}'s permission from {} to {}".format(
			changer,
			changee,
			cur_permission,
			new_permission
		)
	)

	#: Attempt to change the permission, and recieve the error code.
	code = server_object.change_permissions(server_object.get_ip(changee), new_permission)

	#: If the code is -1, then an invalid permission type was passed.
	if code == -1:
		client.send("{} is not a valid permission type.".format(new_permission).encode())

	#: If the code is 0, then the user was already that permission level
	elif code == 0:
		client.send("{} is already {}".format(changee, new_permission).encode())

	#: Otherwise no error was encountered, and the user's permission was changed.
	else:
		client.send("{}'s permission has been updated".format(changee).encode())

def permissions(server_object, client, address, command_args):
	"""
		Gets the permission level for the passed user.
		Eg) /permissions Bob

		Permission_level = 1
	"""

	usr = command_args[1]

	#: Get the permission level of the user
	permission_level = server_object.permissions[server_object.get_ip(usr)].permission

	#: Send that permission level to the caller.
	client.send(permission_level.encode())

def user_list(server_object, client, address, command_args):
	"""
		Gets a list of all of the active users in the server.

		Permission_level = 0
	"""

	msg = ""

	#: Create a formatted string of all the users.
	for usr in server_object.usrs.values():
		msg += usr + '\n'

	client.send(msg.encode())
