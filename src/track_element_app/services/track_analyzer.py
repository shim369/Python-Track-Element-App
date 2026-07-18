from collections.abc import Generator

import pandas as pd

from track_element_app.models.track import TrackData
from track_element_app.services.spotify_client import SpotifyClient
from track_element_app.utils.logger import get_logger

logger = get_logger("track_element_app.services.track_analyzer")


class TrackAnalyzer:
    """Pandas を用いた音楽成分のデータ分析、および各種選曲ロジックを実行するクラス"""

    def __init__(self, spotify_client: SpotifyClient) -> None:
        # ⭕️ 継承ではなく委譲・コンポジション (has-a) の徹底
        self.spotify_client = spotify_client

    def create_fade_in_playlist(self, tracks: list[TrackData]) -> pd.DataFrame:
        """Energy がなだらかに右肩上がりになるようにソートした DataFrame を返す"""
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

        return df.sort_values(by=["energy", "valence"], ascending=[True, True]).reset_index(drop=True)

    def run_time_travel_logic(self, start_artist_id: str, max_artists: int = 5) -> pd.DataFrame:
        """指定アーティストから芋づる式に関連アーティストをたどり、1970~80年代の名曲を抽出"""
        logger.info("タイムトラベル選曲ロジック起動。関連アーティストを探索中...")

        related_artists = self.spotify_client.fetch_related_artists(start_artist_id)
        target_artists = related_artists[:max_artists]

        all_tracks_data = []

        # 芋づる式に楽曲をループ探索
        for artist in target_artists:
            artist_name = artist["name"]
            top_tracks = self.spotify_client.fetch_artist_top_tracks(artist["id"])

            if not top_tracks:
                continue

            track_ids = [t["id"] for t in top_tracks]
            features_list = self.spotify_client.fetch_audio_features(track_ids)

            for track, features in zip(top_tracks, features_list, strict=True):
                if features is None:
                    continue

                # リリース年のフィルタリング（1970年代〜1980年代）
                release_date = track["album"]["release_date"]
                try:
                    release_year = int(release_date[:4])
                except ValueError:
                    continue

                if 1970 <= release_year <= 1989:
                    all_tracks_data.append(
                        {
                            "title": track["name"],
                            "artist": artist_name,
                            "danceability": features["danceability"],
                            "energy": features["energy"],
                            "valence": features["valence"],
                            "release_date": release_date,
                        }
                    )

        df = pd.DataFrame(all_tracks_data)
        if df.empty:
            logger.warning("指定された範囲（1970〜1980年代）に合致する楽曲が見つかりませんでした。")
            return df

        return df.sort_values(by="release_date").reset_index(drop=True)

    # =====================================================================
    # ★試験対策：ジェネレータ・メモリ・アンパックの罠シミュレーション
    # =====================================================================
    def _huge_track_generator(self, limit: int = 10000) -> Generator[str, None, None]:
        for i in range(limit):
            yield f"track_id_heavy_{i}"

    def simulate_advanced_python_traps(self) -> None:
        """ジェネレータ制限、メモリ節約、アンパック代入の挙動を検証する"""
        logger.debug("--- [Advanced Python Traps Verification] ---")

        # 1. ジェネレータと len() の TypeError 罠
        gen = self._huge_track_generator(5)
        try:
            _ = len(gen)  # type: ignore[arg-type]
        except TypeError as e:
            logger.debug("Trap 1 (Generator len): Successfully caught expected TypeError: %s", e)

        # 2. 巨大データと list() 化による MemoryError リスク
        limited_items = [next(gen) for _ in range(3)]
        logger.debug("Trap 2 (Memory Saver): Safely extracted partial items: %s", limited_items)

        # 3. アスタリスクを使った残余引数アンパックの文法制限
        try:
            sample_list = ["Intro_Track", "BGM_1", "BGM_2", "Outro_Track"]
            first_song, *middle_songs, last_song = sample_list
            logger.debug("Trap 3 (Unpacking): First: %s, Last: %s", first_song, last_song)
            _song1, _song2 = sample_list
        except ValueError as e:
            logger.debug("Trap 3 (ValueError Case): Successfully caught ValueError: %s", e)

        logger.debug("--------------------------------------------")
