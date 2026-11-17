from tasktracker.auth import check_password, hash_password, make_api_token


def test_password_roundtrip():
    h = hash_password("hunter2")
    assert check_password("hunter2", h)
    assert not check_password("wrong", h)


def test_token_length():
    assert len(make_api_token()) == 32
