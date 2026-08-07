# 開場：週一 06:30

市場還沒開。Agent 那天做的第一件事，不是找股票，是先問自己一個問題：今天能不能冒新的風險。

上游把這件事寫成一條叫 [`market-regime-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml) 的 workflow。它的 `when_to_run` 圈了一個很窄的時間窗：開盤之前，或者開盤後的頭三十分鐘以內——過了這個窗口，這一步的意義就打了折扣。它的 `when_not_to_run` 則劃了一條更硬的線：輸出不能當成獨立的買賣訊號來用。這條 workflow 給的是一個**姿態**（`allow` / `restrict` / `cash-priority`），不是「買這一檔」的指令。這個分寸，是第一部要立的第一根柱子。

`manual_review` 清單把後果也寫死了：姿態一旦偏向限制，就把第二部的 `swing-opportunity-daily` 往後延，而不是硬湊出一筆交易來配合原本的計畫。今天能不能做，答案有時候就是不能——而這是一個合法的答案，不是流程卡住。

## 本部地圖

第一部借這條 workflow 的四個步驟定調，但五節之中只有三節真的對應到步驟，其餘兩節是刻意補上的背景。

**1.1 市場的心跳：廣度與參與度**——每天都要量。`market-breadth-analyzer` 與 `uptrend-analyzer` 是 workflow 裡兩個必經步驟，沒有 `optional` 標記，也都不是閘門，只負責把今天的證據攤開來。

**1.2 頂部的三種徵兆**——風險升溫時才展開。對應的是 workflow 唯一標成 `optional: true` 的第 3 步 `market-top-detector`：不查，流程照樣往下走，只是第 4 步的判斷會少一份輸入。

**1.3 底部的確認訊號：FTD**——修正過後才用得上。這一節談的內容不在 `market-regime-daily` 的四個步驟裡；它是第一部另外準備的背景判讀，屬於行情已經跌深之後才會打開的工具。

**1.4 更長的視野：宏觀 regime 與泡沫**——拉遠到週的尺度。`macro-regime-detector` 只出現在這條 workflow 的 `optional_skills` 清單裡，本身沒有被排進任何一個步驟——它是備援視角，不是每天必查的證據來源。

**1.5 收斂成一個姿態**——每天的終點，也是每天必經之處。第 4 步 `exposure-coach` 把前面的證據收成一句判斷；整條 workflow 裡，只有這一步的 `decision_gate` 標成 `true`。它要回答的 `decision_question` 只有一個：以今天的廣度、參與度與頂部風險，新的波段風險該是 `allow`、`restrict`，還是 `cash-priority`。

頭尾兩節每天都要走完；1.2 到 1.4 是視情況才打開的背景知識，不是每天的固定動作。

`exposure_decision` 這個 artifact 的 `downstream_hints` 只指向一個地方——`swing-opportunity-daily`。姿態一旦定案，第二部才有資格接手，去問下一個問題：不是「今天能不能做」，是「該做什麼」。
