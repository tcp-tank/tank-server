import json

def register(username, password):
    try:
        with open("data.json", "r") as data:
            users = json.load(data)

            user_found = False
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
                    print("register successful")
                except Exception as e:
                    print(e)
            else:
                print("username already taken, try another one...")
                
    except Exception as e:
        print(e)

def obj_dict(obj):
    return obj.__dict__

register("oguzhn", "kuslar")