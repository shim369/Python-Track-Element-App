import re

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
    NotStr,
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

from track_element_app.services.spotify_client import SpotifyClient
from track_element_app.services.track_analyzer import TrackAnalyzer

app, rt = fast_app()
analyzer = TrackAnalyzer()
spotify_client = SpotifyClient()


@rt("/")  # type: ignore[untyped-decorator]
def get() -> Main:
    header = Section(H1("Track Element App"), Caption("Spotifyの楽曲データを多角的に分析し、時間旅行のような選曲体験を。"))

    sidebar = Aside(
        H3("配信・認証設定"),
        Form(
            Input(type="text", name="scope", value="user-library-read playlist-modify-public", placeholder="APIスコープを入力"),
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
        raw_scope_input = scope.strip()
        if not re.match(r"^[a-zA-Z0-9\-_,\s]+$", raw_scope_input):
            raise ValueError("スコープに使用できない不正な文字が含まれています。")

        # 1. クレンジング・可視化シミュレーション
        raw_title, raw_artist = "Bohemian Rhapsody - 2011 Remastered", "Queen feat. Everyone"
        clean_title, clean_artist = analyzer.clean_track_meta(raw_title, raw_artist)
        svg_chart = analyzer.generate_svg_radar_chart(0.40, 0.85, 0.65)

        chart_container = Div(NotStr(svg_chart), style="text-align: center; padding: 1rem;")
        result_table = Table(
            Thead(Tr(Th("項目"), Th("API生データ"), Th("クレンジング後"))),
            Tbody(Tr(Td("楽曲名"), Td(raw_title), Td(clean_title)), Tr(Td("アーティスト"), Td(raw_artist), Td(clean_artist))),
        )

        # ★ 選曲されたと仮定するトラックIDの隠しリスト（カンマ区切り文字列としてフォームで送る）
        mock_selected_ids = "4pt5fD6g,11dF9JVv,2TpxZ7Jg"

        # ★ 「Spotifyに保存」を実行するセクションを動的HTML断片に追加
        export_section = Section(
            H3("DJ選曲結果をエクスポート"),
            Form(
                # トラックIDリストとデフォルトのプレイリスト名を隠しデータ/入力欄として送信
                Input(type="hidden", name="track_ids_str", value=mock_selected_ids),
                Div(
                    Input(type="text", name="playlist_name", value="My Track Element Mix", placeholder="プレイリスト名を入力"),
                    Button("Spotifyに保存", type="submit", cls="secondary"),
                    cls="grid",  # ← Pico CSSのグリッドをクラスで指定
                ),
                hx_post="/save_playlist",
                hx_target="#save-result-area",  # 結果だけを専用のエリアに非同期流し込み
            ),
            Div(id="save-result-area"),  # 初期状態は空
        )

        return Div(
            Div(P("認証およびマイライブラリの解析に成功しました。"), cls="alert alert-success"),
            H3("現在の音楽成分（平均値）"),
            chart_container,
            H3("メタデータ・クレンジング検証"),
            result_table,
            export_section,
            cls="analysis-results",
        )

    except ValueError as err:
        return Div(P(f"【バリデーションエラー】: {err}"), cls="alert alert-danger")


# ★ 新規追加: プレイリストを非同期で保存するエンドポイント
@rt("/save_playlist")  # type: ignore[untyped-decorator]
def save_playlist(playlist_name: str, track_ids_str: str) -> Div:
    """選曲されたトラックID群をもとに、非同期でプレイリストを構築・保存する。"""
    try:
        # カンマ区切りの文字列をリストに復元
        track_ids = [tid.strip() for tid in track_ids_str.split(",") if tid.strip()]

        if not track_ids:
            raise ValueError("保存するトラックが存在しません。")

        # SpotifyClientの書き出しロジックを呼び出し
        res = spotify_client.create_playlist_and_add_tracks(playlist_name.strip(), track_ids)

        # 成功メッセージのHTML断片を返却（Pico CSSのアラート表現）
        return Div(
            P(f"🎵 プレイリスト 『{res['name']}』 をSpotifyに自動生成しました！（合計: {res['total_tracks']}曲）"),
            cls="alert alert-success",
            style="margin-top: 1rem;",
        )
    except Exception as err:
        return Div(P(f"【エクスポート失敗】: {err}"), cls="alert alert-danger", style="margin-top: 1rem;")


if __name__ == "__main__":
    serve()
