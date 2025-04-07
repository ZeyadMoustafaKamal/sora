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


class Proxy:
    # In the backtrace, the `soup` object outputs a verbose content so we will wrap it here so
    # it doesn't cause problems. But we can you this for more stuff as well.
    def __init__(self, obj) -> None:
        self._obj = obj

    def __getattribute__(self, name: str):
        obj = super().__getattribute__("_obj")
        return getattr(obj, name)
