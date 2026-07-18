import asyncio

from track_element_app.models.track import TrackData
from track_element_app.services.spotify_client import SpotifyClient
from track_element_app.services.track_analyzer import TrackAnalyzer
from track_element_app.utils.logger import get_logger, setup_logger

setup_logger()
logger = get_logger("track_element_app.main")


async def async_main() -> None:
    # 1. 各コンポーネントのインスタンス化と依存性の注入 (DI)
    spotify_client = SpotifyClient()
    analyzer = TrackAnalyzer(spotify_client=spotify_client)

    # 2. 各種試験対策シミュレーションの実行
    analyzer.simulate_advanced_python_traps()
    await spotify_client.simulate_anext_trap()

    # 3. メインビジネスロジックの実行
    try:
        # --- ロジックA: お気に入り50曲のフェードイン選曲 ---
        logger.info("お気に入り曲の取得を開始します...")

        raw_saved_tracks = spotify_client.fetch_user_saved_tracks(limit=50)
        items = raw_saved_tracks.get("items", [])

        if not items:
            logger.warning("お気に入り曲が見つかりませんでした。")
            return

        track_ids = [item["track"]["id"] for item in items]
        features_list = spotify_client.fetch_audio_features(track_ids)

        tracks = []
        for item, features in zip(items, features_list, strict=True):
            if features is None:
                continue
            t = item["track"]
            tracks.append(
                TrackData(
                    track_id=t["id"],
                    title=t["name"],
                    artist=t["artists"][0]["name"],
                    danceability=features["danceability"],
                    energy=features["energy"],
                    valence=features["valence"],
                    release_date=t["album"]["release_date"],
                )
            )

        playlist_df = analyzer.create_fade_in_playlist(tracks)
        print("\n=== 🎧 DJロジック適用：Energy右肩上がりプレイリスト ===")
        print(playlist_df[["title", "artist", "energy", "valence"]].to_string(index=True))
        print("-" * 80)

        # --- ロジックB: 1970〜80年代のタイムトラベル選曲 ---
        # サンプルとして、お気に入り1曲目のアーティストの関連を探索
        if tracks:
            sample_artist_id = items[0]["track"]["artists"][0]["id"]
            sample_artist_name = items[0]["track"]["artists"][0]["name"]

            print(f"\n=== 🕰️ タイムトラベル選曲：{sample_artist_name} の遺伝子 (1970-80s) ===")
            retro_df = analyzer.run_time_travel_logic(start_artist_id=sample_artist_id, max_artists=5)
            if not retro_df.empty:
                print(retro_df[["title", "artist", "release_date", "energy"]].to_string(index=True))
            print("-" * 80)

    except Exception as e:
        logger.error("メイン処理中に予期せぬエラーが発生しました: %s", e, exc_info=True)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
