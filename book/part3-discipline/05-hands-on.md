# 實作：swing-opportunity-daily（閘門段）

09:25，README 開場已經交代過桌面——`vcp_candidates` 篩出來了，`validated_setups` 通過了週線驗證，`position_sizing` 也算出了股數。這一章不再談方法論，直接把 `swing-opportunity-daily.yaml` 的閘門段跑一遍：第 1 步的斷路器、第 7 步的圖表決策閘、第 8 步的部位計算、第 9 步（optional）的進場計畫、第 10 步的論點登記、第 11 步的紀律閘門——一路走到今天這一筆的 `GO` 或 `NO-GO`。第 2 步的 `vcp-screener`（以及 3–6 步的其他篩子）屬於第二部的篇幅，這裡只帶過一句：篩選段產出的 `vcp_candidates` JSON，是本章第 9、10 步指令裡 `--input` 吃進去的那份檔案。

## 兩種跑法

**(a) 在 Claude Code 對話中觸發。** 每一步都能用一句話描述今天想確認的事：
- 「我這個帳戶今天還能不能冒新風險」→ `drawdown-circuit-breaker`
- 上傳週線圖，「這檔的結構乾不乾淨，能不能進 position sizing」→ `technical-analyst`（純圖表判讀，見 3.2 節）
- 「這筆進場 155、停損 148.50，帳戶 10 萬，該買幾股」→ `position-sizer`
- 「幫這批 VCP 候選生成突破進場計畫」→ `breakout-trade-planner`
- 「把這個候選寫進投資論點」→ `trader-memory-core`
- 「下單前最後檢查一次紀律清單」→ `pre-trade-discipline-gate`

**(b) 直接執行 script。** 下面六條指令，逐一對照六支 script 的 `--help` 輸出核對過旗標；技術分析師的一支例外——原因見 Step 7。

## 閘門段 checklist

**Step 1・斷路器**（`decision_gate: true`，決策問題：今天新風險，`circuit_breaker_decision` 是不是 `TRADING_ALLOWED`？）
```bash
python3 skills/drawdown-circuit-breaker/scripts/check_circuit_breaker.py \
  --state-dir state/theses \
  --account-size 100000 \
  --output-dir reports/
```
`--state-dir` 預設就是 `state/theses`、`--output-dir` 預設就是 `reports/`，兩個旗標其實可以省略，這裡照 SKILL.md 慣例寫出來。產出：`reports/circuit_breaker_decision_<timestamp>.json` 與同名 `.md`。非 `TRADING_ALLOWED` 就此打住，第 2 步的篩選器不會被叫起來。

**Step 7・圖表決策閘**（`decision_gate: true`，決策問題：哪些候選有乾淨的週線結構、通過人工複核？）這一步在 `swing-opportunity-daily` 裡沒有 CLI——主路徑是把候選的週線圖上傳給 Claude，走 3.2 節說過的純圖表判讀，沒有腳本會替它決定。`technical-analyst` 唯一的 script `check_weekly_price_action.py` 屬於另一個附加模式（Shapiro Step 3 逆勢確認），跟這一步的候選驗證無關，但作為「沒圖時的稽核備援」值得先記住呼叫方式：
```bash
python3 skills/technical-analyst/scripts/check_weekly_price_action.py \
  --symbol BT --direction CROWDED_LONG --as-of 2026-07-15 \
  --output-dir reports/
```
這支 script 需要 `FMP_API_KEY`（或 `--api-key`）抓週線 OHLC；本章其餘五步都不需要任何 API key。

**Step 8・部位計算**（`decision_gate: false`）
```bash
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 --entry 155 --stop 148.50 --risk-pct 1.0 \
  --max-position-pct 10 --max-sector-pct 30 --current-sector-exposure 22 \
  --output-dir reports/
```
沿用 3.1 節同一筆交易的數字。產出：`reports/position_sizer_<timestamp>.json` 與 `.md`，寫進 `position_sizing`。

**Step 9・進場計畫（optional）**
```bash
python3 skills/breakout-trade-planner/scripts/plan_breakout_trades.py \
  --input reports/vcp_screener_2026-08-07.json \
  --account-size 100000 --risk-pct 0.5 \
  --output-dir reports/
```
`--input` 吃的是第 2 步 `vcp-screener` 的 JSON，不是 step 7 的 `validated_setups` 或 step 8 的 `position_sizing`——這支 script 自帶一套 Minervini Gate 與部位計算，不重讀 `position-sizer` 的輸出。跳過這步不影響第 10、11 步。

**Step 10・登記論點**（`decision_gate: true`，決策問題：每個候選的風險是否與 `position_sizing` 一致、總部位熱度是否在預算內？）
```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py ingest \
  --source vcp-screener \
  --input reports/vcp_screener_2026-08-07.json \
  --state-dir state/theses/
```
註冊出的 thesis 停在 `IDEA`；把 Step 8 的部位算好之後接一步 `attach-position` 掛上去：
```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py store --state-dir state/theses/ \
  attach-position <thesis_id> --report reports/position_sizer_<timestamp>.json
```
`ingest --help` 只要求 `--source` 與 `--input`（或 `--bulk-csv`）二選一，`--state-dir` 是唯一的可選旗標。

**Step 11・紀律閘門**（`decision_gate: true`，決策問題：下單前，每個 actionable 候選是否通過書面計畫、預設停損、部位大小、近期虧損、市場 regime、斷路器六項檢查？）
```bash
python3 skills/pre-trade-discipline-gate/scripts/check_pre_trade_discipline.py \
  --answers-file state/manual-entry-checklist.json \
  --state-dir state/theses \
  --market-regime-decision reports/exposure_decision_latest.json \
  --circuit-breaker-decision reports/circuit_breaker_decision_latest.json \
  --output-dir reports/pre-trade-discipline \
  --journal-dir state/journal/pre-trade-discipline
```
產出：`pre_trade_discipline_decision_<timestamp>.json` 與同名 `.md`，加一筆 JSONL 寫進 `--journal-dir`。

## 前置需求

這一段大多離線可跑：斷路器、部位計算、紀律閘門讀的都是本地 `state/theses/` 或 CLI 參數,不碰任何付費 API。需要 `FMP_API_KEY` 的只有 Step 7 的 script 備援——而它本來就不是這一步的主路徑,跳過不影響其餘五步。`state/theses/` 不用預先手動建立:`trader-memory-core` 的寫入操作(`ingest`、`open-position` 等)與 `check_circuit_breaker.py`、`check_pre_trade_discipline.py` 的 `--output-dir`/`--journal-dir` 都會自己 `mkdir(parents=True, exist_ok=True)`。唯一要注意的是紀律閘門的 `--state-dir` 本身沒有預設值——不傳就等於沒有本地論點可讀,近期虧損(revenge window)檢查會靜靜地找不到任何紀錄,不是報錯,但也等於沒真的查過。

## 產出解讀

`circuit_breaker_decision`(SKILL.md 範例):
```json
{
  "recommendation": "COOLDOWN",
  "triggered_rules": [
    {"rule": "losing_streak_cooldown", "threshold": 2, "observed": 2,
     "active_until": "2026-07-02T15:30:00-04:00"}
  ],
  "data_quality": "OK"
}
```

`position_sizing`(SKILL.md 範例,無額外組合限制時):
```json
{
  "final_recommended_shares": 153,
  "final_position_value": 23715.0,
  "final_risk_dollars": 994.50,
  "final_risk_pct": 0.99,
  "binding_constraint": null
}
```

`pre_trade_discipline_decision`(依 script 實際欄位重建,SKILL.md 未附完整範例):
```json
{
  "overall_decision": "GO",
  "candidate_results": [
    {"symbol": "AAPL", "thesis_id": "th_aapl_gm_20260703_0001",
     "order_intent": "ENTRY_READY", "actionable": true, "decision": "GO",
     "reasons": [], "link_status": "linked"}
  ],
  "metrics": {"candidates_total": 1, "actionable_candidates": 1,
              "theses_scanned": 12, "revenge_window_hours": 24.0},
  "warnings": [],
  "rationale": "All actionable manual-order candidates passed the pre-trade discipline gate."
}
```
`overall_decision` 只有四種值:`GO`、`NO_ACTIONABLE_ORDERS`、`REVIEW_REQUIRED`、`NO_GO`,`NO_GO` 排位在 `REVIEW_REQUIRED` 之上——明確違規永遠蓋過「需要複核」。

## 收尾

`manual_review` 清單裡跟這一段直接相關的三條,親手跑完之後要再對照一次:下單前確認 `circuit_breaker_decision` 是 `TRADING_ALLOWED`;下單前確認 `pre_trade_discipline_decision` 是 `GO`;所有訂單都在券商手動輸入,沒有自動執行。第一條卡在流程最前面,第三條卡在流程最後面,中間五步——不管跑得多順、`validated_setups` 多乾淨、`position_sizing` 算得多精確——沒有一步能替第三條做決定。

跟第一部實作章立的場一樣:這一路六步給出的是可重跑、可稽核的 verdict,不是保證獲利的公式,更不是自動下單的許可。`GO` 之前不下單,是這一部從頭到尾唯一不留模糊空間的一句話。

## 延伸閱讀

- [`skills/drawdown-circuit-breaker/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/drawdown-circuit-breaker/SKILL.md)
- [`skills/technical-analyst/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/technical-analyst/SKILL.md)
- [`skills/position-sizer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/position-sizer/SKILL.md)
- [`skills/breakout-trade-planner/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/breakout-trade-planner/SKILL.md)
- [`skills/trader-memory-core/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trader-memory-core/SKILL.md)
- [`skills/pre-trade-discipline-gate/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/pre-trade-discipline-gate/SKILL.md)
- [`workflows/swing-opportunity-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml)
