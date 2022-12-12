import socket
import threading
import curses

# HOST = '193.138.7.205'
HOST = '10.112.221.32'
PORT = 54950
FORMAT = 'utf-8'

class UI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.messagearea = curses.newwin(curses.LINES-6, curses.COLS-2, 1, 1)
        self.inputarea = curses.newwin(4, curses.COLS-2, curses.LINES-5, 1)
        self.inputareacoords = self.inputarea.getbegyx()
        self.displayedmessages = []
        
        self.stdscr.border()
        self.inputarea.border()

        self.stdscr.addstr(0, 1, 'Messages')
        
        self.inputarea.addstr(0, 1, 'Input')
        self.inputarea.addstr(1, 1, '>')

        self.stdscr.move(self.inputareacoords[0]+1, self.inputareacoords[1]+2)

        self.stdscr.refresh()
        self.messagearea.refresh()
        self.inputarea.refresh()
    
    def addNewMessage(self, msg):
        if len(self.displayedmessages) >= 22:
            self.displayedmessages.pop(0)
        self.displayedmessages.append(msg)
        
        self.messagearea.clear()
        for message in self.displayedmessages:
            self.messagearea.addstr(message+'\n')
        self.messagearea.refresh()
        self.inputarea.refresh()

    def getMessage(self) -> str:
        curr_message = []
        while True:
            self.inputarea.clear()
            self.inputarea.border()

            self.inputarea.addstr(0, 1, 'Input')
            self.inputarea.addstr(1, 1, '>')

            self.inputarea.addstr(''.join(curr_message))
            self.inputarea.refresh()

            char = self.inputarea.getkey()
            if char in ('KEY_BACKSPACE', '\b', '\x7f', '\x08'):
                if curr_message != []:
                    curr_message.pop()
            elif char in ('\n', '\r\n', '\f'):
                msg = ''.join(curr_message)
                curr_message.clear()
                self.inputarea.refresh()
                return msg
            else:
                if len(curr_message) >= curses.COLS-5:
                    continue
                curr_message.append(char)

def sendMessage(client: socket.socket, screen: UI):
    while True:
        msg = screen.getMessage()
        client.send(msg.encode(FORMAT))

def main(stdscr):
    screen = UI(stdscr)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send('very secret string'.encode(FORMAT))

    messageListener = threading.Thread(target=sendMessage, args=(client, screen), daemon=True)
    messageListener.start()

    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message:
                screen.addNewMessage(message)
            else:
                return
        except ConnectionResetError:
            screen.addNewMessage('[SYSTEM] Server shut down. Disconnecting...')
            return
        except ConnectionAbortedError:
            screen.addNewMessage('[SYSTEM] leaving chat.')
            return

if __name__ == '__main__':
    curses.wrapper(main)
    