if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

from Client import Client

HOST = '127.0.0.1'
PORT = 5555

client = Client(HOST, PORT)
client.process()
