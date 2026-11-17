import secrets

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    # Salted, slow key-derivation hash (scrypt) instead of a single fast MD5 round.
    return generate_password_hash(password)


def check_password(password, password_hash):
    return check_password_hash(password_hash, password)


def make_api_token(nbytes=32):
    # secrets uses the OS CSPRNG, unlike the predictable `random` module.
    return secrets.token_urlsafe(nbytes)
