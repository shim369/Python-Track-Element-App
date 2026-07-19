# 画面遷移図

```mermaid
flowchart TD
    A[メイン画面: Spotify Library Recent]
    A -->|ボタン押下| B[SpotifyClient: 過去50曲取得]
    B --> C[結果: 追加日順にソート]
    C -->|hx_target挿入| D[結果テーブルをUIへ描画]
```
