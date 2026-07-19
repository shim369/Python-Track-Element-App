
# クラス・モデル設計

## TrackData (`models/track.py`)

* **役割:** 楽曲情報の不変エンティティ。
* **責務:** `dataclass(frozen=True)` による楽曲ID、タイトル、アーティスト、アートURL、追加日の保持と数値バリデーション。

## SpotifyClient (`services/spotify_client.py`)

* **役割:** APIとの通信管理。
* **責務:** OAuth認証管理、保存済み楽曲リストの取得、`create_playlist_and_add_tracks` によるプレイリスト作成機能。

## TrackAnalyzer (`services/track_analyzer.py`)

* **役割:** 分析・加工ロジック。
* **責務:** `Pandas` を用いた楽曲メタデータの正規化、クレンジング、および将来的なデータ分析のためのデータフレーム構築。

## FastHTML ルーティング (`gui/app.py`)

* **役割:** アプリケーションのエントリポイント。
* **責務:** `rt` ルーティング定義、htmxリクエストへのHTML断片返却、サービス層のコンポジション。
