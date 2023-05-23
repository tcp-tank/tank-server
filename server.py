from socket import AF_INET, SOCK_STREAM, socket, error
from threading import Thread

class Client:
    def __init__(self, addr):
        self.addr = addr
        self.username = ""
        self.logged_in = False
    def login(self, username):
        self.username = username
        self.logged_in = True
    def logout(self):
        self.logged_in = False

class Server:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 4567
        self.BUFFER_SIZE = 1024
        self.ADDR = (self.HOST, self.PORT)
        self.connections = {}
        self.server = socket(AF_INET, SOCK_STREAM)

    def start(self):
        try:
            self.server.bind(self.ADDR)
            self.server.listen()
            print("Server is running on port:", self.PORT)
            # Start Accept Thread
            Thread(target=self.accept_thread, args=(), daemon=True).start()
        except error as e:
            print(str(e))
            return

    def accept_thread(self):
        while True: # Accept Loop
            try:
                client, client_addr = self.server.accept()
                print("Connected: %s:%s." %client_addr)
                self.new_connection(client, client_addr)
            except error as e:
                print(str(e))
                break    
    
    def stop(self):
        self.server.close()
        print("Server was closed...")
    
    def new_connection(self, fd, addr):
        client = Client(addr)
        self.connections[fd] = client
        fd.send("Welcome to server...".encode())
        # START NEW DAEMON THREAD FOR EACH CLIENT_FD
        Thread(target=self.client_ops, args=(fd,), daemon=True).start()

    def client_ops(self, fd):
        try:
            fd.send("Enter your username below to use chat_app:".encode())
            username = fd.recv(self.BUFFER_SIZE).decode()
            if(username == "FIN"): # DISCONNECTION
                reply = "Disconnected: %s:%s." %self.connections[fd].addr
                print(reply)
                self.broadcast(reply, fd)
                fd.close()
                del self.connections[fd]
                return
            else: # BROADCAST JOINED USER TO OTHERS
                self.connections[fd].login(username)
                self.broadcast("Joined.", fd)
                fd.send("Listening.. what do you want to say?".encode())
                while True: # SEND & RECIEVE MESSAGES THROUGH THE CLIENT_FD
                    try:
                        recvd_message = fd.recv(self.BUFFER_SIZE).decode()
                        if(recvd_message == "FIN"): # DELETE CLIENT_FD FROM ACTIVE CONNECTIONS WHEN IT LEAVES
                            print(f"Disconnected: %s:%s ({self.connections[fd].username})." %self.connections[fd].addr)
                            self.broadcast("Left.", fd)
                            fd.send("FIN".encode())
                            fd.close()
                            del self.connections[fd]
                            break
                        # PRINT CLIENT MESSAGE
                        print(self.connections[fd].username + " (%s:%s): " %self.connections[fd].addr + recvd_message)
                        self.broadcast(recvd_message, fd)
                    except error as e:
                        print(str(e))
                        break
        except error as e:
            print(str(e))
            return
        
    def broadcast(self, msg, user_fd=""):
        for fd in self.connections:
            if(self.connections[fd].logged_in and fd != user_fd):
                fd.send((f"{self.connections[user_fd].username} (%s:%s): {msg}" %self.connections[user_fd].addr).encode())

    def print_connections(self):
        for fd in self.connections:
            print(fd)

    def close_connections(self):
        for fd in self.connections:
            try:
                fd.send("FIN".encode())
                fd.close()
            except error as e:
                print(str(e))
                pass

# Server
server = Server()

if __name__ == "__main__":
    server.start()
    while True:
        server_input = input()
        if server_input == "exit":
            break
        print(server.print_connections())
    server.stop()