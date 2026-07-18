import os

import pytest


@pytest.fixture(autouse=True)
def set_spotify_env():
    os.environ["SPOTIPY_CLIENT_ID"] = "mock_id"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "mock_secret"
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8080"
