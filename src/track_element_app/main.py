import asyncio
import os
from collections.abc import Generator

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from track_element_app.models.track import TrackData
from track_element_app.utils.logger import get_logger, setup_logger

# ロガーの初期化
setup_logger()
logger = get_logger("track_element_app.main")


# =====================================================================
# ジェネレータ・メモリ・アンパックの罠シミュレーション
# =====================================================================
def huge_track_generator(limit: int = 10000) -> Generator[str, None, None]:
    """数万件の楽曲IDを想定したジェネレータ（MemoryErrorを防ぐストリーミング用）"""
    for i in range(limit):
        yield f"track_id_heavy_{i}"


def simulate_advanced_python_traps() -> None:
    """ジェネレータ制限、メモリ節約、アンパック代入の挙動を検証する"""
    logger.debug("--- [Advanced Python Traps Verification] ---")

    # 1. ジェネレータと len() の TypeError 罠
    gen = huge_track_generator(5)
    try:
        # ジェネレータオブジェクトに len() は使えない
        _ = len(gen)  # type: ignore[arg-type]
    except TypeError as e:
        logger.debug("Trap 1 (Generator len): Successfully caught expected TypeError: %s", e)
        # 対策：要素数を測るにはリスト化するかループで数える必要がある（ただしメモリに注意）

    # 2. 巨大データと list() 化による MemoryError リスク
    # 安易に list(gen) すると、すべてのデータがメモリに一挙展開され、数百万件規模だとクラッシュする
    # 対策：Pandas や Chunk 処理などを通して、イテレータ（1個ずつ取り出す）のまま小分けにして処理する
    # 今回はシミュレータなので、最初の3件だけ安全に取り出して評価する例
    limited_items = [next(gen) for _ in range(3)]
    logger.debug("Trap 2 (Memory Saver): Safely extracted partial items: %s", limited_items)

    # 3. アスタリスクを使った残余引数アンパックの文法制限
    # 1つの代入文に * (残余アスタリスク) は1つしか使えない
    # 例： `first, *middle, *last = [1, 2, 3, 4]` ➔ SyntaxError: multiple starred expressions
    # 例：要素数が合わない（アスタリスクがないのに数がズレている）と ValueError になる
    try:
        sample_list = ["Intro_Track", "BGM_1", "BGM_2", "Outro_Track"]
        # 1つの代入文にアスタリスクは1つだけ。残余すべてをリストとして受け取る
        first_song, *middle_songs, last_song = sample_list
        logger.debug("Trap 3 (Unpacking): First: %s", first_song)
        logger.debug("Trap 3 (Unpacking): Middle (Starred list): %s", middle_songs)
        logger.debug("Trap 3 (Unpacking): Last: %s", last_song)

        # ValueError を引き起こすアンパック（アスタリスクなしで要素数がズレた場合）
        _song1, _song2 = sample_list  # 4要素あるのに2変数で受け取ろうとする
    except ValueError as e:
        logger.debug("Trap 3 (ValueError Case): Successfully caught ValueError: %s", e)

    logger.debug("--------------------------------------------")


# =====================================================================
# Spotify 認証 & 取得ロジック
# =====================================================================
def get_spotify_client() -> spotipy.Spotify:
    """環境変数から認証情報を読み込み、Spotifyクライアントを生成する"""
    load_dotenv()
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read",
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def fetch_favorite_tracks_features(sp: spotipy.Spotify) -> list[TrackData]:
    """直近のお気に入り曲50曲とそのオーディオ特徴量を取得する"""
    logger.info("Spotifyからお気に入り曲（直近50曲）を取得中...")
    results = sp.current_user_saved_tracks(limit=50)
    items = results.get("items", [])

    if not items:
        logger.warning("お気に入り曲が見つかりませんでした。")
        return []

    track_ids = [item["track"]["id"] for item in items]
    features_list = sp.audio_features(track_ids)

    track_data_objects: list[TrackData] = []

    for item, features in zip(items, features_list, strict=True):
        if features is None:
            continue

        track = item["track"]
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


# =====================================================================
# DJロジック（フェードイン・選曲アルゴリズム）
# =====================================================================
def create_fade_in_playlist(tracks: list[TrackData]) -> pd.DataFrame:
    """Pandas を導入し、Energy がなだらかに右肩上がりになるようにソートした DataFrame を返す"""

    # 1. TrackData のリストを Pandas の DataFrame に変換
    # dataclass オブジェクトのリストは、そのまま dataclasses.asdict() するか、
    # __dict__ 経由、または単に dict リスト化することで簡単に DataFrame に流し込めます。
    raw_data = [
        {
            "title": t.title,
            "artist": t.artist,
            "danceability": t.danceability,
            "energy": t.energy,
            "valence": t.valence,
            "release_date": t.release_date,
        }
        for t in tracks
    ]
    df = pd.DataFrame(raw_data)

    if df.empty:
        return df

    # 2. DJロジック：Energy で昇順ソート（なだらかな右肩上がりにする）
    # 同一 Energy の場合は、曲の明るさ（Valence）が高い方を後半に持ってきて、よりポジティブな流れを作る
    sorted_df = df.sort_values(by=["energy", "valence"], ascending=[True, True]).reset_index(drop=True)

    return sorted_df


async def async_main() -> None:
    # 1. ジェネレータ、メモリ、アンパック代入に関する試験対策シミュレーション
    simulate_advanced_python_traps()

    # 2. 本番のSpotifyデータ取得 & DJソートアルゴリズム
    try:
        sp = get_spotify_client()
        tracks = fetch_favorite_tracks_features(sp)

        if not tracks:
            logger.warning("処理対象の楽曲データがありません。")
            return

        # DJ選曲ロジックを適用
        playlist_df = create_fade_in_playlist(tracks)

        print("\n=== 🎧 DJロジック適用：Energy右肩上がりプレイリスト ===")
        print(playlist_df[["title", "artist", "energy", "valence"]].to_string(index=True))
        print("-" * 80)

        # アンパック代入の実用例（最初と最後の曲を抽出して流れを確認）
        if len(playlist_df) >= 2:
            first_row = playlist_df.iloc[0]
            last_row = playlist_df.iloc[-1]
            print(f"🎵 1曲目（始まりの曲）: '{first_row['title']}' by {first_row['artist']} (Energy: {first_row['energy']:.2f})")
            print(f"🔥 ラスト（最高潮の曲）: '{last_row['title']}' by {last_row['artist']} (Energy: {last_row['energy']:.2f})")
            print("-" * 80)

    except Exception as e:
        logger.error("処理中にエラーが発生しました: %s", e)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
