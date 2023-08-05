import os

import pytest

from tcgplayer.service import TCGPlayer
from tcgplayer.sqlite_cache import SQLiteCache
from tcgplayer.exceptions import ServiceError


@pytest.fixture(scope="session")
def client_id():
    return os.getenv("TCG_PLAYER_CLIENT_ID", default="Invalid")


@pytest.fixture(scope="session")
def client_secret():
    return os.getenv("TCG_PLAYER_CLIENT_SECRET", default="Invalid")


@pytest.fixture(scope="session")
def access_token():
    return os.getenv("TCG_PLAYER_ACCESS_TOKEN", default="Invalid")


@pytest.fixture(scope="session")
def session(client_id, client_secret, access_token) -> TCGPlayer:
    session = TCGPlayer(
        client_id, client_secret, access_token, cache=SQLiteCache("tests/cache.sqlite", expiry=None)
    )
    try:
        if not session.authorization_check():
            session.generate_token()
    except ServiceError:
        pass
    return session
