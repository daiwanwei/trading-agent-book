# 實作：trade-memory-loop

這週三（2026-08-05），第三部實作章那筆判了 `GO` 的 `th_aapl_gm_20260703_0001` 平倉了——168.00 元出場，比 155.00 元的進場多賺了 13 點。從 `ENTRY_READY` 走到真的成交，是人在券商那端按下去的，不是任何腳本，第三部收尾已經講過；這裡接手的是平倉之後的事。`trade-memory-loop` 跟前三部的固定節奏不一樣：不是每天跑一次，是每次平倉才觸發，manifest 標的 `estimated_minutes` 落在半小時上下，`api_profile` 分類跟前三部一樣屬於 `no-api-basic` 這一檔。整條迴圈總共會產出六份 artifact，真正卡在 `required_skills` 清單裡的，就只有負責記錄的 `trader-memory-core` 跟負責分類的 `signal-postmortem`；教練與回測那兩支，manifest 裡都標成 `optional_skills`，跑不跑由使用者自己決定。不用任何付費 API：Step 1 到 Step 3 全部離線可跑，`FMP_API_KEY` 只在 Step 2 派得上用場——底下會提到，沒有這把 key，`outcome_category` 就分類不出來。

## 兩種跑法

**(a) 在 Claude Code 對話中觸發。** 一句話描述剛發生的事，Claude 會自己找到對應的 skill：
- 「這筆 AAPL 平倉了，168 出場，幫我記錄」→ `trader-memory-core`
- 「這筆賺的錢是靠判斷還是手氣」→ `signal-postmortem`
- 「接下來幾筆要注意什麼」→ `trade-performance-coach`（可選）

**(b) 直接執行 script。** 下面三條指令，逐一對照各自的 `--help` 核對過旗標；`trader-memory-core` 走專屬的 `trader_memory_cli.py` launcher（`store`／`ingest`／`review` 三個子指令各轉發給一支真正的腳本），另外兩支各是獨立 script，沒有共用入口，也不共用輸入格式。

## trade-memory-loop checklist

**Step 1・記錄平倉**（`decision_gate: false`）
```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py store --state-dir state/theses/ \
  close th_aapl_gm_20260703_0001 \
  --exit-reason target_hit --actual-price 168.00 --actual-date 2026-08-05
```
終端機只印一行：`th_aapl_gm_20260703_0001 → CLOSED (target_hit), pnl=663.0`。`close` 只接受 `ACTIVE` 或 `PARTIALLY_CLOSED` 起點，`--exit-reason` 是五選一的 enum（`stop_hit`／`target_hit`／`time_stop`／`invalidated`／`manual`），不接受任意字串。

**Step 2・事後檢討**（`decision_gate: true`，必經）`signal-postmortem` 的 `postmortem_recorder.py` 不吃 thesis YAML——它要一份 signal record，欄位是 `signal_id`／`ticker`／`signal_date`／`predicted_direction`／`source_skill`／`entry_price`，得從剛寫出的 `closed_thesis_record` 自己抽出來組一份：
```bash
python3 skills/signal-postmortem/scripts/postmortem_recorder.py \
  --signals-file reports/signals_aapl.json --holding-periods 5,20 --output-dir reports/
```
沒有 `FMP_API_KEY`，`realized_returns` 是空的，`outcome_category` 停在 `NEUTRAL`，連 `holding_days`／`exit_date` 都退回成第一個持有窗口後的 `2026-07-11`——不是 `close` 那步寫進 thesis 的 30 天、2026-08-05。這不是筆誤，是離線時的真實行為：這支 script 靠的是自己抓回來的報酬率分類，不是 `trader-memory-core` 那邊的真實出場。4.2 已經說過，`outcome_category` 本來就不是 `decision_question` 要的那組四選一根因——這筆錢是靠論點還是手氣，`NEUTRAL` 答不了，還是得靠人（或 Claude）回頭讀 `closed_thesis_record` 的 `outcome.pnl_pct`、`kill_criteria` 有沒有被觸發，自己判斷。

**Step 3・反饋 gate**（`decision_gate: true`，可選）`trade-performance-coach` 同樣不讀 thesis YAML，要另外組一份小 JSON，把 `planned`（進場 155、停損 148.50、目標 168）跟 `actual` 對照著放：
```bash
python3 skills/trade-performance-coach/scripts/review_trade_performance.py \
  --input reports/coach_input_aapl.json \
  --output-dir reports/trade-performance-coach --markdown
```
這一筆計畫與執行一致，跑出來 `overall_verdict: OK`，`next_session_operating_rules` 只有一條「維持現行規則」，`human_decision_gate` 預設 `journal_only`。

`trade-memory-loop` 其實還有兩步不在這份三件式 checklist 裡：可選的 Step 4 讓 `backtest-expert` 拿 `postmortem_findings` 回頭重驗這筆交易背後的規則假說；必經的 Step 5 換 `trader-memory-core` 自己收尾——
```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py review --state-dir state/theses/ \
  postmortem th_aapl_gm_20260703_0001
```
寫出 `state/journal/pm_th_aapl_gm_20260703_0001.md`，帶著時間軸、P&L、MAE/MFE 表格——這才是這一輪迴圈真正落袋的 `lessons_log_entry`，跟 Step 2 那個同樣叫「postmortem」的 `signal-postmortem` 不是同一件事，讀的時候別把兩者搞混。

## 週/月節奏

每週收盤後，`weekly-performance-digest` 把這一週所有 `CLOSED` 論點滾成一份摘要——這支 script 的 `--state-dir` 要求目錄已經存在，不像 `trader-memory-core` 的 `ingest`：`register()` 裡那行 `mkdir(parents=True, exist_ok=True)` 只在登記新論點時跑一次；同一支 `store` 底下的 `close`／`trim` 這類指令都要先讀到已存在的論點，不會替你建目錄，第一次跑之前得手動確認 `state/theses/` 已經在：
```bash
python3 skills/weekly-performance-digest/scripts/generate_weekly_digest.py \
  --state-dir state/theses --from-date 2026-08-03 --to-date 2026-08-09 --output-dir reports/ -v
```
這週只平倉這一筆，輸出就是 `1 trades, 1W/0L, P&L $663.00`；`pattern_analysis` 裡的 `by_source_skill`、`by_thesis_type` 各自只有一個桶，樣本一多才看得出分布。`metrics.r_multiple_avg` 算出來是 `2.0`——用的是 `pnl_dollars / ((entry.actual_price − exit.stop_loss) × shares)`，155.00 進場、148.50 停損、168.00 出場，跟第三部位算出來的風險距離對得起來，不是巧合。月初第一個週末，`monthly-performance-review` 第 3 步一樣叫 `review_trade_performance.py`，但決定行為的不是輸入檔裡的 `review_type`——那個欄位只被讀出來原樣印進報告，`build_review()` 沒有任何一支 `evaluate_*` 函式照它分支。真正的分岔在 `main()`：只傳一個 `--input` 就直接載入；傳兩個以上，script 自動組一個 `monthly_aggregate` 包裝，同時在 stderr 印警告——這個包裝只是把每筆記錄原樣塞進 `monthly.trades`，不做任何逐筆彙整，而 `monthly.trades` 事實上從沒被任何 `evaluate_*` 函式讀過，唯一真的會影響風險判斷的是 `monthly.consecutive_losses`，包裝本身並不會自動填上。script 自己的註解說，真正的月度聚合器還沒寫，是待辦；想要準確的月度分析，得自己先把整月資料聚合成一份 JSON 當單一 `--input` 傳進去。

## 產出解讀

`th_aapl_gm_20260703_0001` 平倉後，thesis YAML 的 `outcome` 區塊（本章在暫存目錄實跑 Step 1 得到的真實欄位）：
```yaml
outcome:
  pnl_dollars: 663.0
  pnl_pct: 8.39
  holding_days: 30
  mae_pct: null
  mfe_pct: null
```
`mae_pct`／`mfe_pct` 留白，不是因為沒設 `FMP_API_KEY`——Step 1 的 `close()` 從頭到尾不會呼叫任何抓報價的函式，這兩個欄位在 `close()` 裡壓根沒被碰過。真的會抓歷史報價的是 `thesis_review.generate_postmortem()` 裡的 `compute_mae_mfe()`，但抓不抓得到，取決於呼叫端有沒有傳 `price_adapter`——Step 5 用的 `postmortem` 子指令，argparse 只認 `thesis_id` 跟 `--journal-dir`，沒有 `--api-key`，`main()` 也從沒建過 `FMPPriceAdapter`，就算環境變數設了 `FMP_API_KEY`，這條 CLI 路徑目前還是拿不到 MAE/MFE。

`postmortem_findings`（`postmortem_recorder.py` 實跑 Step 2 寫出的欄位，不是重建的）：
```json
{
  "postmortem_id": "pm_sig_AAPL_20260706_gm01",
  "ticker": "AAPL",
  "predicted_direction": "LONG",
  "realized_returns": {},
  "outcome_category": "NEUTRAL",
  "regime_at_signal": "RISK_ON",
  "regime_at_exit": "UNKNOWN"
}
```
`realized_returns` 若真的有 `FMP_API_KEY`，會長成 `{"5d": 0.02, "20d": 0.06}` 這種鍵值——`--holding-periods 5,20` 就是這兩個鍵的來源；`outcome_category` 也才有機會落在 `TRUE_POSITIVE`／`FALSE_POSITIVE`／`FALSE_POSITIVE_SEVERE`／`REGIME_MISMATCH` 其中一種，而不是停在 `NEUTRAL`。

## 收尾

這三步每一步都要求把上一步的輸出，翻譯成下一支 script 自己的欄位——沒有一條是自動接好的水管，這也是本章示範完之後最值得記住的一件事：`consumes: closed_thesis_record` 寫在 workflow YAML 裡，不代表下一支 script 真的認得那份 YAML。4.1 早就講過這個道理：登記時晚寫幾天的 `IDEA`、事後多算出來的持股數，未必改得了那一筆交易的輸贏，卻足以讓月底、季底彙整出來的每一項指標都跟著歪掉。`trade-memory-loop` 把這句話變成三個具體動作：記錄要如實，分類要老實——連 `NEUTRAL` 這種「資料不夠、答不出來」的結果也照實留著，不硬湊一個好看的分類，根因判斷更不能因為手氣好就跳過不問。跟前三部立的場一樣：這一輪迴圈給出的是可重跑、可稽核的紀錄，不是自動變聰明的保證，也不會替使用者做出「這筆交易做得好不好」的最終判斷——熟練度是不是真的在累積，要等第五部才看得出來。

## 延伸閱讀

- [`skills/trader-memory-core/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trader-memory-core/SKILL.md)
- [`skills/signal-postmortem/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/signal-postmortem/SKILL.md)
- [`skills/trade-performance-coach/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-performance-coach/SKILL.md)
- [`skills/weekly-performance-digest/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/weekly-performance-digest/SKILL.md)
- [`workflows/trade-memory-loop.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/trade-memory-loop.yaml)
- [`workflows/monthly-performance-review.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/monthly-performance-review.yaml)
