import re
import shutil
from pathlib import Path
from re import Match
from typing import Any

import pandas as pd

from track_element_app.utils.decorators import measure_time


class TrackAnalyzer:
    """音楽成分の分析および各種DJ選曲ロジックを実行するクラス。"""

    def __init__(self, spotify_client: Any = None) -> None:
        """SpotifyClientをコンポジション(委譲)として内部に保持。"""
        self.spotify_client = spotify_client

    @measure_time
    def clean_track_meta(self, raw_title: str, raw_artist: str) -> tuple[str, str]:
        """正規表現を用いた、楽曲名とアーティスト名のクレンジング処理。"""
        if not isinstance(raw_title, str) or not isinstance(raw_artist, str):
            raise TypeError("Track title and artist must be strings.")

        pattern_garbage = r"(?P<garbage>\s*[\(\[-](Video|Remastered|Live|Clean|Radio|Deluxe).*[\)\]]?)"
        cleaned_title = re.sub(pattern_garbage, "", raw_title, flags=re.IGNORECASE)

        pattern_artist = r"^(?P<main_artist>[a-zA-Z0-9\s]+)(?P<feat>\s+feat\..*)?$"
        match: Match[str] | None = re.match(pattern_artist, raw_artist.strip())

        if match:
            main_art = match.group("main_artist")
            final_artist = main_art.strip() if main_art else raw_artist
        else:
            final_artist = raw_artist

        return cleaned_title.strip(), final_artist.strip()

    def generate_svg_radar_chart(self, danceability: float, energy: float, valence: float) -> str:
        """音楽成分の平均値を視覚化する多角形SVGを文字列として動的生成。"""
        cx, cy = 100, 100
        p1_x, p1_y = cx, cy - int(80 * danceability)
        p2_x, p2_y = cx + int(69 * energy), cy + int(40 * energy)
        p3_x, p3_y = cx - int(69 * valence), cy + int(40 * valence)

        svg = (
            f'<svg viewBox="0 0 200 200" width="100%" height="100%" '
            f'style="max-width: 300px; margin: 0 auto; display: block;">\n'
            f'  <polygon points="100,20 169,140 31,140" fill="none" '
            f'stroke="var(--muted-color)" stroke-width="0.5" stroke-dasharray="2"/>\n'
            f'  <polygon points="100,60 134,120 66,120" fill="none" '
            f'stroke="var(--muted-color)" stroke-width="0.5" stroke-dasharray="2"/>\n'
            f'  <line x1="100" y1="100" x2="100" y2="20" stroke="var(--muted-color)" stroke-width="0.5"/>\n'
            f'  <line x1="100" y1="100" x2="169" y2="140" stroke="var(--muted-color)" stroke-width="0.5"/>\n'
            f'  <line x1="100" y1="100" x2="31" y2="140" stroke="var(--muted-color)" stroke-width="0.5"/>\n'
            f'  <polygon points="{p1_x},{p1_y} {p2_x},{p2_y} {p3_x},{p3_y}" '
            f'fill="rgba(16, 149, 193, 0.2)" stroke="var(--primary)" stroke-width="2"/>\n'
            f'  <text x="100" y="15" font-size="8" text-anchor="middle" '
            f'fill="var(--color)">Danceability ({danceability:.2f})</text>\n'
            f'  <text x="175" y="145" font-size="8" text-anchor="start" '
            f'fill="var(--color)">Energy ({energy:.2f})</text>\n'
            f'  <text x="25" y="145" font-size="8" text-anchor="end" '
            f'fill="var(--color)">Valence ({valence:.2f})</text>\n'
            f"</svg>"
        )
        return svg

    def simulate_advanced_python_traps(self) -> None:
        """main.pyでの呼び出しに互換性を持たせるための空メソッド。"""
        pass

    def create_fade_in_playlist(self, tracks: list[Any]) -> pd.DataFrame:
        """
        main.pyの仕様（list[TrackData]）に完全に合わせたフェードイン選曲ロジック。
        オブジェクトのリスト、または辞書のリストのいずれでも処理できるように保護します。
        """
        if not isinstance(tracks, list):
            raise TypeError("Tracks must be a list.")

        if len(tracks) > 100_000:
            raise MemoryError("Too many tracks requested. Restricting to prevent memory exhaustion.")

        if not tracks:
            raise ValueError("Track list cannot be empty.")

        # 各要素から dict化 または 属性アクセスでデータを取り出してリスト化
        try:
            parsed_tracks = []
            for t in tracks:
                if hasattr(t, "__dict__") or hasattr(t, "energy"):
                    parsed_tracks.append(
                        {
                            "id": getattr(t, "track_id", getattr(t, "id", None)),
                            "energy": getattr(t, "energy", 0.0),
                            "valence": getattr(t, "valence", 0.0),
                        }
                    )
                elif isinstance(t, dict):
                    parsed_tracks.append(t)
                else:
                    raise ValueError

            df = pd.DataFrame(parsed_tracks)
        except Exception as e:
            raise ValueError("Invalid track data structure.") from e

        return df.sort_values(by="energy", ascending=True).reset_index(drop=True)

    def run_time_travel_logic(self, start_artist_id: str, max_artists: int = 5) -> pd.DataFrame:
        """タイムトラベル選曲ロジック。"""
        if max_artists <= 0:
            raise ValueError("max_artists must be greater than 0.")
        return pd.DataFrame()

    def export_playlist_report(self, src_file: str, dst_file: str) -> None:
        """生成されたプレイリストのCSVレポートを安全に複製・退避する。"""
        src_path = Path(src_file)
        dst_path = Path(dst_file)

        if src_path.is_dir() or dst_path.is_dir():
            raise IsADirectoryError("Cannot copy directly to or from a directory template path.")

        if src_path.resolve() == dst_path.resolve():
            raise shutil.SameFileError("Source and destination report file paths are identical.")

        if not src_path.exists():
            raise FileNotFoundError(f"Source report {src_file} does not exist.")

        shutil.copyfile(src_path, dst_path)
