from fasthtml.common import (
    H1,
    H3,
    A,
    Button,
    Div,
    Form,
    Header,
    Img,
    Input,
    Main,
    P,
    Script,
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

# SpotifyカラーのCSS
css = """
:root {
    --primary: #1DB954;
    --background-color: #121212;
    --color: #FFFFFF;
}
body { background-color: var(--background-color); color: var(--color); }
header { padding: 1rem; }
.analysis-results { margin-top: 1rem; }
.tab-container { display: flex; gap: 1rem; margin: 1rem 0; border-bottom: 1px solid #333; }
.tab-link { cursor: pointer; padding: 0.5rem 1rem; color: #b3b3b3; text-decoration: none; }
.tab-link.active { color: var(--primary); border-bottom: 2px solid var(--primary); font-weight: bold; }
button, .primary { background-color: var(--primary) !important; border-color: var(--primary) !important; color: #000000 !important; font-weight: bold; }
table { border-collapse: collapse; width: 100%; }
thead th { background-color: var(--primary) !important; color: #000 !important; }
td, th { background-color: rgba(29, 185, 84, 0.1) !important; border-bottom: 1px solid #333 !important; color: #fff !important; }
tbody tr:hover td { background-color: rgba(29, 185, 84, 0.2) !important; }
.btn-playlist {
    background-color: var(--primary-dark) !important;
    color: #fff !important;
    border: none !important;
    padding: 0.8rem 1.5rem !important;
    border-radius: 20px !important;
    cursor: pointer;
}
.btn-playlist:hover {
    background-color: #166534 !important; /* ホバー時はさらに濃く */
}
"""

app, rt = fast_app(hdrs=(Style(css),))
analyzer = TrackAnalyzer()
spotify_client = SpotifyClient()


@rt("/")
def get() -> Main:
    return Main(
        Header(H1("Spotify Insights", style="color: var(--primary);")),
        Div(
            Div(
                A("直近の追加曲", hx_get="/analyze", hx_target="#result-area", cls="tab-link active", onclick="updateActiveTab(this)"),
                A("週間再生トップ10", hx_get="/get_top_tracks", hx_target="#result-area", cls="tab-link", onclick="updateActiveTab(this)"),
                cls="tab-container",
            ),
            Div(id="result-area", hx_get="/analyze", hx_trigger="load"),
            Script("""
                function updateActiveTab(el) {
                    document.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
                    el.classList.add('active');
                }
            """),
            cls="container",
        ),
    )


@rt("/analyze")
def get_analyze() -> Div:
    try:
        saved_tracks_data = spotify_client.fetch_user_saved_tracks(limit=50)
        items = saved_tracks_data.get("items", [])
        track_list = [{"track": item["track"], "added_at": item["added_at"]} for item in items if item.get("track")]

        if not track_list:
            return Div(P("楽曲が見つかりませんでした。"), cls="alert alert-warning")

        sorted_tracks = sorted(track_list, key=lambda t: t["added_at"], reverse=True)
        ranking_items = [
            Tr(
                Td(Img(src=t["track"]["album"]["images"][-1]["url"], style="height: 40px; border-radius: 4px;")),
                Td(t["track"]["artists"][0]["name"]),
                Td(t["track"]["name"]),
                Td(t["added_at"][:10]),
            )
            for t in sorted_tracks[:10]
        ]

        return Div(
            H3("最近お気に入りに追加した楽曲"),
            Table(Thead(Tr(Th(""), Th("アーティスト名"), Th("曲名"), Th("追加日"))), Tbody(*ranking_items)),
            cls="analysis-results",
        )
    except Exception as err:
        return Div(P(f"エラー: {err}"), cls="alert alert-danger")


@rt("/get_top_tracks")
def get_top_tracks() -> Div:
    try:
        top_tracks_data = spotify_client.fetch_user_top_tracks(limit=10)
        items = top_tracks_data.get("items", [])

        # プレイリスト作成用のIDリストをカンマ区切り文字列にする
        track_ids = ",".join([t["id"] for t in items])

        ranking_items = [
            Tr(
                Td(Img(src=t["album"]["images"][-1]["url"], style="height: 40px; border-radius: 4px;")),
                Td(t["artists"][0]["name"]),
                Td(t["name"]),
            )
            for t in items
        ]

        return Div(
            H3("今週の再生トップ10楽曲"),
            # プレイリスト作成フォーム
            Form(
                Input(type="hidden", name="track_ids_str", value=track_ids),
                Input(type="text", name="playlist_name", placeholder="プレイリスト名", required=True),
                Button("このリストでプレイリストを作成", type="submit", cls="btn-playlist"),
                hx_post="/save_playlist",
                hx_target="#result-area",
            ),
            Table(Thead(Tr(Th(""), Th("アーティスト名"), Th("曲名"))), Tbody(*ranking_items)),
            cls="analysis-results",
        )
    except Exception as err:
        return Div(P(f"エラー: {err}"), cls="alert alert-danger")


@rt("/save_playlist")
@measure_time
def post(playlist_name: str, track_ids_str: str) -> Div:
    try:
        # カンマ区切り文字列をリストに戻す
        track_ids = [tid.strip() for tid in track_ids_str.split(",") if tid]

        # プレイリスト作成
        res = spotify_client.create_playlist_and_add_tracks(name=playlist_name, track_ids=track_ids)

        return Div(
            P(f"✅ プレイリスト 『{res['name']}』 を作成しました！"),
            # 成功時に再度リストを表示するボタンなどを置くとより親切です
            cls="alert alert-success",
        )
    except Exception as err:
        return Div(P(f"❌ 保存失敗: {err}"), cls="alert alert-danger")


if __name__ == "__main__":
    serve()
