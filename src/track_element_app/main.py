import asyncio

from track_element_app.models.track import TrackData
from track_element_app.services.spotify_client import SpotifyClient
from track_element_app.services.track_analyzer import TrackAnalyzer
from track_element_app.utils.logger import get_logger, setup_logger

setup_logger()
logger = get_logger("track_element_app.main")


async def async_main() -> None:
    spotify_client = SpotifyClient()
    analyzer = TrackAnalyzer(spotify_client=spotify_client)

    try:
        # --- ロジック: 最近再生した曲の取得と分析 ---
        logger.info("最近再生した楽曲の取得を開始します...")

        # 1. 最近の再生履歴を取得
        recent_data = spotify_client.fetch_recently_played_tracks(limit=50)
        items = recent_data.get("items", [])

        if not items:
            logger.warning("最近の再生履歴が見つかりませんでした。")
            return

        # 重複を除去しつつ、トラックIDを抽出
        track_ids = list({item["track"]["id"] for item in items})
        features_list = spotify_client.fetch_audio_features(track_ids)

        # データの構築
        tracks = []
        for item, features in zip(items, features_list, strict=False):
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

        # 2. 分析・選曲ロジック適用
        playlist_df = analyzer.create_fade_in_playlist(tracks)
        print("\n=== 🎵 今週の再生履歴からプレイリストを作成 ===")
        print(playlist_df[["title", "artist", "energy"]].to_string(index=True))

        # 3. プレイリスト化（自動保存）
        target_track_ids = playlist_df["track_id"].tolist()
        result = spotify_client.create_playlist_and_add_tracks(name="My Weekly Favorites (Auto)", track_ids=target_track_ids)
        logger.info("プレイリストを作成しました: %s", result["playlist_id"])

    except Exception as e:
        logger.error("処理中にエラーが発生しました: %s", e, exc_info=True)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
