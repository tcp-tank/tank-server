from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

HOST = "127.0.0.1"
PORT = 4567
BUF_SIZE = 1024
ADDR = (HOST, PORT)

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)

clients = {}

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


def server_start():
    while True:
        try:
            client, client_addr = server.accept()
            print("Connected: %s:%s." %client_addr)

            c = Client(client_addr)
            clients[client] = c

            client.send("Welcome to server...".encode())
            Thread(target=connected_client_ops, args=(client,), daemon=True).start()
        except:
            break


def connected_client_ops(client):
    try:
        client.send("Enter your username below to use chat_app:".encode())
        username = client.recv(BUF_SIZE).decode()

        if(username == "FIN"):
            disc_msg = "Disconnected: %s:%s." %clients[client].addr
            print(disc_msg)
            broadcast(disc_msg, client)
            client.close()
            del clients[client]
            return
        else:
            clients[client].login(username)
            broadcast("Joined.", client)

            client.send("Listening.. what do you want to say?".encode())
            while True:
                try:
                    recvd_message = client.recv(BUF_SIZE).decode()
                    if(recvd_message == "FIN"):
                        print(f"Disconnected: %s:%s ({clients[client].username})." %clients[client].addr)
                        broadcast("Left.", client)
                        client.send("FIN".encode())
                        client.close()
                        del clients[client]
                        break
                    print(clients[client].username + " (%s:%s): " %clients[client].addr + recvd_message)
                    broadcast(recvd_message, client)
                except:
                    break
    except:
        pass


def close_active_client_sockets():
    for client in clients:
        try:
            client.send("FIN".encode())
            client.close()
        except:
            pass


def broadcast(msg, user=""):
    for client in clients:
        if(clients[client].logged_in and client != user):
            client.send((f"{clients[user].username} (%s:%s): {msg}" %clients[user].addr).encode())


if __name__ == "__main__":
    server.listen()
    print("Server is running on port:", PORT)

    Thread(target=server_start, args=(), daemon=True).start()

    while True:
        server_input = input()
        if server_input == "exit":
            break

    print("Server was closed...")
    server.close()