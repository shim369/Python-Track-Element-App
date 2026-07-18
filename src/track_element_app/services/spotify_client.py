import os
from collections.abc import AsyncGenerator
from typing import Any

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from track_element_app.utils.logger import get_logger

logger = get_logger("track_element_app.services.spotify_client")


class SpotifyClient:
    """Spotify APIとの低レイヤー通信を実行するクラス"""

    def __init__(self) -> None:
        load_dotenv()
        self.auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-library-read",
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_client(self) -> spotipy.Spotify:
        """生のspotipyクライアントインスタンスを返す"""
        return self.sp

    def fetch_user_saved_tracks(self, limit: int = 50) -> dict[str, Any]:
        """ユーザーのお気に入り曲を生データで取得"""
        return self.sp.current_user_saved_tracks(limit=limit)  # type: ignore[no-any-return]

    def fetch_audio_features(self, track_ids: list[str]) -> list[Any]:
        """複数楽曲のオーディオ特徴量を一括取得"""
        return self.sp.audio_features(track_ids)  # type: ignore[no-any-return]

    def fetch_related_artists(self, artist_id: str) -> list[dict[str, Any]]:
        """指定したアーティストの関連アーティスト情報を取得"""
        results = self.sp.artist_related_artists(artist_id)
        return results.get("artists", [])  # type: ignore[no-any-return]

    def fetch_artist_top_tracks(self, artist_id: str, country: str = "JP") -> list[dict[str, Any]]:
        """関連アーティストの楽曲を掘り下げるためのトップトラック取得"""
        results = self.sp.artist_top_tracks(artist_id, country=country)
        return results.get("tracks", [])  # type: ignore[no-any-return]

    # =====================================================================
    # ★試験対策：非同期ジェネレータと anext() のコルーチン評価ルール検証
    # =====================================================================
    async def sample_async_track_stream(self) -> AsyncGenerator[str, None]:
        """将来的な非同期一括取得を見据えたデモストリーミング"""
        tracks = ["Track_A", "Track_B", "Track_C"]
        for track in tracks:
            yield track

    async def simulate_anext_trap(self) -> None:
        """anext()がコルーチンを返すだけで await が必須であることを検証する"""
        gen = self.sample_async_track_stream()

        # ❌ 罠：await をつけないと、値ではなく単なる「コルーチンオブジェクト」が返る
        co = anext(gen)
        logger.debug("Trap (anext without await): Successfully verified coroutine object type: %s", type(co))

        # ⭕️ 正解：await を付与して初めて非同期ジェネレータから値が評価・抽出される
        first_value = await co
        logger.debug("Trap (anext with await): Safely evaluated first value: %s", first_value)
