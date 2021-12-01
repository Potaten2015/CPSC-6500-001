import socket
import json
from pprint import pprint

HOST = '192.168.0.22'
PORT = 80
message = ''
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    connecting = True
    while connecting:
        print('Attempting to connect...')
        try:
            s.connect((HOST, PORT))
            connecting = False
            print('Connected...')
        except Exception as e:
            print('Connecting...', str(e))
    while message != 'end':
        # message = input('Enter Message:\n')
        # encoded = message.encode('utf-8')
        # s.sendall(encoded)
        data = s.recv(1024)
        decoded_data = data.decode('utf-8')
        decoded_data = json.loads(decoded_data)
        print('RECEIVED')
        pprint(json.loads())

