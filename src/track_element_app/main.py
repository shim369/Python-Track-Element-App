import asyncio
import os
from collections.abc import AsyncGenerator

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from track_element_app.models.track import TrackData
from track_element_app.utils.decorators import measure_time
from track_element_app.utils.logger import get_logger, setup_logger

# ロガーの初期化
setup_logger()
logger = get_logger("track_element_app.main")


# =====================================================================
# ★試験・実務対策：非同期ジェネレータの罠シミュレーション
# =====================================================================
async def dummy_track_id_generator() -> AsyncGenerator[str, None]:
    """将来的な非同期API一括取得を見据えた、IDを1つずつ返す非同期ジェネレータ"""
    yield "track_id_1"
    yield "track_id_2"


async def simulate_async_generator_trap() -> None:
    """anext()単体では値が評価されない仕様を検証する関数"""
    gen = dummy_track_id_generator()

    # 罠：anext(gen) だけを呼び出しても、返ってくるのはコルーチンオブジェクト自体
    raw_coroutine = anext(gen)
    logger.debug("--- [Trap Verification] ---")
    logger.debug("Just anext(gen): %s", raw_coroutine)
    # 出力: <coroutine object ...> となり、中のデータ ("track_id_1") はまだ評価されていない！

    # 正解：await を添えることで、初めて非同期処理が実行されて値が取り出せる
    real_value = await raw_coroutine
    logger.debug("With await anext(gen): %s", real_value)  # 出力: track_id_1
    logger.debug("---------------------------")


# =====================================================================
# 本番ロジック：Spotifyからのデータ取得
# =====================================================================
def get_spotify_client() -> spotipy.Spotify:
    """環境変数から認証情報を読み込み、Spotifyクライアントを生成する"""
    load_dotenv()

    # ユーザーのお気に入り曲（Scope: user-library-read）を読み取る権限を指定
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read",
    )
    return spotipy.Spotify(auth_manager=auth_manager)


@measure_time
def fetch_favorite_tracks_features(sp: spotipy.Spotify) -> list[TrackData]:
    """直近のお気に入り曲50曲とそのオーディオ特徴量を取得する"""
    logger.info("Spotifyからお気に入り曲（直近50曲）を取得中...")

    # 1. お気に入り曲の基本情報を取得（最大50曲）
    results = sp.current_user_saved_tracks(limit=50)
    items = results.get("items", [])

    if not items:
        logger.warning("お気に入り曲が見つかりませんでした。")
        return []

    track_ids = [item["track"]["id"] for item in items]

    # 2. オーディオ特徴量（Danceability, Energy, Valence等）を一括取得
    features_list = sp.audio_features(track_ids)

    # 3. 基本情報と特徴量をガチャンと結合して TrackData データクラスに格納
    track_data_objects: list[TrackData] = []

    for item, features in zip(items, features_list, strict=True):
        if features is None:
            continue  # 特徴量が取得できない特殊な曲はスキップ

        track = item["track"]

        # 前回作成したバリデーション機能付きデータクラス（TrackData）にマッピング
        track_data = TrackData(
            track_id=track["id"],
            title=track["name"],
            artist=track["artists"][0]["name"],
            danceability=features["danceability"],
            energy=features["energy"],
            valence=features["valence"],
            release_date=track["album"]["release_date"],
        )
        track_data_objects.append(track_data)

    return track_data_objects


async def async_main() -> None:
    # 1. まずは非同期ジェネレータの仕様検証を実行
    await simulate_async_generator_trap()

    # 2. 本番のSpotifyデータ取得を実行
    try:
        sp = get_spotify_client()
        tracks = fetch_favorite_tracks_features(sp)

        print("\n=== 🎵 あなたの直近お気に入り曲のオーディオ特徴量 (Top 50) ===")
        print(f"{'Title':<30} | {'Artist':<20} | {'Dance':<6} | {'Energy':<6} | {'Valence':<6}")
        print("-" * 80)

        for t in tracks:
            # ターミナルで見やすくフォーマットして表示
            print(f"{t.title[:28]:<30} | {t.artist[:18]:<20} | {t.danceability:.2f}  | {t.energy:.2f}  | {t.valence:.2f}")

    except Exception as e:
        logger.error("データの取得中にエラーが発生しました: %s", e)


def main() -> None:
    """アプリケーションのエントリーポイント"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
