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
        # --- ロジック: 最近再生した曲の取得 ---
        logger.info("最近再生した楽曲の取得を開始します...")

        # 1. 最近の再生履歴を取得
        recent_data = spotify_client.fetch_recently_played_tracks(limit=50)
        items = recent_data.get("items", [])

        if not items:
            logger.warning("最近の再生履歴が見つかりませんでした。")
            return

        # 2. データの構築（重複を除去しつつ順序を保持）
        seen_track_ids = set()
        tracks = []
        for item in items:
            t = item["track"]
            track_id = t["id"]
            if track_id in seen_track_ids:
                continue
            seen_track_ids.add(track_id)

            tracks.append(
                TrackData(
                    track_id=track_id,
                    title=t["name"],
                    artist=t["artists"][0]["name"],
                    release_date=t["album"]["release_date"],
                )
            )

        if not tracks:
            logger.warning("有効な楽曲データが見つかりませんでした。")
            return

        # 3. 分析・選曲ロジック適用（※Analyzer側の実装に応じて適宜調整してください）
        playlist_df = analyzer.create_fade_in_playlist(tracks)
        print("\n=== 🎵 今週の再生履歴からプレイリストを作成 ===")
        print(playlist_df[["title", "artist"]].to_string(index=True))

        # 4. プレイリスト化（自動保存）
        target_track_ids = playlist_df["track_id"].tolist()
        result = spotify_client.create_playlist_and_add_tracks(name="My Weekly Favorites (Auto)", track_ids=target_track_ids)
        # spotipyのレスポンス仕様に合わせて result["id"] を参照する
        logger.info("プレイリストを作成しました: %s", result.get("id"))

    except Exception as e:
        logger.error("処理中にエラーが発生しました: %s", e, exc_info=True)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
