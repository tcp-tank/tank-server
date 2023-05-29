from socket import AF_INET, SOCK_STREAM, socket
from threading import Condition, Thread, Event
import json, traceback, time, random
from typing import List
from dbase import login

from utils import encode

HOST = "" 
PORT = 7777

class Server:
    def __init__(self, HOST: str, PORT: int):
        self.HOST           = HOST
        self.PORT           = PORT
        self.ADDR           = (HOST, PORT)
        self.BUFFER_SIZE    = 2048
        self.socket         = socket(AF_INET, SOCK_STREAM)

        self.connections    = {}
        self.users          = []
        self.rooms          = [
            {
                "room_name": "room#1",
                "players": [],
                "settings": {},
                "ids": [0, 1, 2, 3],
                "fds": []
            },
            {
                "room_name": "room#2",
                "players": [],
                "settings": {},
                "ids": [0, 1, 2, 3],
                "fds": []
            },
            {
                "room_name": "room#3",
                "players": [],
                "settings": {},
                "ids": [0, 1, 2, 3],
                "fds": []
            },
            {
                "room_name": "room#4",
                "players": [],
                "settings": {},
                "ids": [0, 1, 2, 3],
                "fds": []
            }
        ]

    def start(self):
        self.socket.bind(self.ADDR)
        self.socket.listen()
        print("Server is running on port:", self.PORT)
        Thread(target=self.accept_thread).start()

    def close(self):
        self.broadcast("DOWN", {"message": "Server closed."})
        self.socket.close()

    def accept_thread(self):
        while True:
            try:
                client, client_addr = self.socket.accept()
                print(f"%s:%s Connected." %client_addr)

                self.connections[client] = client_addr

                ####### SEND SERVER DATA TO CLIENT FIRST #######
                self.organized_rooms = []
                self.organized_users = []
                for room in self.rooms:
                    self.organized_rooms.append({
                        "room_name": room["room_name"],
                        "players": room["players"],
                        "settings": room["settings"],
                    })
                for user in self.users:
                    self.organized_users.append({
                        "username": user["username"],
                        "score": user["score"]
                    })
                reply = {
                    "command": "INIT",
                    "data": {
                        "users": self.organized_users,
                        "rooms": self.organized_rooms,
                    }
                }
                self.send(client, reply)
                ################################################

                Thread(target=self.client_thread, args=(client, client_addr)).start()
            except:
                break
    
    def client_thread(self, fd: socket, addr):
        while True:
            try:
                reply = fd.recv(self.BUFFER_SIZE)
                reply_organized = self.organize_string_data(reply.decode())
                if reply_organized:
                    try:
                        rp = json.loads(reply_organized)
                        command = rp["command"]
                        print(f"[RECIEVED] %s:%s " %addr + command + " - " + reply.decode())

                        # LOGN - Login
                        if command == "LOGN":
                            self.handle_login(fd, rp["data"])
                        # LOGT - Logout
                        elif command == "LOGT":
                            self.handle_logout(rp["data"]["username"])
                        # CRTR - Create Room
                        elif command == "CRTR":
                            self.handle_crtr(fd, rp["data"])
                        # ENTR - Enter Room
                        elif command == "ENTR":
                            self.handle_entr(fd, rp["data"])
                        # LVER - Leave Room
                        elif command == "LVER":
                            self.handle_lver(fd, rp["data"])
                        # SRTG - Start Game
                        elif command == "SRTG":
                            self.handle_srtg(rp["data"])
                        # EXIT -
                        elif command == "EXIT": # Connection closed by client
                            self.handle_exit(fd, rp["data"])
                            break
                        # MOVE - {'command': 'MOVE', 'data': {'player_id': 1, 'direction': 'bottom', 'pos': '1:121,111'}}
                        elif command == "MOVE":
                            self.broadcast(command, rp["data"])
                        # SHOT - {'command': 'SHOT', 'data': {'player_id': 2}}
                        elif command == "SHOT":
                            self.broadcast(command, rp["data"])
                        # MESG -
                        elif command == "MESG":
                            self.broadcast(command, rp["data"])
                    except:
                        print("HEEYYY DATA:")
                        print(reply)
                        traceback.print_exc()
                        pass
            except Exception:
                username = None
                for i, user in enumerate(self.users):
                    if user["fd"] == fd:
                        username = user["username"]
                        self.users.remove(self.users[i])
                        break
                
                if username:
                    for room in self.rooms:
                        for player in room["players"]:
                            if player["user"]["username"] == username:
                                reply = {
                                    "room_name": room["room_name"],
                                    "player_id": player["player_id"]
                                }
                                self.handle_lver(fd, reply)
                
                traceback.print_exc()
                fd.close()
                del self.connections[fd]
                break
    
    def broadcast(self, command: str, data = {}):
        reply = {
            "command": command
        }
        if data: reply["data"] = data
        for client in self.connections:
            self.send(client, reply)

    def room_broadcast(self, command: str, room_name: str, data = {}):
        reply = {
            "command": command
        }
        if data: reply["data"] = data
        room_index = self.get_room_index(room_name)
        for fd in self.rooms[room_index]["fds"]:
            self.send(fd, reply)

    def send(self, fd: socket, data):
        fd.send(encode(data))
        print(f"[SENDED] %s:%s " %self.connections[fd] + "- " + data["command"] + " - ", data)
    
    def handle_login(self, fd, data):
        code    = 400
        message = "Username and password required."
        user    = data

        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]

            user_index = self.get_user_index(username)
            if user_index != -1:
                message = "Already logged in."
            else:
                ### Check username <-> password match from DB
                res = login(username, password)
                if res["code"] == 200: # Login success.
                    code    = 200
                    message = res["message"]
                    user    = res["user"]

                    self.users.append({
                        "username": res["user"]["username"], 
                        "score": res["user"]["score"],
                        "fd": fd
                    })
                    self.broadcast("ENTL", {
                        "user": res["user"],
                        "message": "Joined."
                    })

                message = res["message"]

        self.send(fd, {
            "command": "LOGN",
            "data": {
                "code": code,
                "message": message,
                "user": user
            }
        })

    def handle_logout(self, username):
        user_index = self.get_user_index(username)
        if user_index != -1:
            self.users.remove(self.users[user_index])
            self.broadcast("LVEL", {
                "username": username,
                "message": "Left."
            })

    def get_user_index(self, username):
        user_index = -1
        for i, user in enumerate(self.users):
            if user["username"] == username:
                user_index = i
                break
        return user_index
    
    def handle_crtr(self, fd, data):
        """
        {
            "command": "CRTR",
            "data": {
                "room_name": room_name,
                "settings": {}
            }
        }
        """
        room_name = data["room_name"]
        if room_name:
            room_index = self.get_room_index(room_name)
            if room_index != -1:
                self.send(fd, {
                    "command": "CRTR",
                    "data": {
                        "code": 400,
                        "room_name": room_name,
                        "message": "Room name already exists."
                    }
                })
            else:
                self.rooms.append(data)
                self.broadcast("CRTR", {
                    "code": 200,
                    "room": data
                })

    def handle_entr(self, fd, data):
        # Notify players new player has joined the room
        """
        {
            "command": "ENTR",
            "data": {
                "room_name": room_name,
                "player": {
                    "user": self.user,
                    "player_id": self.player_id,
                    "direction": self.tank.direction,
                    "pos": str(self.player_id) + ":" + str(self.tank.rect.centerx) + "," + str(self.tank.rect.centery)
                }
            }
        }
        """
        player = data["player"]
        room_name  = data["room_name"] 
        room_index = self.get_room_index(room_name)

        reply = {
            "code": 400,
            "message": "Room not found.",
            "room_name": room_name,
            "player": player,
            "players": self.rooms[room_index]["players"]
        }

        if room_index != -1:
            if len(self.rooms[room_index]["players"]) < 4:
                random_id = self.get_id(self.rooms[room_index]["ids"])
                player = {
                    "user": player["user"],
                    "player_id": random_id,
                    "direction": player["direction"],
                    "pos": str(random_id) + ":" + player["pos"].split(":")[1]
                }
                reply["player"] = player
                self.rooms[room_index]["players"].append(player)
                self.rooms[room_index]["fds"].append(fd)
                try:
                    reply["code"] = 200
                    reply["message"] = "Enter room success."
                    self.room_broadcast("ENTR", room_name, reply)
                except:
                    self.add_id(self.rooms[room_index]["ids"], random_id)
                    self.rooms[room_index]["players"].remove(player)
                    self.rooms[room_index]["fds"].remove(fd)
            else: # Room full
                reply["message"] = "Room full."
        
        if reply["code"] == 400:
            self.send(fd, {
                "command": "ENTR",
                "data": reply
            })
            
    def handle_lver(self, fd, data):
        # Delete player from players
        """
        {
            "command": "LVER",
            "data": {
                "room_name": "xxx",
                "player_id": 3
            }
        }
        """
        room_name  = data["room_name"] 
        player_id  = data["player_id"]
        room_index = self.get_room_index(room_name)

        player = None

        # Delete player
        for i, p in enumerate(self.rooms[room_index]["players"]):
            if p["player_id"] == player_id:
                player = self.rooms[room_index]["players"][i]
                self.rooms[room_index]["players"].remove(self.rooms[room_index]["players"][i])
                break
        
        # Delete socket from fds
        self.rooms[room_index]["fds"].remove(fd)

        data = {
            "player": player
        }
        self.add_id(self.rooms[room_index]["ids"], player_id)
        self.room_broadcast("LVER", room_name, data)

    def handle_srtg(self, data):
        # Start game
        """
        {
            "command": "SRTG",
            "data": {
                "room_name": "xxx"
            }
        }
        """
        room_name  = data["room_name"] 
        data = {
            "code": 200
        }
        self.room_broadcast("SRTG", room_name, data)

    def handle_exit(self, fd, data):
        username = data["username"]
        if username:
            self.handle_logout(data["username"])

        self.send(fd, {
            "command": "EXIT",
            "data": {
                "message": "Bye."
            }
        })
        del self.connections[fd]
        fd.close()
    
    def get_room_index(self, room_name):
        room_index = -1
        for i, room in enumerate(self.rooms):
            if room["room_name"] == room_name:
                room_index = i
                break
        return room_index
    
    def get_id(self, arr: List[int]):
        rand_num = random.randrange(0, len(arr))
        rand_id = arr[rand_num]
        arr.pop(rand_num)
        return rand_id
    
    def add_id(self, arr: List[int], id: int):
        arr.append(id)

    def organize_string_data(self, data: str):
        if data.find("}{") != -1:
            i = data.find("}{")
            t = data.replace("}{", "}")
            return t[:i+1]
        return data

    def print_connections(self):
        for con in self.connections:
            print(con)

    def print_data(self):
        while not ev.is_set():
            print("ROOMS:", self.rooms)
            # print("USERS:", self.users)
            time.sleep(2)

ev = Event()
cv = Condition()

if __name__ == "__main__":
    try:
        server = Server(HOST, PORT)
        Thread(target=server.start, daemon=True).start()

        print_thread = Thread(target=server.print_data, daemon=True)

        while True:
            cmd_in = input()
            if cmd_in == "exit":
                break
            elif cmd_in == "stop":
                ev.set()
                pass
            elif cmd_in == "print":
                ev.clear()
                print_thread.start()
                pass
            server.print_connections()

        server.close()
    except Exception:
        traceback.print_exc()
