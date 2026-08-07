# 3.3 三道閘門的 fail-closed 哲學

## 場景

連兩天虧損後的早晨，`swing-opportunity-daily.yaml` 的交棒才剛開始。第 2 步的 `vcp-screener` 什麼都還沒跑，Agent 卻已經先停在第 1 步前面——`decision_question` 只問一句：今天，`circuit_breaker_decision` 是不是 `TRADING_ALLOWED`？昨天、前天各自收了一筆虧損之後，這已經不是形式問題。答案如果是 `COOLDOWN` 或 `HALTED`，今天的 `swing-opportunity-daily` 到此為止——不是「篩選結果比較保守」，是連第 2 步的篩選器都不會被叫起來。

這不是這一週遇到的第一道閘門。更早，`market-regime-daily` 第 4 步的 `exposure-coach` 已經替今天整個交易日回答過一次更寬的問題——市場環境本身容不容得下新風險（1.5 節）。第 1 步的斷路器問的是同一天，但範圍窄了一圈：不管市場多友善，這個帳戶自己，禁不禁得起再冒一次險。

就算第 1 步放行，`vcp-screener` 篩出候選、`technical-analyst` 在週線圖上核可了結構（3.2 節）、`position-sizer` 算出股數（3.1 節）、`trader-memory-core` 把論點寫進 `candidate_journal_entry`——十步都跑完了，`swing-opportunity-daily` 還是沒有讓 Agent 按下去。第 11 步，`pre-trade-discipline-gate`，又問了一次，這次問的既不是市場也不是帳戶，是這一張具體的訂單本身。

三道閘門，各自守著不同的東西，卻共用同一種設計脾氣：資訊不明朗的時候，寧可什麼都不做。

## 方法論

「Fail-closed」不是這三個 skill 共用的口號，而是各自用不同方式落實的同一個選擇：輸入不完整、或訊號互相矛盾時，系統的預設輸出不是「假設沒事、繼續往下走」，而是「先擋下來」。1.5 節已經在 `exposure-coach` 身上看過這個選擇的第一種形式——Safety First 原則要求輸入不完整或衝突時，預設更低的曝險。斷路器與紀律閘門把同一套哲學，分別套進帳戶層與行為層。

`drawdown-circuit-breaker/references/circuit_breaker_framework.md` 一開頭就把自己定位成 `exposure-coach` 的交易者側對應版本：exposure-coach 問的是市場環境准不准新曝險，斷路器問的是交易者自己已實現的帳戶損傷，准不准再冒一次新風險。它只讀 trader-memory-core 的 thesis YAML，四條規則各自守一個時間窗，數字全部寫死在 `references/circuit_breaker_framework.md` 的預設表裡：單日已實現虧損達帳戶 2.0%，觸發 `HALTED`，下一個美東交易日解除；連續兩筆終局虧損（`outcome.pnl_dollars` 為負）觸發 `COOLDOWN`，距最近一次虧損出場滿 24 小時解除；週度已實現虧損達帳戶 5.0%，觸發 `HALTED`，下週一美東時間解除；月度已實現虧損達帳戶 8.0%，觸發 `HALTED`，下個月第一天美東時間解除。多條規則同時觸發，回傳最嚴格的那個狀態：`HALTED` 排第一、`COOLDOWN` 第二、`TRADING_ALLOWED` 最後——跟 3.1 節部位計算裡「三個候選股數取最小值」是同一套邏輯，最保守的結果永遠勝出。文件另外註明一個容易被忽略的細節：損益兩平算作獲勝，這跟 trader-memory-core 月度回顧的分類標準一致（`pnl >= 0` 記勝）。

`pre-trade-discipline-gate` 守的是完全不同的一層——不是市場、不是帳戶，是下單這個動作本身有沒有紀律。它的 `decision_question` 把六類檢查寫得很白：書面計畫（written-plan）、預先設定的停損（predefined-stop）、部位大小（position-size）、近期虧損（recent-loss）、市場 regime、斷路器。對應到 `discipline_gate_framework.md` 的 Blocking Rules，一個 actionable 候選只要踩中以下任一項，就判 `NO_GO`：`entry_in_written_plan` 不是 `true`、`stop_predefined` 不是 `true`、`size_within_plan` 不是 `true`、`actual_risk_dollars` 超過 `planned_risk_dollars`、報復性交易冷卻窗內出現過虧損或部分平倉、市場 regime 判定是 `REDUCE_ONLY` 或 `CASH_PRIORITY`、斷路器判定是 `COOLDOWN`、`HALTED`，或 `TRADING_HALTED`。只有真正打算下單的意圖才會被這道閘門攔——`ENTRY_READY`、`ACTIONABLE`、`ACTIONABLE_DAY1`、`MANUAL_ORDER` 四種算 actionable；`WATCHLIST`、`DELAYED_EP_WATCH`、`PEAD_HANDOFF`、`IGNORE`、`REJECTED` 五種只會被記錄，不構成下單許可，整批都是這幾種意圖時，輸出直接是 `NO_ACTIONABLE_ORDERS`。

## 機制

兩個 skill 有個共同結構，跟 3.1 節看到的 `position-sizer` 與 `futures-position-sizer` 一樣：都只讀本地的 trader-memory-core thesis YAML（`state/theses/` 底下的 `th_*.yaml`），不叫任何付費 API，純計算、離線可跑。

斷路器的輸出帶一個 `data_quality` 欄位，三種取值分得很細：`OK` 是狀態目錄存在、每個 thesis 檔都正常讀出、沒有任何格式錯誤或衝突的紀錄被跳過；`EMPTY_STATE` 是狀態目錄根本不存在、或裡面沒有任何 `th_*.yaml` 檔案——這種情況回傳 `TRADING_ALLOWED`，理由寫得直接：不該讓一個還沒有交易紀錄的新使用者被「沒有歷史」這件事擋下來；`PARTIAL` 才是真正觸發 fail-closed 的那一種——只要有一筆 ledger 紀錄或終局結果被跳過、格式錯誤、非有限值，或跟另一個來源的損益數字衝突，就回傳 `HALTED`，加一條 `incomplete_state_data` 規則，`active_until` 是 `null`：不是等一段時間自動解除，而是要求先修好資料、重新跑一次才能解除。唯一可回復的例外，是一筆遺留（legacy）thesis 沒有 realized-P&L 的 ledger 紀錄，但終局的 `outcome.pnl_dollars` 是有限值——這種情況仍標成 `PARTIAL`，留給稽核看見，但不會單獨強迫整體判定變成 `HALTED`。這正是上游最近一次修正（fail closed on incomplete state）落地後的行為：「沒有資料」跟「資料有問題」被刻意分開處理——前者不擋新人，後者才是真正要 fail-closed 的地方。

紀律閘門在 workflow 裡卡在第 11 步，`consumes` 明確列了四個同一條 workflow 內產出的 artifact：第 10 步 `trader-memory-core` 寫的 `candidate_journal_entry`、第 8 步 `position-sizer` 寫的 `position_sizing`、第 9 步（optional）`breakout-trade-planner` 寫的 `trade_plans`，以及第 1 步斷路器自己的 `circuit_breaker_decision`。市場側的 `exposure_decision` 沒有出現在這份 `consumes` 清單裡——不是被遺漏，是因為它來自另一條 workflow（`market-regime-daily`），而 workflow schema 的驗證規則只允許 `consumes` 引用同一條 workflow 裡更早步驟產出的 artifact；`exposure_decision` 因此改用明確路徑傳給 CLI，不走 `consumes` 欄位，但它仍然是紀律閘門六類檢查裡「市場 regime」那一項要核對的輸入。決策本身分四級，`discipline_gate_framework.md` 排出明確順位：`GO` 最高，`NO_ACTIONABLE_ORDERS` 其次，`REVIEW_REQUIRED` 再次，`NO_GO` 最低——`NO_GO` 故意排在 `REVIEW_REQUIRED` 之下，讓「明確違規」永遠蓋過「另一個候選只是需要複核」，不會被沖淡成一個中性的「再看看」。缺失或讀不到的上游 artifact（比如斷路器報告檔案根本沒生成）不會被直接判成 `NO_GO`，而是 `REVIEW_REQUIRED`——這道閘門刻意把「不知道」和「知道而且結果不好」分開對待，只有真正讀到 `COOLDOWN`、`HALTED`、`REDUCE_ONLY`、`CASH_PRIORITY` 這些明確的壞結果，才會判 `NO_GO`。

順序本身就是設計。斷路器卡在第 1 步，比第 2 步的篩選器早一步——它擋下的是「今天根本不該冒新風險」，一旦判定不是 `TRADING_ALLOWED`，後面 `vcp-screener` 篩選、`technical-analyst` 讀圖、`position-sizer` 算股數這些工作全部不用做，省下的是整個下午的分析成本。紀律閘門卡在第 11 步，晚了整整十步——它要擋的不是「今天」，是「這一筆、此刻、這個數字」：書面計畫是否真的跟最後要下的單一致、寫論點之後有沒有又發生一次新的虧損（斷路器的判定可能在這十步之間變過）、這張單是不是報復性交易的樣子。一個閘門省的是分析力氣，另一個閘門守的是最後一次按鈕之前，一切是否仍然吻合原本寫下的計畫。

## 判讀與誤用

三道閘門各自算出一個明確的 verdict——`exposure_decision`、`circuit_breaker_decision`、`pre_trade_discipline_decision`——但沒有一個 verdict 真正攔得住訂單。斷路器 SKILL.md 把這件事寫得毫不含糊：「The circuit breaker is a recommendation and recordkeeping tool. It does not replace human judgment, and it does not enforce broker-side blocks or automated order rejection.」紀律閘門同樣寫明：「The gate is intentionally offline. It does not place orders, cancel orders, call a broker API, or fetch market data.」——它的核心原則第一條就是「Manual execution only」：輸出是下單前的檢查表，不是訂單路由器。workflow schema 裡 `decision_gate: true` 這個標記，驗證器只要求它必須帶一句非空的 `decision_question`；它不是一個會讓程式停下來的開關，只是提醒 Claude 與交易者：這一步，有一個問題必須主動回答。

這正是序章與 1.5 節已經定調、這一節只是把它攤在三道閘門並排看一次的事實：verdict 是 script 算出來的——`TRADING_ALLOWED`、`GO`／`NO-GO` 都是程式輸出，可稽核、可重複；執行是人守出來的——沒有任何程式碼攔得住一個決心無視 verdict 下單的人。`swing-opportunity-daily.yaml` 的 `exposure_decision` 甚至連 `decision_gate` 這個標記都沒有，只在 `prerequisite_workflows` 底下用一句註解承認：順序有沒有被遵守，驗證器不檢查，是交易者自己的責任。

覆寫閘門的誘惑，通常不是明著跟系統對著幹，而是說服自己「這次不一樣」——連兩天虧損之後，正是最容易想繞過斷路器 `COOLDOWN` 去扳回一城的時候，而這正是斷路器與紀律閘門的 revenge window 檢查要攔的那種交易。代價不是單筆虧損放大這麼簡單：斷路器存在的理由是「Survival first」——防止虧損後的風險升級；紀律閘門的「Written plan first」原則說得同樣直接：沒有書面進場計畫、沒有預先設定的停損、沒有確認過的部位大小，就不該有手動進場。繞過任何一道，等於把前面十步做的分析、驗證、記錄工作，在最後一刻讓一個未經核對的決定推翻。`manual_review` 清單把這條紀律寫成最後一句明文：「Confirm pre_trade_discipline_decision is GO before placing any manual broker order.」——GO 之前不下單，是整章唯一不留模糊空間的一句話。

## 延伸閱讀

- [`skills/drawdown-circuit-breaker/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/drawdown-circuit-breaker/SKILL.md)
- [`skills/drawdown-circuit-breaker/references/circuit_breaker_framework.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/drawdown-circuit-breaker/references/circuit_breaker_framework.md)
- [`skills/pre-trade-discipline-gate/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/pre-trade-discipline-gate/SKILL.md)
- [`skills/pre-trade-discipline-gate/references/discipline_gate_framework.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/pre-trade-discipline-gate/references/discipline_gate_framework.md)
- [`workflows/swing-opportunity-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml)
