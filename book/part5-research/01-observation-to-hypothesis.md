# 5.1 從觀察到假說

## 場景

跑一次 `auto_detect_candidates.py --ohlcv /path/to/ohlcv.parquet --output-dir reports/edge_candidate_auto --top-n 10`，`edge-candidate-agent` 的輸出資料夾裡會多出幾樣東西：一份 `daily_report.md`、一份 `market_summary.json`、一份 `anomalies.json`、一份 `watchlist.csv`，還有 `tickets/` 底下分裝的兩個籃子——`exportable/` 和 `research_only/`。SKILL.md 沒有承諾這些檔案裡有哪一筆已經是「機會」；它承諾的只是今天的 EOD OHLCV 掃出來、還沒被驗證過的異常清單。

`edge-hint-extractor` 接手的方式更窄。`build_hints.py --market-summary .../market_summary.json --anomalies .../anomalies.json --output-dir reports/` 把這兩份 JSON（外加可選的 `news_reactions.csv`）讀進去，吐出一份 `hints.yaml`：一個 `title`、一句 `observation`，外加一串幾乎全部標成 optional 的欄位。走到這一步，產出裡仍然沒有一個欄位負責回答「該不該買」。SKILL.md 另外開了兩條增豐路——`--llm-ideas-cmd` 把資料丟給外部 LLM CLI，或 `--llm-ideas-file` 讀一份人工先寫好的 YAML；兩者互斥，只能二選一。規則式的 hint 永遠先跑一輪，LLM 只負責疊加，不負責取代。

同一個「今天觀察到什麼」的問題，`trade-hypothesis-ideator` 選了另一個入口。它不吃 `market_summary.json`，也不吃 `hints.yaml`；SKILL.md 的 Prerequisites 只寫了一句：輸入是一包 JSON bundle，裡面至少包含 `trade_log`、`journal_snippets`、`market_data`、`observations` 四類之一或多類。同一個時間點，這個 skill 從交易日誌與筆記本問起，而不是從 OHLCV 掃描問起。

## 方法論

「觀察」到「假說」之間，這三個 skill 都刻意留了一道縫，只是填縫的方向分兩派。

`edge-candidate-agent` 與 `edge-hint-extractor` 這一派由下而上：先讓程式不帶立場地掃過 EOD OHLCV，找出統計上「不對勁」的地方，`hypothesis_type` 這種帶著交易邏輯味道的標籤要到後面才登場，而且還是 optional。SKILL.md 把 `edge-hint-extractor` 的位置寫得很明白——它是 split workflow 裡的第一站，`observe -> abstract -> design -> pipeline` 四階段裡的 `observe`。它產出的 `hints.yaml` 還不是終點，下一步在 5.2，換 `edge-concept-synthesizer` 接手。

`trade-hypothesis-ideator` 這一派反過來，由上而下：先有既有的 `trade_log`、`journal_snippets` 或 `market_data`，經兩趟 pass 正規化、批判、排序，才收斂成假說卡。它的 description 用一個詞把終點寫死——`falsifiable trade strategy hypotheses`，可否證的交易策略假說——比 `hints.yaml` 往前多跨了一步：帶著實驗設計與 kill criteria。

兩派在 `skills-index.yaml` 裡站在不同抽屜：`edge-candidate-agent`、`edge-hint-extractor` 都是 `category: strategy-research`；`trade-hypothesis-ideator` 是 `category: trade-memory`。分類不是巧合——`trade-hypothesis-ideator` 的 SKILL.md 定義的輸入，原本就不是 `market_summary.json` 或 `anomalies.json`。這是「觀察到假說」同一個問題的兩份獨立答案，不是同一條管線先後相接的兩個工位。

## 機制

先看 `edge-candidate-agent` 這條線怎麼決定一張 ticket 能不能往下走。`research_ticket_schema.md` 只要求三個必填欄位——`id`、`hypothesis_type`、`entry_family`——而 `entry_family` 只認兩個值：`pivot_breakout` 或 `gap_up_continuation`。剩下一長串都是 Optional Fields：`name`、`description`、`mechanism_tag`、`regime`、`holding_horizon`、`universe`、`data`、`entry`、`exit`、`risk`、`cost_model`、`promotion_gates`、對應 entry_family 的 `detection.vcp_detection` 或 `detection.gap_up_detection`，還有 `strategy_overrides`。這些欄位決定的是策略草稿會長什麼樣子，不是這一步要不要成立——必填的三個欄位才是。`signal_mapping.md` 把門檻攤成一張表：8 種 `hypothesis_type` 裡，只有 `breakout`（配 `pivot_breakout`，還得帶 `vcp_detection` 區塊）與 `earnings_drift`（配 `gap_up_continuation`，Phase I 要避開 walk-forward）算 exportable；剩下 `momentum`、`pullback`、`sector_x_stock`、`panic_reversal`、`low_vol_quality`、`regime_shift` 六種一律 research-only——規則寫得直接：research-only 就不產生 `strategy.yaml`，先留在 `tickets/research_only/`，排隊等未來的介面版本擴充。

`hints.yaml` 的 canonical 形狀比 ticket 鬆得多。`hints_schema.md` 定的骨架是 `generated_at_utc`、`as_of`、一段 `meta`（`rule_hints`、`llm_hints`、`total_hints`、`regime`），底下才是 `hints` 陣列，每一筆只有 `title` 與 `observation` 是必填，`hypothesis_type`、`preferred_entry_family`、`symbols`、`regime_bias`、`mechanism_tag` 全部 optional。`hypothesis_type` 就算填了也不一定算數——文件寫明它先被拿去跟 `title`、`observation` 做關鍵字比對，比對不上才落回一個統一的預設標籤 `research_hypothesis`，用在 `--promote-hints` 開啟時的分群。值得一提的是，`hints_schema.md` 認得的 8 個 `hypothesis_type` 值——`breakout`、`earnings_drift`、`news_reaction`、`futures_trigger`、`calendar_anomaly`、`panic_reversal`、`regime_shift`、`sector_x_stock`——跟 `signal_mapping.md` 那張表只有五項重疊；`news_reaction`、`futures_trigger`、`calendar_anomaly` 這三個在 ticket 端的匯出表裡完全找不到對應列。觀察階段的詞彙，本來就比交易邏輯階段的詞彙寬。

`--llm-ideas-cmd` 走的是一份寫死的契約：`build_hints.py` 把 `as_of`、`market_summary`、`anomalies`、`news_reactions` 和一句 `instruction` 打包成 JSON 送進外部指令的 stdin，對方只要印出一個陣列或一個帶 `hints` 鍵的物件就算合格。契約定得越死，換一個 LLM 供應商也不怕整條線跟著斷掉。

`trade-hypothesis-ideator` 的機制是兩趟跑法。Pass 1 把輸入 bundle 正規化、抽出證據摘要；Pass 2 才真正生成 1 到 5 張假說卡，逐一送進 critique prompt 批判，再排序、貼上 `pursue`、`revise`、`discard` 三種判決之一。每張卡背後的佐證，`evidence_quality_guide.md` 分成三級：`High` 級要有驗證過的交易紀錄、可重現的回測輸出，或可稽核的成交紀錄；`Medium` 級是有明確結果的結構化筆記，或反覆出現的圖表觀察；`Low` 級是一次性的軼事、沒有約束力的直覺，或無法重現的截圖。checklist 還有一條硬性規定：kill criteria 至少要包含一個可否證的反向條件，缺了這條，這張卡通不過。判成 `pursue` 的卡，才能選擇性地經由 Step H strategy exporter 匯出成 `strategy_<hypothesis_id>.yaml`；`hypothesis_types.md` 把類型對應到 entry_family 分三組——`breakout` 對 `pivot_breakout`；`earnings_drift` 與 `gap_continuation` 兩個標籤共用 `gap_up_continuation`；`momentum`、`pullback`、`regime_shift` 一律 `research_only`——另外還點名第七個標籤 `gap_open_scored`，註明在 v2 支援之前同樣是 research-only。

## 判讀與誤用

三個 skill 有一條共同的紅線：optional 欄位不是「隨便填」，是「沒填也合法」。`hints.yaml` 裡一筆沒帶 `hypothesis_type` 的 hint，不代表它比較弱，只代表這條觀察還沒被貼上交易邏輯；如果哪個下游流程因為欄位缺失就把它直接丟掉，那是誤讀了這份 schema 的設計意圖。

`hypothesis_type` 落回 `research_hypothesis` 的那條退路，也容易被誤讀成「這筆觀察沒有價值」。schema 的原意是反過來的：它是給貼不上既有標籤、但仍要參與後續分群的觀察留一個位子，不讓一個無法歸類的異常直接從流程裡消失。

最容易踩的坑，是把 `edge-candidate-agent`／`edge-hint-extractor` 這條 EOD 掃描線，跟 `trade-hypothesis-ideator` 這條假說卡線，當成同一條管線的前後兩段來讀。兩者的分類、輸入 schema 都不一樣，`hints.yaml` 也從未出現在 `trade-hypothesis-ideator` 的 SKILL.md 輸入清單裡。真正把它們接上同一個下游的，只有一件事：兩邊各自判成可匯出的結果，最終都收斂進同一個 `interface_version: edge-finder-candidate/v1`——`trade-hypothesis-ideator` 的 SKILL.md 自己這樣寫，`export_candidate.py` 產生的 `metadata.json` 用的也是這個版號。介面相同，不代表管線相同。

`edge-candidate-agent` 的 Guardrails 另外訂了兩條前置門檻：candidate 的資料夾名稱如果跟 ticket 裡的 `id` 對不上，直接拒絕；凡是違反 schema 邊界——風險參數、出場條件、空條件——同樣拒絕。SKILL.md 還補了一句操作提醒：進 pipeline 前先用 `--dry-run` 跑一次，別讓第一次執行就是全量執行。

最後一條紅線最硬：不管走哪一條路，這一步的產出都還不是策略，更不是訂單。`tickets/research_only/` 裡的東西按規則不准生成 `strategy.yaml`；`hypothesis_cards_<date>.json` 裡標成 `revise` 或 `discard` 的卡也一樣出不了場。就算判成 `pursue`，或落進了 `tickets/exportable/`，接下來要走的也是 5.2 的 `edge-concept-synthesizer` 與 `edge-strategy-designer`，離真正能被審查的策略草稿還有一整章的距離。

## 延伸閱讀

- [`skills/edge-candidate-agent/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-candidate-agent/SKILL.md)
- [`skills/edge-candidate-agent/references/research_ticket_schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-candidate-agent/references/research_ticket_schema.md)
- [`skills/edge-candidate-agent/references/signal_mapping.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-candidate-agent/references/signal_mapping.md)
- [`skills/edge-hint-extractor/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-hint-extractor/SKILL.md)
- [`skills/edge-hint-extractor/references/hints_schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-hint-extractor/references/hints_schema.md)
- [`skills/trade-hypothesis-ideator/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-hypothesis-ideator/SKILL.md)
- [`skills/trade-hypothesis-ideator/references/hypothesis_types.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-hypothesis-ideator/references/hypothesis_types.md)
- [`skills/trade-hypothesis-ideator/references/evidence_quality_guide.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-hypothesis-ideator/references/evidence_quality_guide.md)
