from dataclasses import dataclass


@dataclass(frozen=True)
class TrackData:
    track_id: str
    title: str
    artist: str
    release_date: str
    danceability: float | None = None
    energy: float | None = None
    valence: float | None = None

    def __post_init__(self) -> None:
        """
        インスタンス化直後にバリデーションを行う。
        値が存在する場合のみ 0.0 〜 1.0 の範囲を検証する。
        """
        metrics = {
            "danceability": self.danceability,
            "energy": self.energy,
            "valence": self.valence,
        }
        for name, value in metrics.items():
            if value is not None and not (0.0 <= value <= 1.0):
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")
