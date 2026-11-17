import hashlib
import random
import string


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def check_password(password, password_hash):
    return hash_password(password) == password_hash


def make_api_token(length=32):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
