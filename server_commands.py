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

	Finally, The /command command will show the client all available commands.
	Further, the docstring of each function will also be shown to the user, so
	that they have a better understanding of what each function does.
"""

def quit(server_object, client, address, command_args):
	"""
		Closes the connection to the chatroom.
	"""
	server_object.close_client(client, address, "quit command")

def commands(server_object, client, address, command_args):
	"""
		Lists out all of the commands for the client.
	"""

	import inspect

	msg = ""
	for command in server_object.command_list.keys():
		msg += "\n/" + command + " - "
		msg += inspect.getdoc(server_object.command_list[command])
		msg += '\n'

	client.send(msg.encode())

def promote_user(server_object, client, address, command_args):
	"""
		Changes the permissions of the passed user to the passed permission level.
		eg) /promote_user Bob admin
	"""
	changer = server_object.usrs[address]
	changee = command_args[1]
	new_permission = command_args[2]
	cur_permission = server_object.permissions[server_object.get_ip(changee)].permission

	print("{} has changed {}'s permission from {} to {}".format(
			changer,
			changee,
			cur_permission,
			new_permission
		)
	)

	code = server_object.change_permissions(server_object.get_ip(changee), new_permission)

	if code == -1:
		client.send("{} is not a valid permission type.".format(new_permission).encode())

	elif code == 0:
		client.send("{} is already {}".format(changee, new_permission).encode())
	else:
		client.send("{}'s permission has been updated".format(changee).encode())

def permissions(server_object, client, address, command_args):
	"""
		Gets the permission level for the passed user.
		Eg) /permissions Bob
	"""

	usr = command_args[1]
	permission_level = server_object.permissions[server_object.get_ip(usr)].permission

	client.send(permission_level.encode())
