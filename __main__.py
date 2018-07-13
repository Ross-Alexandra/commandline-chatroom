from chatroomGUI.startClient import clientGUI
from chatroomGUI.startServer import serverGUI
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='place holder script for starting host or clien')
	parser.add_argument('--host', action="store_true", help='host a serevr')
	parser.add_argument('--client', action="store_true", help='connect to a server')

	args = parser.parse_args()

	if args.host:
		serverGUI().start()
	elif args.client:
		clientGUI().start()
	else:
		print("need --host or --client")


