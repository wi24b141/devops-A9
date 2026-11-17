from tasktracker.auth import check_password, hash_password, make_api_token


def test_password_roundtrip():
    h = hash_password("hunter2")
    assert check_password("hunter2", h)
    assert not check_password("wrong", h)


def test_password_hash_is_salted():
    # Same password must not give the same hash (MD5 would).
    assert hash_password("hunter2") != hash_password("hunter2")


def test_tokens_are_long_and_unique():
    tokens = {make_api_token() for _ in range(100)}
    assert len(tokens) == 100
    assert all(len(t) >= 32 for t in tokens)
