from fasthtml.common import (
    H1,
    H3,
    Aside,
    Button,
    Caption,
    Div,
    Form,
    Input,
    Main,
    P,
    Section,
    Table,
    Tbody,
    Td,
    Th,
    Thead,
    Tr,
    fast_app,
    serve,
)

from track_element_app.config.logging_config import setup_logging
from track_element_app.services.spotify_client import SpotifyClient
from track_element_app.services.track_analyzer import TrackAnalyzer
from track_element_app.utils.decorators import measure_time

setup_logging()

app, rt = fast_app()
analyzer = TrackAnalyzer()
spotify_client = SpotifyClient()


@rt("/")  # type: ignore[untyped-decorator]
def get() -> Main:
    header = Section(
        H1("Track Element App"),
        Caption("Spotifyの楽曲データを多角的に分析し、時間旅行のような選曲体験を。"),
    )
    sidebar = Aside(
        H3("配信・認証設定"),
        Form(
            Input(
                type="text",
                name="scope",
                value="user-library-read playlist-modify-public user-read-recently-played",
                placeholder="APIスコープを入力",
            ),
            Button("分析を開始する", type="submit", cls="primary"),
            hx_post="/analyze",
            hx_target="#result-area",
        ),
        Div(H3("システムステータス"), P("API接続可能 (認証待ち)", id="status-text"), cls="card"),
    )
    main_content = Section(H3("分析結果 / 可視化レーダー"), Div(P("サイドバーから分析を開始してください。"), id="result-area"))
    return Main(header, Div(sidebar, main_content, cls="grid"), cls="container")


@rt("/analyze")  # type: ignore[untyped-decorator]
def post(scope: str) -> Div:
    try:
        # 50曲取得（ここは変えません）
        saved_tracks_data = spotify_client.fetch_user_saved_tracks(limit=50)
        items = saved_tracks_data.get("items", [])

        # 特徴量は取れないものとして、単にライブラリの楽曲情報を表示する
        track_list = [item["track"] for item in items if item.get("track")]

        if not track_list:
            return Div(P("ライブラリから楽曲が見つかりませんでした。"), cls="alert alert-warning")

        # 最初の楽曲をデモとして表示する
        target_track = track_list[0]
        clean_title, _ = analyzer.clean_track_meta(target_track["name"], target_track["artists"][0]["name"])

        # 楽曲のメタデータでテーブルを作成
        result_table = Table(
            Thead(Tr(Th("項目"), Th("値"))),
            Tbody(
                Tr(Td("楽曲名"), Td(clean_title)),
                Tr(Td("アーティスト"), Td(target_track["artists"][0]["name"])),
                Tr(Td("アルバム"), Td(target_track["album"]["name"])),
                Tr(Td("リリース日"), Td(target_track["album"]["release_date"])),
            ),
        )

        return Div(
            Div(P("🎉 楽曲データの取得に成功しました（メタデータを使用）。"), cls="alert alert-success"),
            H3("楽曲詳細データ"),
            result_table,
            # (以下、保存ボタンなどの描画はそのまま)
        )
    except Exception as err:
        return Div(P(f"【エラー】: {err}"), cls="alert alert-danger")


@rt("/save_playlist")  # type: ignore[untyped-decorator]
@measure_time
def save_playlist(playlist_name: str, track_ids_str: str) -> Div:
    try:
        track_ids = [tid.strip() for tid in track_ids_str.split(",") if tid.strip()]
        res = spotify_client.create_playlist_and_add_tracks(playlist_name.strip(), track_ids)
        return Div(P(f"🎵 プレイリスト 『{res['name']}』 をSpotifyに自動生成しました！"), cls="alert alert-success")
    except Exception as err:
        return Div(P(f"【システムエラー】: {err}"), cls="alert alert-danger")


if __name__ == "__main__":
    serve()
