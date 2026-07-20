import logging
import os
from typing import Any, cast

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth

# ロガーの取得
logger = logging.getLogger("track_element_app.services.spotify_client")


class SpotifyAPIError(Exception):
    """Spotify API通信に関するカスタム例外クラス。"""

    pass


class SpotifyTokenExpiredError(SpotifyAPIError):
    """トークン切れ（401 Unauthorized）を表現する例外クラス。"""

    pass


class SpotifyClient:
    """Spotify APIとの低レイヤー通信を実行するクラス"""

    def __init__(self) -> None:
        load_dotenv()
        # キャッシュハンドラーの作成
        self.cache_handler = CacheFileHandler(cache_path=".cache")
        self.auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-library-read user-read-recently-played user-top-read playlist-modify-public playlist-modify-private",
            cache_handler=self.cache_handler,
            show_dialog=True,
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

        token_info = self.cache_handler.get_cached_token()
        if token_info:
            self.auth_manager.validate_token(token_info)

    def create_playlist_and_add_tracks(self, name: str, track_ids: list[str]) -> dict[str, Any]:
        try:
            # 1. プレイリスト作成
            playlist = self.sp.current_user_playlist_create(
                name=name,
                public=False,
            )
            print(f"DEBUG: プレイリスト '{name}' を作成しました！")

            # 2. トラック追加
            if track_ids:
                track_uris = [f"spotify:track:{tid}" for tid in track_ids]
                self.sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)

            return cast(dict[str, Any], playlist)
        except Exception as e:
            logger.error("プレイリスト作成エラー: %s", e)
            raise SpotifyAPIError(f"Playlist Creation Error: {e}") from e

    def get_client(self) -> spotipy.Spotify:
        return self.sp

    def fetch_user_saved_tracks(self, limit: int = 50) -> dict[str, Any]:
        return cast(dict[str, Any], self.sp.current_user_saved_tracks(limit=limit))

    def fetch_audio_features(self, track_ids: list[str]) -> list[Any]:
        return cast(list[Any], self.sp.audio_features(track_ids))

    def fetch_related_artists(self, artist_id: str) -> list[dict[str, Any]]:
        results = self.sp.artist_related_artists(artist_id)
        return cast(list[dict[str, Any]], results.get("artists", []))

    def fetch_artist_top_tracks(self, artist_id: str, country: str = "JP") -> list[dict[str, Any]]:
        results = self.sp.artist_top_tracks(artist_id, country=country)
        return cast(list[dict[str, Any]], results.get("tracks", []))

    def fetch_recently_played_tracks(self, limit: int = 50) -> dict[str, Any]:
        return cast(dict[str, Any], self.sp.current_user_recently_played(limit=limit))

    def fetch_user_top_tracks(self, limit: int = 10, time_range: str = "short_term") -> dict[str, Any]:
        try:
            return cast(dict[str, Any], self.sp.current_user_top_tracks(time_range=time_range, limit=limit))
        except Exception as e:
            logger.error("トップ楽曲取得エラー: %s", e)
            raise SpotifyAPIError(f"Top Tracks Fetch Error: {e}") from e
