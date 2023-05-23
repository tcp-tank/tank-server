import json
from socket import AF_INET, SOCK_STREAM, socket, error
from threading import Thread
import traceback
from constants import *

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
    def listen(self):
        pass

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
        self.server.close()
        print("Server was closed...")
    
    def new_connection(self, fd, addr):
        client = Client(addr)
        self.connections[fd] = client
        fd.send(Server.encode({
            "code": SUCCESS
        }))
        Thread(target=self.client_ops, args=(fd,), daemon=True).start() # START NEW DAEMON THREAD FOR EACH CLIENT_FD

    def client_ops(self, fd):
        try:
            while True: # Wait username and password to init client
                try:
                    response = fd.recv(self.BUFFER_SIZE)
                    print(response)
                    json_data = json.loads(response)

                    command = json_data["command"]
                    # data = json_data["data"]
                    
                    if(command == QUIT): # DISCONNECTION
                        reply = "Disconnected: %s:%s." %self.connections[fd].addr
                        self.broadcast(reply, fd)
                        self.close_connection(fd)
                        return
                    else:
                        pass
                except:
                    break
        except error:
            self.close_connection(fd)
            return
        
    def broadcast(self, msg, user_fd=""):
        for fd in self.connections:
            if(self.connections[fd].logged_in and fd != user_fd):
                fd.send(Server.encode({
                    "code": SUCCESS,
                    "data": (f"{self.connections[user_fd].username} (%s:%s): {msg}" %self.connections[user_fd].addr)
                }))

    def print_connections(self):
        for fd in self.connections:
            print(fd)
            print(self.connections[fd])
            print(self.connections[fd].logged_in)

    def close_connection(self, fd):
        fd.close()
        del self.connections[fd]

    def close_connections(self):
        for fd in self.connections:
            try:
                fd.send(Server.encode({
                    "code": QUIT
                }))
                fd.close()
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




    # def client_ops(self, fd):
    #     try:
    #         fd.send("Enter your username:".encode())
    #         username = fd.recv(self.BUFFER_SIZE).decode()
    #         if(username == QUIT): # DISCONNECTION
    #             reply = "Disconnected: %s:%s." %self.connections[fd].addr
    #             print(reply)
    #             self.broadcast(reply, fd)
    #             self.close_connection(fd)
    #             return
    #         else: # BROADCAST JOINED USER TO OTHERS
    #             self.connections[fd].login(username)
    #             self.broadcast("Joined.", fd)
    #             fd.send("Listening.. what do you want to say?".encode())
    #             while True: # SEND & RECIEVE MESSAGES THROUGH THE CLIENT_FD
    #                 try:
    #                     recvd_message = fd.recv(self.BUFFER_SIZE).decode()
    #                     if(recvd_message == QUIT): # DELETE CLIENT_FD FROM ACTIVE CONNECTIONS WHEN IT LEAVES
    #                         print(f"Disconnected: %s:%s ({self.connections[fd].username})." %self.connections[fd].addr)
    #                         self.broadcast("Left.", fd)
    #                         fd.send(QUIT.encode())
    #                         self.close_connection(fd)
    #                         break
    #                     # PRINT CLIENT MESSAGE
    #                     print(self.connections[fd].username + " (%s:%s): " %self.connections[fd].addr + recvd_message)
    #                     self.broadcast(recvd_message, fd)
    #                 except error as e:
    #                     traceback.print_exc()
    #                     print(str(e))
    #                     break
    #     except error as e:
    #         self.close_connection(fd)
    #         traceback.print_exc()
    #         print(str(e))
    #         return