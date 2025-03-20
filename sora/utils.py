import base64
import random
import string


def get_from_to(data, f, t, offset):
    from_index = data.find(f)
    to_index = data.find(t)
    return data[from_index : to_index + offset]


def get_random_name():
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


def base64_decode(s):
    return base64.b64decode(s).decode()
