import shutil
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from track_element_app.gui.app import app  # FastHTMLアプリインスタンス
from track_element_app.services.track_analyzer import TrackAnalyzer

# =====================================================================
# 1. ロジック・例外ハンドリングの堅牢性テスト (pytest.raises)
# =====================================================================


def test_track_analyzer_type_and_value_errors() -> None:
    """TypeError と ValueError の発生とキャッチを厳密に検証"""
    analyzer = TrackAnalyzer()

    # 1. clean_track_meta の入力型エラー検証 (TypeError)
    with pytest.raises(TypeError):
        analyzer.clean_track_meta(12345, "Artist")  # type: ignore[arg-type]

    # 2. create_fade_in_playlist の入力型エラー検証 (TypeError)
    with pytest.raises(TypeError):
        analyzer.create_fade_in_playlist("not-a-list")  # type: ignore[arg-type]

    # 3. 空データに対する適切なハンドリング検証 (ValueError)
    with pytest.raises(ValueError, match="Track list cannot be empty."):
        analyzer.create_fade_in_playlist([])


def test_track_analyzer_memory_error_guard() -> None:
    """一括メモリ確保リスク（OOM）に対するアプリケーション・セーフガードの検証"""
    analyzer = TrackAnalyzer()

    # 巨大なダミーリストによる一括処理リスクを検知して MemoryError を投げるか検証
    huge_tracks = [{"id": str(i), "energy": 0.5, "valence": 0.5} for i in range(100_001)]
    with pytest.raises(MemoryError):
        analyzer.create_fade_in_playlist(huge_tracks)


def test_shutil_file_exceptions(tmp_path: pytest.TempPathFactory) -> None:
    """レポート出力時における shutil のファイル操作例外の検証"""
    analyzer = TrackAnalyzer()

    # テスト用のクリーンな一時ディレクトリ環境
    test_dir = tmp_path / "report_workspace"
    test_dir.mkdir()

    dummy_report = test_dir / "playlist_report.csv"
    dummy_report.write_text("id,title,energy\n1,Song,0.8")

    # 1. 宛先がファイルではなくディレクトリだった場合の IsADirectoryError 検証
    with pytest.raises(IsADirectoryError):
        analyzer.export_playlist_report(str(dummy_report), str(test_dir))

    # 2. コピー元とコピー先が完全に同一だった場合の SameFileError 検証
    with pytest.raises(shutil.SameFileError):
        analyzer.export_playlist_report(str(dummy_report), str(dummy_report))


# =====================================================================
# 2. 厳格な Mock 検証 (autospec, unsafe, assert_called_with)
# =====================================================================


@patch("track_element_app.services.spotify_client.SpotifyClient", autospec=True)
def test_spotify_client_strict_mock(mock_spotify_client_cls: MagicMock) -> None:
    """Mock の仕様制限機能を活かした API 通信部分のモック化テスト"""
    mock_instance = mock_spotify_client_cls.return_value

    with pytest.raises(AttributeError):
        mock_instance.typo_method_name_here()

    # 正常系: メソッドのモック化と呼び出し検証
    mock_instance.create_playlist_and_add_tracks.return_value = {"name": "Summer Mix", "total_tracks": 2}

    res = mock_instance.create_playlist_and_add_tracks("Summer Mix", ["id1", "id2"])
    assert res["total_tracks"] == 2

    # 引数が完全に一致しているかを厳格に検証
    mock_instance.create_playlist_and_add_tracks.assert_called_with("Summer Mix", ["id1", "id2"])


# =====================================================================
# 3. FastHTML エンドポイントのオフライン統合テスト
# =====================================================================


def test_fasthtml_endpoints_offline() -> None:
    """test_clientを使用したネットワーク非依存のUI・エンドポイント検証"""
    # FastHTML公式のヘルパー関数、またはappのtest_clientメソッドを使用
    client = TestClient(app)

    # 1. メイン画面のレンダリング確認
    response = client.get("/")
    assert response.status_code == 200
    assert "Track Element App" in response.text

    # 2. プレイリスト保存エンドポイントのモック検証
    with patch("track_element_app.gui.app.spotify_client") as mock_app_client:
        mock_app_client.create_playlist_and_add_tracks.return_value = {"name": "My Auto Playlist", "total_tracks": 5}

        post_response = client.post("/save_playlist", data={"playlist_name": "My Auto Playlist", "track_ids_str": "id1,id2"})
        assert post_response.status_code == 200
        assert "My Auto Playlist" in post_response.text
        assert "alert-success" in post_response.text
