import socket
import threading

HOST = '193.138.7.205'
PORT = 54950
FORMAT = 'utf-8'

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
    