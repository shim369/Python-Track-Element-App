# クラス設計・モデル設計

## TrackData (`src/track_element_app/models/track.py`)

**役割：** 楽曲のメタデータとオーディオ特徴量を表すエンティティ
**責務：**

* 楽曲ID（`track_id`）、曲名（`title`）、アーティスト名（`artist`）、Danceability、Energy、Valence、リリース年（`release_date`）などのデータを不変（Immutable）データとして保持する。
* インスタンス化の直後に、各数値データが適切な範囲（例：Danceabilityが0.0〜1.0）に収まっているかを検証する（`__post_init__`）。
* **★試験対策の埋め込み：** 型アノテーションがない変数がフィールド（`fields()`）として認識されず、通常のクラス変数として扱われてしまうデータクラスの挙動（出力が1になるひっかけ問題等）を再現するため、型ヒントを厳格に付与したフィールドと、意図的な定数クラス変数を明確に区別して設計する。

**使用技術：**

* `dataclass (frozen=True)`、型ヒント（`str | float`）

---

## SpotifyClient (`src/track_element_app/services/spotify_client.py`)

**役割：** Spotify APIとの低レイヤー通信の実行
**責務：**

* `Spotipy` を用いた認証（OAuth 2.0フロー）およびアクセストークンの管理。
* ユーザーの直近の再生履歴（50曲）や、指定したアーティストの関連アーティスト（影響を受けた/似ている）情報のAPI取得。
* **★試験対策の埋め込み：** 将来的なAPI非同期一括取得を見据え、非同期ジェネレータにおいて `anext()` 単体ではコルーチンを返すだけであり、値の評価には `await anext(gen)` が必須であるルールのシミュレーションロジックを配置する。

**使用技術：**

* `spotipy`、非同期ジェネレータ（`async generator`）

---

## TrackAnalyzer (`src/track_element_app/services/track_analyzer.py`)

**役割：** 音楽成分のデータ分析およびDJ選曲ロジックの実行
**責務：**

* `Pandas` を用いて、取得した楽曲データを DataFrame に変換・一括処理する。
* 1曲目（静かな曲）から最後の曲（激しい曲）に向かって、Energy の数値がなだらかに右肩上がりに並ぶ「フェードイン・選曲ロジック」を実装。
* 1970〜80年代の古い名曲をフィルタリングする「タイムトラベル選曲ロジック」を実装。
* **★試験対策の埋め込み：** 大量トラック候補の処理において、「ジェネレータと `len()` での `TypeError`」「巨大データと `list()` 化による `MemoryError` リスク」「アスタリスクを使った残余引数のアンパック（1つの代入文に `*` は1つ、要素数不一致での `ValueError`）」を内部ロジックの動作境界として仕込む。
* `SpotifyClient` を内部に保持する設計とし、継承（is-a）より委譲・コンポジション（has-a）を最優先する（CarがEngineインスタンスを保持するのと同様の設計）。

**使用技術：**

* `pandas`

---

## CacheRepository (`src/track_element_app/utils/cache_repository.py`)

**役割：** ローカルキャッシュ（JSON）および設定ファイルの管理
**責務：**

* `pathlib.Path` を用いた、API取得データのローカルキャッシュ保存・読み込み。
* **★試験対策の埋め込み：** `Path.parts` はプロパティのため `()` をつけると `TypeError` になる罠や、`len(Path.parents)` の要素数ルールの挙動をパス操作コード内に埋め込む。

**使用技術：**

* `pathlib`、`json`

---

## TrackElementApp (`src/track_element_app/main.py`)

**役割：** アプリケーション全体の中央制御（DI・責務分離）
**責務：**

* 各種サービス（`SpotifyClient`, `TrackAnalyzer`, `CacheRepository`）のインスタンスを管理し、コンポジションを構築する。
* GUIからのイベント（分析開始ボタン押下など）を受け取り、ビジネスロジックを実行してUI側に結果を返す。

---

## TrackElementGui (`src/track_element_app/gui/app.py`)

**役割：** ユーザーインターフェース（画面描画とグラフ可視化）
**責務：**

* `Streamlit` を用いたWeb UIの描画（認証ボタン、スライダー、選曲ロジック選択、書き出しボタン）。
* `Plotly` を用いて、分析された音楽成分をレーダーチャートや散布図として画面上にオシャレに描画する。
* **★試験対策の埋め込み：** 入力されたAPIスコープ文字列の検証や、画面へのトースト通知処理、および `f-string` によるフォーマット安全性の検証。

**使用技術：**

* `Streamlit`、`Plotly`
