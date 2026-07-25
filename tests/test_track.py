from track_element_app.models.track import TrackData


def test_track_data_creation():
    """TrackDataインスタンスが正しく生成できるかテスト"""
    track = TrackData(
        track_id="test_id_123",
        title="Test Title",
        artist="Test Artist",
        release_date="2026-07-25",
        danceability=0.0,
        energy=0.0,
        valence=0.0,
    )

    assert track.track_id == "test_id_123"
    assert track.title == "Test Title"
    assert track.artist == "Test Artist"
    assert track.release_date == "2026-07-25"
    assert track.danceability == 0.0
