#! python2

import socket
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

def get_local_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(('google.com', 80))
		ip = s.getsockname()[0]
		s.close()
	except:
		ip = 'N/A'
	return ip

def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user('user', 'user', './../..', perm='elradfmwMT')
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer((get_local_ip(), 2121), handler)
    server.serve_forever()

if __name__ == "__main__":
    print('IP: ' + get_local_ip())
    main()
