# 開場：盤後與週末

某個星期三下午，一筆單子平倉了——賺錢的單。開盤前闖過的三道閘、五路偵查隊選出的標的、風控算出的部位，全部在這一刻兌現成一個具體數字。而 Agent 接下來要做的第一件事，不是核對賺了多少，也不是慶祝，是打開一輪檢討。

[`trade-memory-loop`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/trade-memory-loop.yaml) 的節奏跟前三部不一樣：不是每天固定跑一次，是每一次平倉才觸發，`estimated_minutes` 只抓了 30 分鐘，`api_profile` 是最省錢的那一檔。五個步驟裡，`required_skills` 只有兩個——`trader-memory-core` 與 `signal-postmortem`；`trade-performance-coach` 與 `backtest-expert` 都在 `optional_skills` 之列。強制的部分小得驚人：記錄結果、分類原因。要不要再往下深挖，是選擇題。

更值得留意的是五個 artifact 的去向。`closed_thesis_record` 與 `backtest_validation` 只在這條 workflow 裡打轉；其餘三個——`postmortem_findings`、`performance_coach_report`、`next_session_operating_rules`——連同最後的 `lessons_log_entry`，`downstream_hints` 全部指向同一個地方：`monthly-performance-review`。第一到三部的判斷大多在同一天內兌現；第四部產出的東西，要等到月初那個週末才會被再打開來看一次。

## 本部地圖

**4.1 論點的生命週期**——從論點被登記的那一刻算起（3.1 節提過，那個數字之後會被原樣核對一次），走到第 1 步，`trader-memory-core` 把結果收斂成 `closed_thesis_record`。`decision_gate` 是 `false`：這一步不判斷，只記錄——論點的生命週期，到這裡才算真正閉合。

**4.2 誠實的事後檢討**——對應第 2 步，`signal-postmortem`，`decision_gate: true`。要回答的只有一個問題：結果的根本原因，是論點品質、是執行、是市場環境，還是隨機性？四個選項並列，隨機性也在其中——這一節要講的，正是為什麼承認「純粹運氣」也是一種誠實。

**4.3 教練看的是行為不是損益**——對應可選的第 3 步，`trade-performance-coach`，同樣是決策閘。它的 `decision_question` 問的不是這筆賺了或虧了多少，而是下一個交易時段的操作規則該採用、修改、保留，還是只記錄不執行。兩份輸出都流向月度總結——教練看的是行為模式，不是單筆損益。

**4.4 模型書：把熟練度變成資料**——收尾的兩步。可選的第 4 步讓 `backtest-expert` 回頭重驗原本的假說；必經的第 5 步，`trader-memory-core` 把整輪檢討追加成 `lessons_log_entry`。一次平倉、一次分類、一次記錄，單看不起眼；持續寫進同一本帳，熟練度才有機會變成看得見的資料。

實作章會把這五個步驟接在某個星期三的平倉之後，實際跑一遍。

第一到三部做的是同一件事：判斷該不該冒一筆風險、冒多大。第四部從這裡往前一步，把已經發生的交易變成可以複用的經驗；第五部再把這些經驗變成新的工具。
