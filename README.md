# linctra-room

《鏈次元》(linctra.io) 房間設計檔的發佈來源。

- `map.json` — 房間內容，schemaVersion 1.0
- `logo.webp` — 首頁卡片縮圖（選用）

平台會在玩家每次進入房間時，以 `cache: 'no-store'` 直接讀取本站的 `map.json`，
所以更新這個檔案即可讓房間同步，不需要重新提交。

> 此 repo 為公開發佈用途，只放上述檔案，不存放任何其他程式碼或設定。
