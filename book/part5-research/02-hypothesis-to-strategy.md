# 5.2 從假說到策略草稿

## 場景

5.1 留下的原料分兩批：`tickets/exportable/`、`tickets/research_only/` 底下一批批 ticket YAML，外加一份可選的 `hints.yaml`。`edge-concept-synthesizer` 先接手，跑一次 `scripts/synthesize_edge_concepts.py --tickets-dir /tmp/edge-auto/tickets --hints /tmp/edge-hints/hints.yaml --output /tmp/edge-concepts/edge_concepts.yaml --min-ticket-support 2`，輸出資料夾裡多出一份 `edge_concepts.yaml`。`edge-strategy-designer` 接著讀這份檔案，跑 `scripts/design_strategy_drafts.py --concepts /tmp/edge-concepts/edge_concepts.yaml --output-dir /tmp/strategy-drafts --risk-profile balanced`，多出一批 `strategy_drafts/*.yaml` 與一份 `run_manifest.json`；再加上 `--exportable-tickets-dir`，還會多出 `exportable_tickets/*.yaml`，供下游的 `export_candidate.py` 使用。`SKILL.md` 把 `edge-strategy-designer` 的位置寫得很白：它「sits after concept synthesis and before pipeline export validation」——夾在概念合成與匯出驗證之間，自己不做審查。兩份 `SKILL.md` 各自的 Prerequisites 段落，把這條先後關係釘得更死：`edge-concept-synthesizer` 要吃的是偵測器輸出的 ticket YAML 目錄（`tickets/exportable`、`tickets/research_only`），`hints.yaml` 只是可選項；`edge-strategy-designer` 要吃的則是前一步產出的 `edge_concepts.yaml`——沒有這份檔案，後一個 skill 連跑都跑不起來。

## 方法論

兩個 skill 隔著一層才互相接手，理由寫在各自的 Overview 與 When to Use 裡。`edge-concept-synthesizer` 的 Overview 說得直接：「Create an abstraction layer between detection and strategy implementation」——在偵測與策略實作之間插一層抽象。When to Use 列了三個觸發條件：手上一堆原始 ticket、需要 mechanism 層級的結構；想避免 ticket 直接對應策略造成過擬合；想在寫策略之前先做 concept 層級的審查。三條理由指向同一件事：單一 ticket 只代表某一天某一檔股票的一次觀察，若讓它直接長成策略草稿，草稿等於是照著這一次巧合量身訂做，換一批資料就站不住。

`edge-strategy-designer` 的 Overview 換了位置：「Translate concept-level hypotheses into concrete strategy draft specs.」它翻譯的對象已經是抽象化過的 concept，不再是原始 ticket。When to Use 三條分別是：手上有 `edge_concepts.yaml`、需要策略候選；想要每個 concept 產出多個變體（core／conservative／research-probe）；想要可選的可匯出 ticket 檔。抽象與具體因此分居兩層：concept 層回答「這個機制成不成立」，靠許多筆 ticket 的共同支持撐住 thesis；draft 層回答「這個機制寫成規則要下什麼參數」，一份 concept 底下攤開成好幾份帶著具體停損、報酬比、部位大小的候選，供之後回測與審查逐一檢驗。換句話說，從 ticket 到 concept 是多對一的收斂，把統計上的巧合過濾成有共同支持的機制；從 concept 到 draft 又是一對多的展開，把一個機制翻譯成好幾份各自可以被否掉的具體規則。夾在中間的這一層抽象，兩頭都不白費。

## 機制

`edge_concepts.yaml` 的骨架照 `concept_schema.md`：頂層是 `generated_at_utc`、`as_of`、記錄輸入來源與 ticket 數量的 `source`（底下再分 `tickets_dir`、`hints_path`、`ticket_file_count`、`ticket_count` 四個欄位）、`concept_count`，底下是 `concepts` 陣列。每個 concept 必有 `id`、`title`、`hypothesis_type`、`mechanism_tag`、`regime`，再往下四個區塊——`support`（`ticket_count`、`avg_priority_score`、`symbols`、`entry_family_distribution`、`representative_conditions`，若靠 `--promote-hints` 促升了合成 ticket，才會多出 `real_ticket_count`、`synthetic_ticket_count`）、`abstraction`（`thesis` 與 `invalidation_signals`）、`strategy_design`（`playbooks`、`recommended_entry_family`、`export_ready_v1`）、`evidence`（`ticket_ids`、`matched_hint_titles`，合成 ticket 同樣多出 `synthetic_ticket_ids`）。Design Rule 寫死兩條：`abstraction` 必須同時有 `thesis` 與明確的 `invalidation_signals`；`export_ready_v1` 只有在建議的 `entry_family` 目前被 pipeline 介面 v1 支援時才能是 true。`hypothesis_type` 認得的九個值裡，`research_hypothesis` 是留給促升 ticket 裡關鍵字判斷不出具體類型的那一批用的 fallback。

概念怎麼從一堆 ticket 收斂出來，`SKILL.md` 的 Workflow 給了五步：收集偵測器產出的 ticket YAML；可選地帶上 `hints.yaml` 做上下文比對；跑合成腳本；去重——「merge same-hypothesis concepts with overlapping conditions (containment > threshold)」，只在同一個 `hypothesis_type` 內比對，門檻用 `--overlap-threshold` 調（Quick Commands 給的示範值是 0.6，或用 `--no-dedup` 整個關掉）；最後才是人工審查，只把高支持度的 concept 往下送進策略設計。

`edge-strategy-designer` 的 Workflow 分七步：載入 `edge_concepts.yaml`；選一種風險姿態（`conservative`、`balanced`、`aggressive`，Quick Commands 顯示這是整次執行只下一次的旗標）；為每個 concept 生成多個變體——`core`、`conservative`、`research-probe`；套用 `HYPOTHESIS_EXIT_OVERRIDES`，依 `hypothesis_type`（breakout、earnings_drift、panic_reversal 等）分別微調停損、報酬風險比、時間停損與移動停損；把報酬風險比夾在 `RR_FLOOR=1.5` 之上，`SKILL.md` 寫明這是為了「prevent C5 review failures」；產出符合 v1 介面的可匯出 ticket；最後把可匯出 ticket 交給 `edge-candidate-agent` 的 `export_candidate.py`。`strategy_draft_schema.md` 給的樣本草稿是一份 `core` 變體的 breakout 策略，帶著 `stop_loss_pct: 0.07`、`take_profit_rr: 3.0`、`time_stop_days: 20`，外加 `risk.position_sizing`、`risk.risk_per_trade`、`risk.max_positions` 三個部位控管欄位，以及 `validation_plan`（`period`、`hold_days`、`success_criteria`）——每份草稿都附著自己要怎麼被回測驗證的計畫。schema 文件另外提醒一句：`risk_profile` 會原樣寫進每份草稿，方便日後追溯這份倉位限制是在哪種風險姿態下算出來的。

## 判讀與誤用

容易被誤讀的地方分兩層。第一層是 concept 本身：`export_ready_v1: true` 說的是「建議的 `entry_family` 目前被 pipeline 介面 v1 支援」——`concept_schema.md` 的 Design Rule 原句如此——不是「這個機制已經被驗證能賺錢」。`thesis` 寫得再完整，仍然是待否證的假說。`real_ticket_count`、`synthetic_ticket_count`、`synthetic_ticket_ids` 三個欄位只在用了 `--promote-hints` 且真的存在合成 ticket 時才出現，反過來讀，一個 concept 底下看不到這三個欄位，代表它完全由真實 ticket 撐起來，不是資料被省略。

第二層是 draft，這裡藏著一個容易撞名的陷阱。`--risk-profile` 的三個合法值是 `conservative`、`balanced`、`aggressive`，整次執行只選一種；而每個 concept 底下生成的變體名稱裡，剛好也有一個叫 `conservative`——`SKILL.md` 的 When to Use 原句是「multiple variants (core/conservative/research-probe) per concept」。同一個詞在這裡出現兩次，指的是兩層完全不同的東西：一個是整批草稿共用的風險姿態，一個是同一個 concept 底下某一份具體草稿的名字。把兩者混為一談，很容易把「用 conservative 風險姿態跑出來的 core 草稿」誤讀成「這份草稿就是 conservative 變體」。

最後，`strategy_draft_schema.md` 的「Export Ticket Output」一節寫明，只有指定了 `--exportable-tickets-dir`、而且草稿本身 `export_ready_v1` 為真，才會多產出一份相容 `export_candidate.py` 的 ticket YAML；沒被匯出的草稿不是被丟棄，只是還沒有資格進下一關——它要先通過審查與否證，才有機會被叫做策略。

## 延伸閱讀

- [`skills/edge-concept-synthesizer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-concept-synthesizer/SKILL.md)
- [`skills/edge-concept-synthesizer/references/concept_schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-concept-synthesizer/references/concept_schema.md)
- [`skills/edge-strategy-designer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-designer/SKILL.md)
- [`skills/edge-strategy-designer/references/strategy_draft_schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-designer/references/strategy_draft_schema.md)
