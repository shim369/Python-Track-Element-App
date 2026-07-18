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
    P,
    Section,
    fast_app,  # ← fast_app を明示的にインポートに追加、使わない FastHTML は削除
    serve,
)

# FastHTMLアプリケーションの初期化
app, rt = fast_app()


@rt("/")  # type: ignore[untyped-decorator]
def get() -> Main:
    """初期画面（GETリクエスト）のレンダリング"""

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

    main_content = Section(H3("分析コントロール"), Div(P("サイドバーから分析を開始してください。"), id="result-area"))

    return Main(header, Div(sidebar, main_content, cls="grid"), cls="container")


@rt("/analyze")  # type: ignore[untyped-decorator]
def post(scope: str) -> Div:
    """分析開始ボタン押下時の非同期処理（POSTリクエスト）"""
    try:
        raw_scope_input = scope.strip()

        if not re.match(r"^[a-zA-Z0-9\-_,\s]+$", raw_scope_input):
            raise ValueError("スコープに使用できない不正な文字（記号など）が含まれています。")

        sanitized_scope = ", ".join([s.strip() for s in re.split(r"[,\s]+", raw_scope_input) if s.strip()])

        if not sanitized_scope:
            raise ValueError("スコープ文字列が空です。有効なスコープを指定してください。")

        success_message = f"認証チェック成功: スコープ「{sanitized_scope}」で分析処理を開始します。"

        return Div(
            P(success_message),
            P("バックエンドの分析ロジックを実行中...（次のステップで結合します）", cls="secondary"),
            cls="alert alert-success",
        )

    except ValueError as e:
        return Div(P(f"【バリデーションエラー】: {e}"), cls="alert alert-danger")


if __name__ == "__main__":
    serve()
