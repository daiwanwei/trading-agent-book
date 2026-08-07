# 設計文件：《一個 AI 交易 Agent 的一週》GitBook

- 日期：2026-08-07
- 狀態：已與作者確認的設計（brainstorming 產出）
- 上游素材：[tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)（本機 clone：`~/Projects/wade/math/claude-trading-skills`）

## 1. 背景與目標

上游 repo 收錄 71 個交易相關 Claude Skills，素材量已達書籍規模（167 份 references、約 18.3 萬英文字），但知識散落在各 skill 目錄內，缺乏連貫敘事。本專案以**策展**方式把這些 skills 重組成一本 GitBook：以「一個 AI 交易 Agent 如何運作」為敘事主軸，從市場分析開始，沿著真實的決策鏈一步步展開。

成功標準：讀者讀完序章就理解整個系統的運作循環；讀完任一部就能理解該決策階段「為什麼這樣設計」並實際跑起來；全書指令與事實可驗證。

## 2. 讀者與語言

- **讀者（混合型）**：主線敘事寫給想了解「AI Agent 如何做交易決策」的廣泛讀者；每部收尾的「實作」章寫給想動手跑的人。與上游 Jekyll 文件站（操作手冊定位）互補不重複。
- **語言**：繁體中文敘事；術語、指令、檔名、artifact 名稱保留英文原文。

## 3. 範圍

- **主線**：約 45 個 skills 深入敘事，以上游 `workflows/*.yaml` 的真實步驟順序為骨架。
- **附錄**：全部 71 個 skills 的速查表 + 11 條 workflows 對照表，由腳本從上游 `skills-index.yaml` 與 `workflows/*.yaml` 自動生成。
- **非目標（out of scope）**：
  - 不整篇翻譯上游 references；不重複上游文件站的 CLI 細節（連結回上游）。
  - 不做英文版（結構驗證後再議）。
  - 不修改上游 repo；本書 repo 完全獨立。
  - 不提供投資建議；書中明確承襲上游「輸出是姿態不是訊號、不自動下單」的立場。

## 4. 敘事架構與目錄

書名（暫定）：《一個 AI 交易 Agent 的一週：71 個 Claude Skills 的策展導讀》

架構：**序章時間軸總覽 + 五部決策漏斗深入**。序章用連續敘事完整走一遍 Agent 的一週；之後各部按決策階段深入，每部以場景開場、以「實作」章收尾。

```
序章　一個 AI 交易 Agent 的一週
      週一 06:30 regime check（廣度→上升趨勢→頂部風險→exposure 姿態）
      → 姿態 allow 才進入盤前篩選（斷路器→screeners→週線驗證→部位計算
      →登記論點→紀律閘門）→ 手動下單 → 盤後記帳 → 週六存股檢視
      → 平倉觸發檢討迴圈 → 月底總結 → 研究日進化。
      核心隱喻：skills 是器官、workflows 是神經系統、fail-closed gates 是本能反射。

第一部　市場狀態 ── 今天能不能做？
  1.1  市場的心跳：廣度與參與度        market-breadth-analyzer, uptrend-analyzer
  1.2  頂部的三種徵兆                  market-top-detector, ibd-distribution-day-monitor
  1.3  底部的確認訊號：FTD             ftd-detector
  1.4  更長的視野：宏觀 regime 與泡沫  macro-regime-detector, us-market-bubble-detector
  1.5  收斂成一個姿態                  exposure-coach（allow / restrict / cash-priority）
  實作  market-regime-daily 完整跑一遍（15 分鐘、免 API）

第二部　選股 ── 做什麼？（五大流派的偵查工具）
  2.1  Minervini：波動收縮與突破       vcp-screener, breakout-trade-planner
  2.2  O'Neil：CANSLIM 成長股          canslim-screener
  2.3  Stockbee：動能三部曲            stockbee-momentum-burst-screener,
                                        stockbee-episodic-pivot-analyzer,
                                        stockbee-exhaustion-hammer-screener
  2.4  Kanchi：存股的紀律              kanchi-dividend-sop, value-dividend-screener,
                                        dividend-growth-pullback-screener
  2.5  Shapiro：站在人群的對面         cot-contrarian-detector → news-reaction-failure-analyzer
                                        → technical-analyst → contrarian-setup-gate
                                        （完整四步管線含 fail-closed 狀態機；
                                        futures-position-sizer 於第三部回頭引用）
  2.6  事件驅動衛星                    earnings-trade-analyzer → pead-screener,
                                        theme-detector；parabolic-short-trade-planner（進階選讀）
  實作  swing-opportunity-daily 的 screener 段

第三部　風險與紀律 ── 做多少、該不該做？
  3.1  風險先行的部位計算              position-sizer（停損距離 / ATR / Kelly）,
                                        futures-position-sizer
  3.2  最後一眼：圖表決策閘            technical-analyst 作為 decision gate
  3.3  三道閘門的 fail-closed 哲學     exposure gate → drawdown-circuit-breaker
                                        → pre-trade-discipline-gate
  3.4  人與 Agent 的分工               manual_review 設計、「不自動下單」原則
  實作  swing-opportunity-daily 的 gate 段（step 7–11）

第四部　交易記憶 ── 平倉之後學什麼？
  4.1  論點的生命週期                  trader-memory-core（IDEA→ENTRY_READY→ACTIVE
                                        →PARTIALLY_CLOSED→CLOSED 狀態機）
  4.2  誠實的事後檢討                  signal-postmortem、MAE/MFE
  4.3  教練看的是行為不是損益          trade-performance-coach, weekly-performance-digest
  4.4  模型書：把熟練度變成資料        stockbee-setup-fluency-trainer
  實作  trade-memory-loop + monthly-performance-review

第五部　策略研究 ── Agent 如何進化？
  5.1  從觀察到假說                    edge-candidate-agent, edge-hint-extractor,
                                        trade-hypothesis-ideator
  5.2  從假說到策略草稿                edge-concept-synthesizer, edge-strategy-designer
  5.3  審查與否證                      edge-strategy-reviewer, backtest-expert,
                                        residual-edge-analyzer, strategy-pivot-designer
  5.4  整條管線自動化                  edge-pipeline-orchestrator, stockbee-20pct-study
  5.5  Agent 改進自己的 skills         skill improvement loop 與 generation pipeline
                                        （dual-axis-skill-reviewer, skill-designer,
                                        skill-idea-miner）——全書 meta 收尾：本書描述的
                                        Agent 正在每天自動改進書裡描述的這些工具
  實作  edge pipeline 端到端一次

附錄
  A.  71 skills 速查表（自動生成，含 API 需求矩陣）
  B.  11 條 workflows 對照表（自動生成）
  C.  API 設定指南（FMP / FINVIZ / Alpaca；手寫）
  D.  詞彙表（改編自上游 docs/en/glossary.md；手寫）
```

設計取捨：

- **Shapiro 整條放 2.5**：四步管線橫跨選股與規劃，拆開會毀掉「完整逆勢方法」的敘事價值；第三部僅回頭引用其 sizing 步驟。
- **主線未覆蓋的 26 個 skills**（meta 工具、日曆類、盤中執行類）只出現在附錄 A，5.5 例外（meta 故事需要）。

## 5. 章節內部模板

每個小節固定五段：

1. **場景**（150–300 字）：Agent 時間軸上的具體一刻；全部對應真實 workflow 步驟與 artifact 名稱，不虛構。
2. **方法論**：流派理論脈絡（從 references 提煉重述），標注原始出處（書名/部落格/訪談）。
3. **機制**：輸入 → 評分/判定邏輯 → 輸出 artifact → decision gate 語義；複雜管線配 Mermaid 圖。
4. **判讀與誤用**：怎麼讀輸出、什麼情況不該用（取材 workflow YAML 的 `when_not_to_run` 與 `manual_review`）。
5. **延伸閱讀**：連回上游 SKILL.md 與 references 的 GitHub 連結。

每部開場 1–2 頁「場景 + 本部地圖」；收尾統一「實作」章（指令、API 需求、產出檔案位置）。

## 6. 素材對應與引用策略

素材優先序：`workflows/*.yaml`（敘事骨架）→ `SKILL.md`（機制事實）→ `references/*.md`（方法論深度）→ `docs/en/skills/*.md`（操作細節）。

三原則：

1. **重述不搬運**：英文素材以繁中重述 + 連結回上游具體檔案，不整段翻譯貼入（防漂移、降 IP 風險）。
2. **區分實作與原著**：每個流派章節標注「原著方法」vs「本 repo 的程式化實作」，並點出兩者差異。
3. **指令可驗證**：書中所有指令、檔名、參數在寫作時逐一對照上游 repo 現狀驗證。

## 7. Repo 結構與工具鏈

```
trading-agent-book/                 # 本機：~/Projects/wade/math/trading-agent-book
├── .gitbook.yaml                   # Git Sync 設定（root: book/）
├── README.md                       # repo 說明（非書內容）
├── book/
│   ├── SUMMARY.md                  # GitBook 目錄（手寫維護）
│   ├── README.md                   # 書首頁 = 序章導言
│   ├── prologue/
│   ├── part1-regime/
│   ├── part2-screening/
│   ├── part3-discipline/
│   ├── part4-memory/
│   ├── part5-research/
│   └── appendix/
│       ├── a-skills-reference.md   # 自動生成
│       ├── b-workflows.md          # 自動生成
│       ├── c-api-setup.md          # 手寫
│       └── d-glossary.md           # 手寫
├── scripts/
│   └── generate_appendix.py        # 上游 index/workflows → 附錄 A/B
└── docs/specs/                     # 本設計文件
```

- **附錄防漂移**：`generate_appendix.py` 以上游 repo 為唯一資料源（預設讀本機 clone 路徑，可設定），生成頁開頭標 `<!-- generated: true -->`；手寫頁不標。v1 手動跑，之後視需要加 CI。
- **GitBook 接線**：GitBook.com space → GitHub Git Sync → `.gitbook.yaml` 設 `root: book/`；Mermaid 原生支援；開源免費方案可申請。
- **手寫頁自由**：敘事章節不受生成器管轄；快速變動的 CLI 細節一律連結回上游。

## 8. 路線圖（每個 milestone 結束都是可發布狀態）

| 里程碑 | 內容 | 理由 |
|---|---|---|
| M0 | repo + Git Sync + 完整 SUMMARY.md（空頁佔位）+ 附錄生成器 | GitBook 立即可見書的形狀；附錄先有真內容 |
| M1 | 序章 + 第一部（含實作章） | 最薄縱切先驗證章節模板，避免在最厚的第二部才發現模板問題 |
| M2 | 第三部 | 與第一部合成完整「閘門哲學」敘事弧 |
| M3 | 第二部（五大流派） | 最厚，可逐流派分批釋出 |
| M4 | 第四部 + 第五部 | 收尾於 Agent 自我改進的 meta 故事 |
| M5 | 附錄 C/D 手寫頁 + 全書校對 | 術語一致性、指令再驗證 |

## 9. 風險與對策

| 風險 | 對策 |
|---|---|
| 上游 skills 每日演進，書中事實過時 | 書只寫穩定的方法論層；CLI 細節連結回上游；附錄自動生成；「機制」段寫作時標注對應上游 commit 區間 |
| IP 敏感（Minervini / O'Neil / Stockbee / Shapiro / Kanchi 方法論） | 重述不搬運；每節標注原著出處並推薦原著；區分原著與 repo 實作 |
| 敘事與事實脫節（場景虛構過度） | 場景僅使用真實 workflow 步驟、gate 與 artifact 名稱；寫作時對照 YAML |
| GitBook 平台綁定 | 內容為純 Markdown + Mermaid，隨時可遷移 mdBook / Docusaurus |

## 10. 決策紀錄

| 決策 | 選擇 |
|---|---|
| 讀者定位 | 混合型（敘事主線 + 章末實作） |
| 語言 | 繁體中文（術語/指令保留英文） |
| 範圍 | 核心主線約 45 skills + 自動生成附錄涵蓋全部 71 |
| 存放 | 獨立新 repo `trading-agent-book`，GitBook Git Sync |
| 敘事主軸 | 混合式：序章時間軸總覽 + 五部決策漏斗 |
| 書名 | 《一個 AI 交易 Agent 的一週：71 個 Claude Skills 的策展導讀》（暫定） |
