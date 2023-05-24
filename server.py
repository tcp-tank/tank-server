import json
from socket import AF_INET, SOCK_STREAM, socket, error
from threading import Thread
import traceback
from constants import *
from login import login
from register import register

class Client:
    def __init__(self, addr):
        self.addr = addr
        self.username = ""
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
            traceback.print_exc()
            print(str(e))
            return

    def accept_thread(self):
        while True: # Accept Loop
            try:
                client, client_addr = self.server.accept()
                print("Connected: %s:%s." %client_addr)
                self.new_connection(client, client_addr)
            except error as e:
                traceback.print_exc()
                print(str(e))
                break    
    
    def stop(self):
        self.close_connections()
        self.server.close()
        print("Server was closed...")
    
    def new_connection(self, fd, addr):
        client = Client(addr)
        self.connections[fd] = client
        self.send(fd, SUCCESS, STRT, message="Connection success.")
        Thread(target=self.client_ops, args=(fd,), daemon=True).start() # START NEW DAEMON THREAD FOR EACH CLIENT_FD

    def client_ops(self, fd):
        while True: # Client command loop
            try:
                recvd_bytes = fd.recv(self.BUFFER_SIZE)
                recvd_json = json.loads(recvd_bytes)
                print(str(f"Recieved from (%s:%s):" %self.connections[fd].addr) + recvd_bytes.decode())

                if "command" in recvd_json and "data" in recvd_json:
                    command = recvd_json["command"]
                    data    = recvd_json["data"]
                    if command == QUIT: # DISCONNECTION
                        print("Disconnected: %s:%s." %self.connections[fd].addr)
                        self.close_connection(fd)
                        return
                    elif command == LOG: # USER LOGIN
                        self.login(fd, data)
                    elif command == REG: # USER REGISTER
                        self.register(fd, data)
                    elif command == BRDC: # BROADCAST
                        b_type = data["b_type"]
                        if b_type == LEFT:   # REMOVE PLAYER FROM PLAYER LIST
                            self.connections[fd].logged_in = False
                            self.connections[fd].username = ""
                            self.send(fd, SUCCESS, QUIT)
                            self.broadcast(fd, LEFT, {
                                "username": self.connections[fd].username,
                                "addr": fd.getpeername()
                            })
                        if b_type == MOVE:
                            pass
                        pass
                    else: # Given invalid command
                        self.send(fd, FAILURE, message="invalid command.")
                else: # Given no command
                    self.send(fd, FAILURE, message="command and data props are missing")
            except error as e: # Connection lost or any kind of error with recv regarding to active socket
                traceback.print_exc()
                self.close_connection(fd)
                break
        
    def broadcast(self, from_fd, b_type, data):
        for fd in self.connections:
            if(self.connections[fd].logged_in and fd != from_fd):
                self.send(fd, SUCCESS, BRDC, data, b_type)
    
    def send(self, fd, code, command="", data={}, message=""):
        response = Server.encode({
            "code": code,
            "command": command,
            "data": data,
            "message": message
        })
        try:
            fd.send(response)
            print(str(f"Sended to (%s:%s): " %self.connections[fd].addr) + response.decode())
        except error:
            traceback.print_exc()
            print(str(f"Couldn't send to (%s:%s): " %self.connections[fd].addr) + response.decode())

    def print_connections(self):
        for fd in self.connections:
            print(fd)
            print(self.connections[fd])
            print(self.connections[fd].logged_in)

    def login(self, fd, data):
        if "username" in data and "password" in data:
            is_logged_in = self.is_logged_in(data["username"])

            if is_logged_in:
                self.send(fd, FAILURE, LOG, data, "already logged in.")
            else:
                response = login(data["username"], data["password"])
                if response["user_found"]:
                    self.send(fd, response["code"], LOG, data, response["message"])
                    if(response["code"] == SUCCESS):
                        self.connections[fd].username = data["username"]
                        self.connections[fd].logged_in = True
                        self.broadcast(fd, JOINED, {
                            "username": data["username"],
                            "addr": fd.getpeername()
                        })
                else:
                    self.send(fd, response["code"], LOG, data, response["message"])

        else:
            self.send(fd, response["code"], LOG, data, "username and password props are missing.")

    def is_logged_in(self, username):
        logged_in = False
        for con in self.connections.values():
            if con.username == username:
                logged_in = True
                break
        return logged_in

    def register(self, fd, data):
        if "username" in data and "password" in data:
            response = register(data["username"], data["password"])
            if response["is_created"]:
                self.send(fd, response["code"], REG, data, response["message"])
            else:
                self.send(fd, response["code"], REG, data, response["message"])
        else:
            self.send(fd, response["code"], REG, data, "username and password props are missing.")

    def close_connection(self, fd):
        fd.close()
        del self.connections[fd]

    def close_connections(self):
        for fd in self.connections:
            reply = "Server closed."
            try:
                self.send(fd, CRASH, QUIT, message=reply)
                fd.close()
                print(str(f"Sended to (%s:%s): " %self.connections[fd].addr) + reply)
            except: # Socket closed already
                pass

    @staticmethod
    def encode(data):
        plain_str = json.dumps(data, default=Server.obj_dict)
        encoded_str = plain_str.encode()
        return encoded_str
    @staticmethod
    def obj_dict(obj):
        return obj.__dict__

# Server
server = Server()

if __name__ == "__main__":
    server.start()
    while True:
        server_input = input()
        if server_input == "exit":
            break
        server.print_connections()
    server.stop()