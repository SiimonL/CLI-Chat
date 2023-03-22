import socket
import threading
import json

with open('config.json', 'rb') as f:
    config = json.load(f)
    HOST = config['server-ip']
    PORT = config['server-port']
    FORMAT = config['encoding-format']


class User:
    def __init__(self, socket: socket.socket, username:str=None):
        self.socket = socket
        self.username = username
    
    def send(self, msg: str) -> None:
        self.socket.send(msg.encode(FORMAT))
    
    def recv(self, size: int) -> str:
        return self.socket.recv(size).decode(FORMAT)

    def disconnect(self, users: list) -> None:
        sendToAll(users, f'[SYSTEM] {self.username} left the chat.')
        self.socket.close()
        users.remove(self)


def sendToAll(users: list[User], msg: str) -> None:
    for user in users:
        user.send(msg)

def isVaildUsername(username: str) -> bool:
    return bool(not (' ' in username or not username))


def listenForConnections(server: socket.socket, connections: list[User]):
    while True:
        # Hangs until a new client connects
        comm_sock, _ = server.accept()

        # Validates that the connecting client is actually the client i wrote
        # (Super strong cryptography)
        if comm_sock.recv(1024).decode(FORMAT) != 'very secret string':
            comm_sock.close()
            continue

        newUser = User(comm_sock)
        newUser.send('[SYSTEM] Enter username: ')

        # Hangs until the client sends an username
        username = newUser.recv(128)
        while not isVaildUsername(username):
            # keep askin until they enter a valid username
            newUser.send('[SYSTEM] Not a vaild username!')
            username = newUser.recv(128)

        newUser.username = username

        # Starts a seperate listener thread for every user that connects
        messageListener = threading.Thread(target=listenForMessages, args=(newUser, connections))
        messageListener.start()

        print(f'[LOG] {newUser.username} joined the chat!')
        # Store client instance in list defined in main function
        connections.append(newUser)
        sendToAll(connections, f'[SYSTEM] {newUser.username} joined the chat!')
        newUser.send('[SYSTEM] type anything to chat, /list to list participants or /leave to leave.')


def listenForMessages(user: User, connections: list[User]) -> str:
    while True:
        try:
            # hangs until the user enters something
            message = {'author': user.username, 'content': user.recv(1024)}
        except ConnectionResetError:
            # Handles the client terminating the program early
            print(f'[LOG] {user.username} got a ConnectionResetError. Terminating...')
            user.socket.close()
            connections.remove(user)
            sendToAll(connections, f'[SYSTEM] {user.username} left the chat.')
            return
        
        # parses message
        if message["content"].startswith('/'):
            print(f'[LOG] {user.username} used command {message["content"]}')
            match message["content"].split(' '):
                case ['/leave']:
                    user.disconnect(connections)
                    return
                case ['/list']:
                    participants = ', '.join([conn.username for conn in connections])

                    user.send(f'[SYSTEM] Users: {participants}')
                case _:
                    user.send('[SYSTEM] Command not found.')
        else:
            print(f'[LOG] {message["author"]}: {message["content"]}')
            sendToAll(connections, f'{message["author"]}: {message["content"]}')

def main():
    connections: list[User] = []

    print('[LOG] Starting Server...')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    
    server.listen()
    print('[LOG] Server Started.')

    # Thread that listens for new connections
    connListener = threading.Thread(target=listenForConnections, args=(server, connections), daemon=True)
    connListener.start()

    while True:
        msg = input()
        if msg == 'kill':
            for thread in threading.enumerate():
                print(thread)
            for conn in connections:
                print(conn)
                conn.disconnect(connections)
            break
        elif msg == 'threads':
            for thread in threading.enumerate():
                print(thread)

if __name__ == '__main__':
    main()