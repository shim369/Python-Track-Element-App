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

# アナライザーのインポート
from track_element_app.services.track_analyzer import TrackAnalyzer

app, rt = fast_app()
analyzer = TrackAnalyzer()


@rt("/")  # type: ignore[untyped-decorator]
def get() -> Main:
    header = Section(H1("Track Element App"), Caption("Spotifyの楽曲データを多角的に分析し、時間旅行のような選曲体験を。"))

    sidebar = Aside(
        H3("配信・認証設定"),
        Form(
            Input(type="text", name="scope", value="user-library-read", placeholder="APIスコープを入力"),
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

        # 1. 擬似的なSpotifyからの生データ取得シミュレーション
        raw_title = "Bohemian Rhapsody - 2011 Remastered"
        raw_artist = "Queen feat. Everyone"

        # 2. 本日実装した試験対策クレンジングロジックの適用
        clean_title, clean_artist = analyzer.clean_track_meta(raw_title, raw_artist)

        # 3. 擬似的な平均特徴量（Danceability: 0.40, Energy: 0.85, Valence: 0.65）
        d, e, v = 0.40, 0.85, 0.65
        svg_chart = analyzer.generate_svg_radar_chart(d, e, v)

        # FastHTMLでは、生のHTML/SVG文字列を安全にレンダリングする際に `NotStr()` を使用します
        chart_container = Div(NotStr(svg_chart), style="text-align: center; padding: 1rem;")

        # クレンジング結果を表示するテーブルコンポーネント
        result_table = Table(
            Thead(Tr(Th("項目"), Th("API生データ"), Th("クレンジング後"))),
            Tbody(Tr(Td("楽曲名"), Td(raw_title), Td(clean_title)), Tr(Td("アーティスト"), Td(raw_artist), Td(clean_artist))),
        )

        return Div(
            Div(P("認証およびマイライブラリの解析に成功しました。"), cls="alert alert-success"),
            H3("現在の音楽成分（平均値）"),
            chart_container,
            H3("メタデータ・クレンジング検証"),
            result_table,
            cls="analysis-results",
        )

    except ValueError as err:
        return Div(P(f"【バリデーションエラー】: {err}"), cls="alert alert-danger")


if __name__ == "__main__":
    serve()
