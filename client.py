import socket
import threading
import json

with open('config.json', 'rb') as f:
    config = json.load(f)
    HOST = config['server-ip']
    PORT = config['server-port']
    FORMAT = config['encoding-format']

def sendMessage(client: socket.socket):
    while True:
        msg = input()
        if msg:
            client.send(msg.encode(FORMAT))

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send('very secret string'.encode(FORMAT))

    messageListener = threading.Thread(target=sendMessage, args=(client,), daemon=True)
    messageListener.start()

    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message:
                print(message)
            else:
                return
        except ConnectionResetError:
            print('[SYSTEM] Server shut down. Disconnecting...')
            return
        except ConnectionAbortedError:
            print('[SYSTEM] leaving chat.')
            return

if __name__ == '__main__':
    main()
    