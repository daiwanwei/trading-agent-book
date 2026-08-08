# 4.4 模型書：把熟練度變成資料

## 場景

2.3 節已經走過 `stockbee-momentum-burst-screener` 的計分邏輯：候選分成 A、A-、B、`WATCH_ONLY`、`REJECTED` 五級，往下游走的路徑是 `technical-analyst → position-sizer → breakout-trade-planner（可選）→ trader-memory-core`。但真正走完這條路的只是每天輸出裡的一小部分——多數候選在週線覆核那一關就被淘汰，等不到覆核機會的更多。這些留在原地的候選，通常就這樣被忘記。

`stockbee-setup-fluency-trainer` 不走那條路，也不在序章走過的那幾條核心 workflow 裡——它有自己的一條，`stockbee-fluency-loop`：`cadence: daily`，約 20 分鐘做完，`api_profile` 是最省錢的 `no-api-basic`。它直接讀 `stockbee-momentum-burst-screener` 產出的原始 JSON 報告，跟候選最後有沒有被 `technical-analyst` 留下、有沒有被 `trader-memory-core` 登記成論點無關——預設只跳過 `REJECTED` 一級，其餘不管進沒進場，都能落進模型書。

## 方法論

`review_workflow.md` 把這套工具的目的講成一句話：目標不是再生出候選，而是靠反覆比較「setup 在第一天長什麼樣」跟「接下來 3、5 個交易日實際發生了什麼」，把辨識能力練成程序性的直覺。「熟練度」在這裡被翻譯成一件具體的事：不是憑印象記得某種型態通常會漲，而是把每一次出現、每一次的後續走勢，都寫成能並排比較的紀錄。

`model_book_schema.md` 說得更直白：`setup_tags` 是整套 fluency loop 的核心，它把原本主觀的看圖判斷——底部乾不乾淨、量能有沒有乾涸、收盤位置——轉成能分群分析的資料。有了它，「這組特徵的勝率比較高」才是一句可以被驗證的話，而不只是一種印象。

`mfe_pct`、`mae_pct` 這兩個欄位，4.1、4.2 都定義過，這裡不重講意義，只提一個關鍵差異：`trader-memory-core` 的 `outcome.mfe_pct`／`outcome.mae_pct` 只補在走到 `CLOSED` 的真實部位上，還得設定 FMP key 才會有值；模型書的版本不管候選有沒有變成論點、有沒有真的下單，只要落進 `state/stockbee/model_book.jsonl`，就能靠獨立的 `update` 子指令把這兩個數字補齊。這正是模型書能覆蓋「沒有進場的候選」的關鍵——論點記憶做不到這件事，因為那裡根本沒有論點存在。

## 機制

整套流程分四步，前三步都由同一支腳本 `build_model_book.py` 驅動。

第一步 `ingest`：讀進 `stockbee-momentum-burst-screener` 的 JSON 報告，寫進或更新 `state/stockbee/model_book.jsonl`。每筆紀錄有一個決定性的 `record_id`（例如 `stockbee_mb:TEST:2026-06-20:4pct_breakout`），重複 ingest 同一筆候選只會更新原紀錄，不會生出重複行。欄位分三群：識別欄位（`schema_version`、`record_id`、`source_skill`、`source_report`、`symbol`、`setup_date`、`setup_type`、`primary_trigger`）；設定品質欄位（`rating`、`setup_score`、`state_at_ingest`、`trigger_tags`、`setup_tags`、`entry_reference`、`stop_reference`、`risk_pct_to_stop`、`day_gain_pct`、`volume_ratio_1d`、`close_location_pct`、`prior_base_days`、`base_width_pct`）；人工複核欄位（`human_label`、`human_decision`、`human_notes`——腳本只負責初始化，重跑 ingest 不會覆蓋已經寫進去的人工紀錄）。

第二步 `update`：抓 3 日、5 日兩個窗口成熟後的走勢，兩條路可選——設定 FMP API key，或直接傳一份離線的 `--prices-json`；後者是 Prerequisites 明講的選配路徑，只有沒提供離線報價時才需要 FMP key。每個窗口寫進 `outcomes.3d`／`outcomes.5d`：`forward_return_pct`、`mfe_pct`、`mae_pct`、`stop_hit`、`outcome_tag`；`overall_outcome` 取最長的窗口，通常是 5 日。七種結果標籤，條件寫死在 `outcome_tags.md`：`STRONG_WINNER`（MFE ≥ 12% 或收盤報酬 ≥ 8%，且未踩停損）、`WORKED`（MFE ≥ 6% 或收盤報酬 ≥ 4%，且未踩停損）、`FAILED_STOP`（區間內任一低點觸及或跌破 `stop_reference`）、`FAILED_FADE`（收盤報酬 ≤ −2% 且未記到停損）、`CHOPPY_FAILURE`（MAE ≤ −5% 且收盤報酬 < 2%、未記到停損）、`NEUTRAL`（沒有明確跟進或失敗）、`PENDING`（未來交易日數還不夠）。紀錄的生命週期分三階段：`PENDING_OUTCOME`（剛 ingest，未來 K 棒還不夠）、`MATURED_OUTCOME`（3 日或 5 日窗口已有足夠資料）、`REVIEWED_BY_HUMAN`——但目前腳本只寫 `matured: true/false` 這個欄位，`REVIEWED_BY_HUMAN` 本身不是被寫入的值，要靠 `human_label`／`human_notes` 有沒有填來推斷。

第三步 `summarize`：按 `rating,primary_trigger,setup_tags` 這類欄位分群，設下限如 `--min-sample 5`，產出 cohort 統計與 `rule_candidates`。`review_workflow.md` 把每週、每月的節奏也定了下來：每週用 `--min-sample 3` 看早期訊號——最好的 A/A- 贏家、最糟的 `FAILED_STOP` 案例、收盤品質差的假陽性，以及 `wide_risk`、`wide_base`、`three_days_up_before_trigger` 這類值得留意的標籤群；每月才把門檻拉到 `--min-sample 10`，才考慮要不要真的升降某個標籤。

在進到記錄之前，`SKILL.md` 自己還留了一段「把證據變成練習」的判斷準則：勝率高、5 日期望值為正、平均 MAE 還算可接受的標籤，可以考慮升級；5 日期望值疲弱、常常踩到停損、`FAILED_FADE` 反覆出現的標籤，該降級或篩掉——但升降之前，一樣要求先人工看過具代表性的圖表，不是看數字就動手改規則。這組判斷落定之後，才輪到第四步：可選的 `trader-memory-core` 記錄步驟，同時也是 `stockbee-fluency-loop.yaml` 的第 4 步，`decision_gate: true`，問的是哪些發現該被接受成操作規則、哪些只留在日誌裡等更多樣本。`stockbee-fluency-loop` 唯一必要的 skill 是 `stockbee-setup-fluency-trainer`；`trader-memory-core`、`signal-postmortem`、`backtest-expert` 都寫在 `optional_skills` 清單裡，但四個 `steps` 中只有第 4 步真的點名 `trader-memory-core`——`signal-postmortem` 與 `backtest-expert` 雖列在可選清單上，manifest 本身沒有替它們接上任何一步。`journal_destination` 同樣指向 `trader-memory-core`——跟序章走過的那幾條 workflow 一樣，最後一行寫的都是同一句話。

## 判讀與誤用

`stockbee-fluency-loop.yaml` 的 `when_not_to_run` 把話說在前面：不要把這條迴圈當成執行流程或訊號服務；不要靠少數樣本就改變交易規則，採用或篩掉一個 setup 標籤前，要有足夠觀測案例，還得配上人工看圖。`review_workflow.md` 的 Review Discipline 是同一件事的操作版：不要對一小撮樣本過度解讀；`rule_candidates` 只是提示該去覆核哪些圖，不是自動生效的規則變更；真要改規則，通常得同時滿足樣本數夠、市場邏輯站得住腳、代表性圖表已經看過這三個條件。

這正是模型書的統計跟回測不是同一件事的地方。回測是拿一段固定的歷史區間、跑一套完整規則重演一遍；模型書則是每天篩選器跑出什麼就記什麼，一天天疊上去，覆蓋到的市況取決於哪些日子被記錄下來，不是事先劃定的抽樣。三步驟裡的 cohort 統計，講的是「目前為止觀察到的樣本」，不是「這套規則在歷史上驗證過」。

除了這份可選清單裡的落差，還有一件事值得多想一層：`stockbee-setup-fluency-trainer` 本身在 `skills-index.yaml` 標成 `status: beta`——2.3 節已經用同一句話提醒過三支 Stockbee screener，模型書工具也不例外，讀 cohort 報告時值得多留一分餘地。`manual_review` 補了四條：接受規則變更之前，先看過具有代表性的贏家與輸家圖表；把證據跟執行決策分開——記錄下來的是 setup 的行為，不是真實損益；樣本數門檻要寫清楚，尤其是市場 regime 換了的時候；接受的學習要餵進 `monthly-performance-review`，不要每天就地拼湊規則。

## 延伸閱讀

- [`skills/stockbee-setup-fluency-trainer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-setup-fluency-trainer/SKILL.md)
- [`skills/stockbee-setup-fluency-trainer/references/model_book_schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-setup-fluency-trainer/references/model_book_schema.md)
- [`skills/stockbee-setup-fluency-trainer/references/outcome_tags.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-setup-fluency-trainer/references/outcome_tags.md)
- [`skills/stockbee-setup-fluency-trainer/references/review_workflow.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-setup-fluency-trainer/references/review_workflow.md)
- [`workflows/stockbee-fluency-loop.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/stockbee-fluency-loop.yaml)
