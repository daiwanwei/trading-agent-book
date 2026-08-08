# 實作：edge pipeline 端到端

研究日沒有固定鐘點——README 開場的地圖已經講清楚，`edge-candidate-agent` 到 `edge-pipeline-orchestrator` 這六個 skill，在 `skills-index.yaml` 裡全部標成 `timeframe: research`，沒有一條 workflow 規定它幾點該跑。這一章是全書最後一個實作章：把 5.1 到 5.4 分開驗證過的六個 skill 實際接力跑一遍——先看六個 stage 各自的 script 怎麼串，再看 `edge-pipeline-orchestrator` 把整條接力收進一支指令之後，落地的產出長什麼樣子。

## 兩種跑法

**(a) 在 Claude Code 對話中觸發。** 一句話描述今天想做的事：
- 「今天的 OHLCV 有沒有掃出什麼異常」→ `edge-candidate-agent`
- 「把這批 ticket 跟 hints 合成幾個 edge 概念」→ `edge-concept-synthesizer`
- 「這份策略草稿有沒有機會過審」→ `edge-strategy-reviewer`
- 「從 tickets 到策略，整條線一次跑完」→ `edge-pipeline-orchestrator`

**(b) 直接執行 script。** 六個 stage 各自的旗標，5.1 到 5.4 已經逐一對照過 `--help`；這章新核對的是 `edge-pipeline-orchestrator/scripts/orchestrate_edge_pipeline.py`，外加重新核對一次 `auto_detect_candidates.py` 與 `review_strategy_drafts.py`——六支 script 裡唯二在這裡直接示範完整指令的兩支。

## 管線 checklist

**手動逐段。** `pipeline_flow.md` 把六個 stage 對到六支 script（5.4 已經列過）：`auto_detect`→`edge-candidate-agent`、`hints`→`edge-hint-extractor`、`concepts`→`edge-concept-synthesizer`、`drafts`→`edge-strategy-designer`、`review`→`edge-strategy-reviewer`、`export` 繞回 `edge-candidate-agent`。中間 `build_hints.py`、`synthesize_edge_concepts.py`、`design_strategy_drafts.py` 三支的指令，5.1、5.2 已經核對過旗標，這裡不重複；只重新核對頭尾兩支：

```bash
python3 skills/edge-candidate-agent/scripts/auto_detect_candidates.py \
  --ohlcv /path/to/ohlcv.parquet \
  --output-dir reports/edge_candidate_auto \
  --top-n 10
```
`--output-dir` 不傳，預設就是 `reports/edge_candidate_auto`，跟 `SKILL.md` 的 Quick Commands 一致。

```bash
python3 skills/edge-strategy-reviewer/scripts/review_strategy_drafts.py \
  --drafts-dir reports/edge_strategy_drafts/ \
  --output-dir reports/ --markdown-summary
```
`--drafts-dir` 跟單檔的 `--draft` 互斥，二選一；`--markdown-summary` 額外多寫一份人讀的摘要。

**orchestrator 一鍵。** 三種模式，指令都對過 `--help`：
```bash
# 從 tickets 起跑，一路做到匯出
python3 skills/edge-pipeline-orchestrator/scripts/orchestrate_edge_pipeline.py \
  --tickets-dir path/to/tickets/ \
  --output-dir reports/edge_pipeline/

# 只跑審查—修正迴圈，吃現成的草稿
python3 skills/edge-pipeline-orchestrator/scripts/orchestrate_edge_pipeline.py \
  --review-only \
  --drafts-dir reports/edge_strategy_drafts/ \
  --output-dir reports/edge_pipeline/

# 全程跑一遍，但不落地成策略
python3 skills/edge-pipeline-orchestrator/scripts/orchestrate_edge_pipeline.py \
  --tickets-dir path/to/tickets/ \
  --output-dir reports/edge_pipeline/ --dry-run
```

**先跑一次 `--dry-run`。** 本章在暫存目錄用一份合成 ticket 實跑過：`--dry-run` 只跳過匯出這一步，`hints/`、`concepts/`、`drafts/`、`exportable_tickets/`、`reviews_iter_0/` 全部照常寫出；`pipeline_run_manifest.json` 的 `stages.export.status` 落在 `skipped_dry_run`，`exported` 欄位仍列出「本來會匯出」的候選 id，只是磁碟上不會多出 `strategies/` 那個資料夾。先看過這份清單，再決定要不要拿掉 `--dry-run`，比跑完才發現匯出了不該匯出的東西省事。

## 前置需求

六個 skill 裡，`skills-index.yaml` 的 `integrations` 只有 `edge-candidate-agent` 掛了一條——`fmp`，標 `optional`，註記是「為了產生 edge ticket 匯出用的 OHLCV」。但這不是說 `auto_detect_candidates.py` 自己去打 FMP API：這支 script 從頭到尾不叫任何 FMP 端點，`--ohlcv` 吃的是使用者自己準備好的一份 parquet；FMP 只是準備這份 parquet 的其中一種可能來源，不是這個 skill 內建的呼叫。`edge-hint-extractor`、`edge-concept-synthesizer`、`edge-strategy-designer`、`edge-strategy-reviewer`、`edge-pipeline-orchestrator` 五個在 `skills-index.yaml` 裡的 `integrations` 一律標 `local_calculation`／`not_required`——本章示範的所有指令，包含 orchestrator 一鍵模式的三種跑法，全部不連網路。

## 產出解讀

`review.yaml` 的骨架 5.3 已經拆過；這裡貼的是本章在暫存目錄用三份手寫草稿實跑 `review_strategy_drafts.py` 得到的真實輸出，不是重建的樣本：
```yaml
summary: {total: 3, PASS: 1, REVISE: 1, REJECT: 1, export_eligible: 1}
reviews:
- draft_id: draft_..._core           # verdict: PASS    confidence_score: 82
- draft_id: draft_..._conservative   # verdict: REVISE  confidence_score: 60
- draft_id: draft_..._research_probe # verdict: REJECT  confidence_score: 59
```
三筆判決印證了 5.3 那條硬規則：`research_probe` 那筆 `confidence_score` 有 59 分，換算成加權平均不算低，但 `thesis` 是空字串，C1 直接判 `fail`——一票就把總分否決成 `REJECT`，跟另外兩筆分數高低無關。`conservative` 那筆沒有任何一項 `fail`，只是 C1（thesis 太籠統）、C3（估計年度機會僅 18 次）、C8（只有一條 invalidation signal）各拿了 `warn`，加權後落在 70 分門檻之下，判 `REVISE`；只有 `core` 那筆同時過了 70 分門檻、沒背著任何 `fail`，判 `PASS`，也是三筆裡唯一 `export_eligible: true` 的一份。

`pipeline_run_manifest.json` 的形狀，同一批草稿改用 `--review-only` 跑（同樣是本章實跑結果，非重建）：`stages` 底下只有 `review_loop` 與 `export` 兩截——`review_loop` 記 `passed_ids`／`rejected_ids`／`downgraded_ids` 三份清單（各自還帶一個同名的 `passed_count`／`rejected_count`／`downgraded_count` 伴生計數欄位），`conservative` 那筆兩輪都過不了 `REVISE`，被記進 `downgraded_ids`；`export` 底下列 `exported` 與 `skipped_not_eligible` 兩個陣列，這裡只有 `core` 那一個 candidate id 進了前者。改成全流程執行，`stages` 前面還會多出 `hints`／`concepts`／`drafts` 三截，各自只記 `status` 與輸出路徑——這部分 `SKILL.md`、`pipeline_flow.md` 都沒附完整範例，是本章依實跑結果整理，不是官方文件直接列出的樣本。

`conservative` 那筆兩輪的完整過程也一併實跑過：`reviews_iter_0` 判 `REVISE`，`revision_loop_rules.md`（5.4 引過）講的 `apply_revisions` 只認得三種修正指示——精簡進場條件、補流動性篩選、四捨五入精確門檻；這份草稿實際拿到的三條建議是補因果機制、放寬樣本限制、補一條 invalidation signal，沒有一條對得上，`apply_revisions` 因此原樣放行，`reviews_iter_1` 重跑出同一組分數，仍是 `REVISE`，兩輪用盡才落進 `downgraded_ids`。規則寫死能修的三種情況，修不到的照樣空轉兩輪才降級，不是跳過。

## 收尾

匯出資格卡三個條件同時成立——判決 `PASS`、`export_ready_v1` 為 `true`、`entry_family` 落在可匯出白名單之內——5.4 已經講過，三處各自獨立寫。這裡把前幾章各自揭露過的文件落差收攏核實一次：`review_strategy_drafts.py`、`orchestrate_edge_pipeline.py`、`design_strategy_drafts.py`、`synthesize_edge_concepts.py` 四支 script 的 `DEFAULT_EXPORTABLE_FAMILIES` 現在都是同一組四個值——`pivot_breakout`、`gap_up_continuation`、`panic_reversal`、`news_reaction`；`pipeline_flow.md`「Exportable Entry Families」那節還停在只列前兩個的舊版本，是文件沒跟上程式碼的一個例子，本章依實際讀過的常數再核對一次無誤。三個條件全過，寫出來的也只是一份 `strategy.yaml` 加一份 `metadata.json`，不是一張券商訂單：離真正能被交易的策略，還要走第二部到第四部那整條篩選、部位計算、紀律閘門。跟第一部實作章那句「這是可重跑、可稽核的姿態，不是保證獲利的公式」一樣，這一章給出的也只是一份可重跑、可稽核的研究產出。從第一部 06:31 的 `market-regime-daily` 問「今天能不能做」，繞了四部到這裡問「這個觀察站不站得住」，答案照樣不是任何一支 script 替使用者做的決定。

## 延伸閱讀

- [`skills/edge-candidate-agent/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-candidate-agent/SKILL.md)
- [`skills/edge-hint-extractor/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-hint-extractor/SKILL.md)
- [`skills/edge-concept-synthesizer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-concept-synthesizer/SKILL.md)
- [`skills/edge-strategy-designer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-designer/SKILL.md)
- [`skills/edge-strategy-reviewer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-reviewer/SKILL.md)
- [`skills/edge-pipeline-orchestrator/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-pipeline-orchestrator/SKILL.md)
- [`skills/edge-pipeline-orchestrator/references/pipeline_flow.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-pipeline-orchestrator/references/pipeline_flow.md)
