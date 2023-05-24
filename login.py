import json

from constants import *

def login(username, password):
    try:
        with open("data.json", "r") as data:
            users = json.load(data)
            user_found = False
            reply = ""
            code = FAILURE
            for user in users:
                if user["username"] == username:
                    user_found = True
                    if user["password"] == password:
                        reply = "login successfull"
                        code = SUCCESS
                    else:
                        reply = "wrong password"
                    break
            # user not found
            if not user_found:
                reply = "user not found"
            return {
                "code": code,
                "user_found": user_found,
                "message": reply
            }
                
    except Exception as e:
        print(e)
        return {
            "code": FAILURE,
            "user_found": False,
            "message": "db connection failure"
        }

# login("oguzhn", "kuslar")