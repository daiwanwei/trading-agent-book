# 後續里程碑待辦（源自 M0+M1 最終審查，2026-08-07）

## M5 校對清單

- [x] `book/part1-regime/03-ftd.md`：「判定分四步」但方法論段只標了三個「第N步」（第四步在機制段未標號）——（M5 wave 1 完成）
- [x] `book/part1-regime/04-macro-and-bubble.md`：FMP「必要 vs 建議」的上游文件矛盾（SKILL.md vs skills-index.yaml）未在正文向讀者揭露——與生成的附錄 A 形成書內張力；上游調和後同步——（M5 wave 1 完成）
- [x] `book/part1-regime/04-macro-and-bubble.md`：「第 32 行」行號引用對每日演進的上游太脆弱，改為欄位名引用——（M5 wave 1 完成）
- [x] `book/part1-regime/05-exposure-posture.md`：「反向換算過」措辭可能被讀成代數反轉（實為獨立計算、方向相反），可再鬆一字——（M5 wave 1 完成）
- [x] 序章「兩種出身」句未涵蓋 CPW→KDW 邊的 `prerequisite_workflows` 出處類別（無錯誤陳述，僅不窮盡）——（M5 wave 1 完成）
- [x] 1.1 divergence 警告條件漏了 spread>20pp 分支——（M5 wave 1 完成）
- [x] 全書重複語感：「把話說死／講死」出現多次——（M5 wave 1/2/最終 fix wave 全部完成：序章與第二部三處已改（agent-week.md:35, part2/README.md:7, 07-hands-on.md:69——先前結案時誤植成 01-minervini.md:29，已更正），README.md:31 與 05-shapiro.md:44 已於最終 fix wave 改寫；01-minervini.md:29 保留原話不動，是全書唯一刻意保留的一處）
- [x] 3.3 的 TRADING_HALTED 引文可加註「斷路器實際不會輸出此值」——（M5 wave 3 完成）；3.2/實作章「唯一的腳本」可改「唯一的 CLI 入口」——（M5 wave 3 完成）
- [ ] 未來勘誤：`book/part5-research/05-self-improvement.md:43` 還有一處裸 SKILL.md（該檔案本輪長度鎖定在 2,800 CJK 字，任何淨增字數的編輯都得延後）；COT 在 `part2-screening/README.md:19`、`05-shapiro.md:5` 與附錄 A／B 多處寫成單數「Commitment of Traders」，但附錄 D 詞彙表的正式定義是複數「Commitments of Traders」——一字之差，留待下次勘誤一併訂正

## M4（第五部）前置

- [x] 序章 Mermaid 的 EDGE 虛線邊（改進後的 skills → swing-opportunity-daily）是本書詮釋——寫第五部時必須對照實際 pipeline 重新確認，並釐清 skill improvement loop 與 edge pipeline 的敘事順序（解決：task-12 查核確認虛線邊語義成立，M4 最終審查 fix wave 已改正 EDGE 節點標籤與研究日散文的敘事順序）

## M4 上游觀察（供回報上游）

- [ ] `skills/exposure-coach` 的 `--theme` 輸入接不上 `theme-detector` 的輸出：`calculate_exposure.py` 的 `extract_theme_score()` 只認頂層的 `theme_score` 或 `theme_strength` 兩個欄位，但 `theme_detector.py` 產出的 JSON 頂層是 `themes`／`industry_rankings`／`sector_uptrend`／`summary` 等，兩個欄位都不存在。結果是即使把 theme 報告傳給 `--theme`，該分項仍被算成缺漏（實測後 `inputs_missing` 依然含 `theme`），`WEIGHTS` 裡分配給它的 5% 永遠拿不到。修法有兩種：`theme-detector` 在頂層補一個 `theme_score`（其 `summary` 已有 `bullish_count`／`bearish_count` 可換算），或 `extract_theme_score()` 改讀既有結構。同一份 `WEIGHTS` 裡的 `sector` 5% 也有類似問題，但成因不同——`sector-analyst` 是吃圖表截圖的人工分析 skill，本來就沒有可自動產出的 JSON
- [ ] `skills/signal-postmortem/SKILL.md` 第 36 行左右宣稱沒有 API key 時仍可用 `--exit-price`／`--exit-date` 手動記錄結果，但 `postmortem_recorder.py` 的手動路徑把 `realized_returns` 傳成空字典，`classify_outcome()` 讀到的 5 日報酬永遠是 0.0，手動記錄的 `outcome_category` 因此恆定判成 `NEUTRAL`，不會反映真實輸入的出場價
- [ ] `skills/edge-hint-extractor/references/hints_schema.md` 的 Field Notes 寫 `preferred_entry_family` 只能是 `pivot_breakout` 或 `gap_up_continuation`（2 個），但同一個 skill 的 `build_hints.py` 的 `SUPPORTED_ENTRY_FAMILIES` 已經是 4 個（多了 `panic_reversal`、`news_reaction`），連腳本自己生成的範例 hint 都已經在用這兩個新值
- [ ] `skills/edge-strategy-reviewer/references/review_criteria.md` 的 C7 `EXPORTABLE_FAMILIES` 仍寫兩個值，`review_strategy_drafts.py` 的 `DEFAULT_EXPORTABLE_FAMILIES` 已經是四個；另外 C1 的 fail 門檻文件寫「少於 5 個字」，程式碼實際是 `len(words) < 3`，C2／C3 的 pass 分數文件寫死 80，程式碼其實是連續分級（60、80、90 等級距），建議一併核對用語與門檻是否同步
- [ ] `skills/edge-candidate-agent/references/research_ticket_schema.md`、`skills/edge-candidate-agent/references/signal_mapping.md`、`skills/edge-pipeline-orchestrator/references/pipeline_flow.md`、`skills/edge-pipeline-orchestrator/references/revision_loop_rules.md` 四份文件都還停在「只有 `pivot_breakout`、`gap_up_continuation` 兩個可匯出家族」的舊版本，`candidate_contract.py` 的 `SUPPORTED_ENTRY_FAMILIES` 與四支 script 的 `DEFAULT_EXPORTABLE_FAMILIES` 已經同步成四個
- [ ] `scripts/run_skill_improvement_loop.py` 的 `_is_safe_dirty_tree()` docstring 有兩處與實作不符：（1）未追蹤檔（`??`）並非「一律擋下」，`state/` 底下放行；（2）tracked 變更並非只允許 `reports/`／`logs/`，`_SAFE_DIRTY_PREFIXES` 還含 `state/`
- [ ] `skills/signal-postmortem/references/feedback-integration.md` 宣稱「skill improvement loop reads backlog entries」，但 `scripts/run_skill_improvement_loop.py` 全文搜尋 `backlog` 是 0 處引用，這條回饋路徑目前只是文件承諾、程式未接
- [ ] `trade-performance-coach` 的 behavior tag 清單在三處文件不一致：`SKILL.md`（及其自動生成的 `docs/en/skills/trade-performance-coach.md`）列 9 個，`references/behavior-tags.md` 列 10 個（多 `unknown_size_discipline`），`assets/performance_coach_report.schema.json` 的 enum 列 11 個（再多一個 `loss_aversion`，前兩處文件都沒提到它）

## 工具強化（下次動到腳本時）

- [x] `scripts/generate_appendix.py`：加 rendered-rows == len(skills) 斷言（category 遺漏時 fail closed）——（Task 2 完成）；workflows/ 目錄缺失防護——（Task 2 完成）；表格 cell 的 `|` 跳脫——（Task 2 完成）
- [x] `scripts/check_book.py`：SUMMARY.md 缺失時的友善錯誤——（Task 1 完成）
- [ ] `scripts/check_book.py`：upstream dirty tree 時 source-commit 標記可能失真——（未交付，保留以供下次動到此腳本時）
- [ ] `tests/`：appendix B renderer 的 optional_skills / prerequisite_workflows /（可選）步驟分支補 fixture 覆蓋——（Task 2 明確未含 appendix B 分支測試，誠實保留未勾）
- [x] check_book.py：加「CJK 散文中出現半形標點（code span 之外）」檢查——（Task 1 完成）

## 使用者手動步驟（尚未完成）

- [ ] GitBook.com：建 space →GitHub Git Sync 綁 `daiwanwei/trading-agent-book`（main）→ root 由 .gitbook.yaml 讀取
- [ ] 取得公開 URL 後回填 `README.md` 第 7 行

## M3 最終審查 ride-along（併入 M5 校對）

- [x] 第二部 README：COT 首次出現可加（Commitment of Traders）展開；Kanchi 句逗號連綴可順——（M5 wave 2 完成）
- [x] 2.1：可補 Alpaca 品牌標注；dry-up ratio 方法論/機制間可加一句橋——（M5 wave 2 完成）
- [x] 2.1 與實作章：「S&P 500 前 100 名候選」措辭可更精確（全數抓取→預篩→截斷 100）——（M5 wave 2 完成）
- [x] 2.4：「六到九成」混合了兩支 screener 的節省機制，可拆開表述——（M5 wave 2 完成）
- [x] 序章：「說法一模一樣」→「開頭一模一樣」（與 2.3 的細分一致）——（M5 wave 1 完成）
