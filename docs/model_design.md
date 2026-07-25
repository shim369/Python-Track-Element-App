# クラス・モデル設計

### `TrackData` (`models/track.py`)
* **役割:** 楽曲情報の不変エンティティ。
* **責務:** 楽曲ID、タイトル、アーティスト、アートURL、追加日、ランキング指標の保持と検証。

### `SpotifyClient` (`services/spotify_client.py`)
* **役割:** APIとの通信管理。
* **責務:** OAuth認証、ライブラリ取得、週間再生トップ10データの抽出、`create_playlist_and_add_tracks`（週間トップ専用）。

### `TrackAnalyzer` (`services/track_analyzer.py`)
* **役割:** 分析・加工ロジック。
* **責務:** 各タブ用のデータ加工、ランキング計算、楽曲メタデータの正規化。

### `FastHTML ルーティング` (`gui/app.py`)
* **役割:** アプリケーションのエントリポイント。
* **責務:** タブ切り替えルーティング、htmxリクエスト制御、サービス層のコンポジション。
