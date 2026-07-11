from dataclasses import fields

import pytest
from track_element_app.models.track import DummyTrackSpecification, TrackData, verify_dataclass_trap


def test_dataclass_field_trap() -> None:
    """型アノテーションがない変数が fields() から除外される仕様を検証（Ch4対策）"""
    # 実際には 3 つの変数があるが、fields() はアノテーションありの 2 つしか認識しない
    assert len(fields(DummyTrackSpecification)) == 2
    assert verify_dataclass_trap() == 2


def test_track_data_validation() -> None:
    """境界値チェックが正常に動作し、範囲外の数値で ValueError が出るか検証（Ch3, 16対策）"""
    with pytest.raises(ValueError) as excinfo:
        # energy が 1.5 (範囲外) なのでエラーになるはず
        TrackData(
            track_id="dummy_id",
            title="Dummy Title",
            artist="Dummy Artist",
            danceability=0.5,
            energy=1.5,
            valence=0.5,
            release_date="2026",
        )
    assert "energy must be between 0.0 and 1.0" in str(excinfo.value)
