from collections.abc import AsyncGenerator
import logging
import os
from typing import Any

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
        cache_handler = CacheFileHandler(cache_path=".cache")
        self.auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-library-read playlist-modify-public user-read-recently-played",
            cache_handler=cache_handler,
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def create_playlist_and_add_tracks(self, playlist_name: str, track_ids: list[str]) -> dict[str, Any]:
        """
        ユーザーのアカウントに新規プレイリストを作成し、指定された楽曲群を保存する。
        """
        # 擬似エラー判定と「遅延フォーマット評価」の実装
        if playlist_name == "error_token":
            err_code = 401
            # ⭕️ 遅延フォーマット評価（%s を使い、カンマで引数を渡す）
            logger.error("Spotify authentication failed. Status code: %s", err_code)
            raise SpotifyTokenExpiredError("アクセストークンの有効期限が切れています。再認可が必要です。")

        if playlist_name == "error_api":
            err_msg = "Rate limit exceeded"
            logger.warning("Spotify API dynamic warning triggered. Reason: %s", err_msg)
            raise SpotifyAPIError("Spotify APIの呼び出し制限に達しました。時間をおいて試してください。")

        # 正常系のログ（ここでも文字列結合を避け、%s で遅延評価）
        logger.info("Successfully created playlist: %s with %s tracks", playlist_name, len(track_ids))

        # 既存のダミーレスポンス
        return {
            "success": True,
            "playlist_id": "mock_playlist_37i9dQZF1DXcBWIGor7RQa",
            "name": playlist_name,
            "total_tracks": len(track_ids),
        }

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
