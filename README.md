# linctra-room

《鏈次元》(linctra.io) 房間設計檔的發佈來源。

## 檔案

| 檔案 | 用途 |
|---|---|
| `map.json` | 房間內容，schemaVersion 1.0 |
| `chart-ada.png` | ADA 腿資金曲線 |
| `chart-btc.png` | BTC 腿資金曲線 |
| `chart-combo.png` | 組合資金曲線（30/70，每月再平衡）|
| `chart-verify.png` | TradingView ↔ Python 逐筆對帳 |
| `logo.webp` | 首頁卡片縮圖（選用）|

平台會在玩家每次進入房間時，以 `cache: 'no-store'` 直接讀取本站的 `map.json`，
牆上的圖則由 `map.json` 內的絕對網址載入。所以更新這些檔案即可讓房間同步，
不需要重新提交。

## 資料口徑

資金曲線採 Python 實戰引擎，**已扣除永續合約資金費與滑點**。
TradingView 無法模擬資金費，其顯示數字會較高——這裡刻意採用較保守的那一組。

`chart-verify.png` 比對的是同一套策略的兩個獨立實作：TradingView 的 Pine 腳本
與 Python 引擎。147 筆交易中對上 145 筆（98.6%），方向 100% 一致，
進場價平均誤差 0.0587%。

## 這個 repo 的紀律

- `.gitignore` 採**白名單**：預設忽略一切，只放行上述檔案。
  這是結構性防護，避免策略程式碼、參數、金鑰被誤 commit 進這個公開 repo。
- `map.json` 只含**績效結果**，不含任何策略參數（均線、ADX、停損停利、容差、槓桿）。
- **不放** API 金鑰、錢包連接物件、轉帳入口、邀請碼。
  金鑰類的東西沒有例外：這個 repo 是公開的，而 git 歷史是永久的。
