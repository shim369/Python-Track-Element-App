from fasthtml.common import (
    H1,
    H3,
    Button,
    Caption,
    Div,
    Form,
    Header,
    Img,
    Main,
    P,
    Section,
    Style,
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

# SpotifyカラーのCSSを定義
css = """
:root {
    --primary: #1DB954;
    --background-color: #121212;
    --color: #FFFFFF;
}
body { background-color: var(--background-color); color: var(--color); }
.card { background-color: #181818; padding: 1rem; border-radius: 8px; }
.analysis-results { margin-top: 1rem; }

section {padding: 1rem;}

/* ボタン */
button, .primary {
    background-color: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #000000 !important;
    font-weight: bold;
}

/* テーブルの背景を薄いグリーンに修正 */
table {
    border-collapse: collapse;
    width: 100%;
}
thead th {
    background-color: var(--primary) !important;
    color: #000 !important;
}
/* tdとthのデフォルト背景を上書き */
td, th {
    background-color: rgba(29, 185, 84, 0.1) !important;
    border-bottom: 1px solid #333 !important;
    color: #fff !important;
}
/* ホバーした時に少し明るくするとSpotifyっぽくなります */
tbody tr:hover td {
    background-color: rgba(29, 185, 84, 0.2) !important;
}
"""
app, rt = fast_app(hdrs=(Style(css),))
analyzer = TrackAnalyzer()
spotify_client = SpotifyClient()


@rt("/")  # type: ignore[untyped-decorator]
def get() -> Main:
    # タイトルとボタンを同じエリアに配置
    header = Header(
        Div(H1("Spotify Library Recent", style="margin-bottom: 0; color: #1DB954;"), Caption("直近でライブラリに追加した楽曲を表示"), style="flex: 1;"),
        Form(
            Button("最新の追加曲を取得", type="submit", cls="primary"),
            hx_post="/analyze",
            hx_target="#result-area",
            style="margin-bottom: 0;",
        ),
        style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; background: #181818; border-radius: 8px; margin-bottom: 1rem;",
    )

    main_content = Section(Div(P("ボタンを押して取得を開始してください。"), id="result-area"))

    return Main(header, main_content, cls="container")


@rt("/analyze")  # type: ignore[untyped-decorator]
def post() -> Div:
    try:
        saved_tracks_data = spotify_client.fetch_user_saved_tracks(limit=50)
        items = saved_tracks_data.get("items", [])

        track_list = [{"track": item["track"], "added_at": item["added_at"]} for item in items if item.get("track")]

        if not track_list:
            return Div(P("楽曲が見つかりませんでした。"), cls="alert alert-warning")

        sorted_tracks = sorted(track_list, key=lambda t: t["added_at"], reverse=True)

        ranking_items = [
            Tr(
                # 画像を追加 (高さ40px程度に制限)
                Td(Img(src=t["track"]["album"]["images"][-1]["url"], style="height: 40px; border-radius: 4px;")),
                Td(t["track"]["artists"][0]["name"]),
                Td(t["track"]["name"]),
                Td(t["added_at"][:10]),
            )
            for t in sorted_tracks[:10]
        ]

        # 余計なステータス表示を削除し、結果テーブルだけにする
        return Div(
            H3("最近お気に入りに追加した楽曲"),
            Table(Thead(Tr(Th(""), Th("アーティスト名"), Th("曲名"), Th("追加日"))), Tbody(*ranking_items)),
            cls="analysis-results",
        )
    except Exception as err:
        return Div(P(f"エラー: {err}"), cls="alert alert-danger")


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
