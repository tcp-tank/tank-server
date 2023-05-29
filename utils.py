import json

def encode(data):
    plain_str = json.dumps(data, default=obj_dict)
    encoded_str = plain_str.encode()
    return encoded_str

def obj_dict(obj):
    return obj.__dict__