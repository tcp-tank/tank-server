import json

def login(username, password):
    try:
        with open("data.json", "r") as data:
            users = json.load(data)

            user_found = False
            for user in users:
                if user["username"] == username:
                    user_found = True
                    if user["password"] == password:
                        print("login successfull")
                    else:
                        print("wrong password")
                    break

            # user not found
            if not user_found:
                print("user not found")
                
    except Exception as e:
        print(e)

login("oguzhn", "kuslar")