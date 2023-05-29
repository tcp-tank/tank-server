import json

def login(username, password):

    try:
        with open("data.json", "r") as data:

            users = json.load(data)

            user_found = False
            code = 400
            reply = ""
            user = {}
            for user in users:
                if user["username"] == username:
                    user_found = True
                    if user["password"] == password:
                        reply = "Login successful."
                        code = 200
                        user = {
                            "username": username,
                            "score": user["score"]
                        }
                    else:
                        reply = "Wrong password."
                    break
            
            if not user_found:
                reply = "User not found."

            return {
                "code": code,
                "user_found": user_found,
                "message": reply,
                "user": user
            }
                
    except Exception as e:
        print(e)
        return {
            "code": 400,
            "user_found": False,
            "message": "DB connection failure"
        }

# login("oguzhn", "kuslar")

def register(username, password):
    try:
        with open("data.json", "r") as data:
            users = json.load(data)

            user_found = False
            is_created = False
            reply = ""
            code = 400
            for user in users:
                if user["username"] == username:
                    user_found = True
                    break

            if not user_found:
                # create new user
                new_user = {
                    "username": username,
                    "password": password,
                    "score": 0
                }
                users.append(new_user)
                try:
                    with open("data.json", "w") as db:
                        json_text = json.dumps(users, default=obj_dict)
                        db.write(json_text)
                    is_created = True
                    reply = "register successful"
                    code = 200
                except Exception as e:
                    print(e)
                    return {
                        "code": 400,
                        "is_created": False,
                        "message": "db connection failure"
                    }
            else:
                reply = "username already taken, try another one..."

            return {
                "code": code,
                "is_created": is_created,
                "message": reply
            }
                
    except Exception as e:
        print(e)
        return {
            "code": 400,
            "is_created": False,
            "message": "db connection failure"
        }

def obj_dict(obj):
    return obj.__dict__

# print(register("oguzhn", "kuslar"))