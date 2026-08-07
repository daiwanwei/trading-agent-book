# 後續里程碑待辦（源自 M0+M1 最終審查，2026-08-07）

## M5 校對清單

- [ ] `book/part1-regime/03-ftd.md`：「判定分四步」但方法論段只標了三個「第N步」（第四步在機制段未標號）
- [ ] `book/part1-regime/04-macro-and-bubble.md`：FMP「必要 vs 建議」的上游文件矛盾（SKILL.md vs skills-index.yaml）未在正文向讀者揭露——與生成的附錄 A 形成書內張力；上游調和後同步
- [ ] `book/part1-regime/04-macro-and-bubble.md`：「第 32 行」行號引用對每日演進的上游太脆弱，改為欄位名引用
- [ ] `book/part1-regime/05-exposure-posture.md`：「反向換算過」措辭可能被讀成代數反轉（實為獨立計算、方向相反），可再鬆一字
- [ ] 序章「兩種出身」句未涵蓋 CPW→KDW 邊的 `prerequisite_workflows` 出處類別（無錯誤陳述，僅不窮盡）
- [ ] 全書重複語感：「把話說死／講死」出現多次；1.1 divergence 警告條件漏了 spread>20pp 分支
- [ ] 3.3 的 TRADING_HALTED 引文可加註「斷路器實際不會輸出此值」；3.2/實作章「唯一的腳本」可改「唯一的 CLI 入口」

## M4（第五部）前置

- [ ] 序章 Mermaid 的 EDGE 虛線邊（改進後的 skills → swing-opportunity-daily）是本書詮釋——寫第五部時必須對照實際 pipeline 重新確認，並釐清 skill improvement loop 與 edge pipeline 的敘事順序

## 工具強化（下次動到腳本時）

- [ ] `scripts/generate_appendix.py`：加 rendered-rows == len(skills) 斷言（category 遺漏時 fail closed）；workflows/ 目錄缺失防護；表格 cell 的 `|` 跳脫
- [ ] `scripts/check_book.py`：SUMMARY.md 缺失時的友善錯誤；upstream dirty tree 時 source-commit 標記可能失真
- [ ] `tests/`：appendix B renderer 的 optional_skills / prerequisite_workflows /（可選）步驟分支補 fixture 覆蓋
- [ ] check_book.py：加「CJK 散文中出現半形標點（code span 之外）」檢查——M2 曾發生此問題

## 使用者手動步驟（尚未完成）

- [ ] GitBook.com：建 space →GitHub Git Sync 綁 `daiwanwei/trading-agent-book`（main）→ root 由 .gitbook.yaml 讀取
- [ ] 取得公開 URL 後回填 `README.md` 第 7 行

## M3 最終審查 ride-along（併入 M5 校對）

- [ ] 第二部 README：COT 首次出現可加（Commitment of Traders）展開；Kanchi 句逗號連綴可順
- [ ] 2.1：可補 Alpaca 品牌標注；dry-up ratio 方法論/機制間可加一句橋
- [ ] 2.1 與實作章：「S&P 500 前 100 名候選」措辭可更精確（全數抓取→預篩→截斷 100）
- [ ] 2.4：「六到九成」混合了兩支 screener 的節省機制，可拆開表述
- [ ] 序章：「說法一模一樣」→「開頭一模一樣」（與 2.3 的細分一致）
