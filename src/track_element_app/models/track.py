from dataclasses import dataclass, fields


# ==========================================
# 型アノテーションの罠シミュレーション用クラス
# ==========================================
@dataclass(frozen=True)
class DummyTrackSpecification:
    # 型アノテーションがあるものは適切に「フィールド」として認識される
    genre: str
    min_bpm: float = 60.0

    # 罠：型アノテーションを忘れると、ただの「クラス変数」になる
    # dataclasses.fields() のカウントやイテレーションから完全に無視されます
    DEFAULT_PLATFORM = "Spotify"


def verify_dataclass_trap() -> int:
    """
    データクラスのフィールド数を返す関数。
    DEFAULT_PLATFORM はカウントされないため、返り値は 3 ではなく 2 になる。
    """
    all_fields = fields(DummyTrackSpecification)
    return len(all_fields)


# ==========================================
# 本番用：楽曲データクラス
# ==========================================
@dataclass(frozen=True)
class TrackData:
    track_id: str
    title: str
    artist: str
    danceability: float
    energy: float
    valence: float
    release_date: str

    def __post_init__(self) -> None:
        """
        インスタンス化直後にバリデーションを行う（Ch4仕様）。
        Spotifyのオーディオ特徴量は 0.0 〜 1.0 の範囲に収まる性質を持つため境界値を検証。
        """
        # 数値のバリデーション例
        metrics = {"danceability": self.danceability, "energy": self.energy, "valence": self.valence}
        for name, value in metrics.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")
