# 2.4 Kanchi：存股的紀律

## 場景

週六上午，跟平日的兩道閘完全不是同一個世界。序章已經走過一次：`swing-opportunity-daily` 是天天要跑的日內偵查隊，`core-portfolio-weekly` 是週末盤點既有持股的例行公事。這裡要深化的是另一條同樣掛在週末、卻朝著完全相反時間尺度延伸的線——[`kanchi-dividend-weekly`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/kanchi-dividend-weekly.yaml)。

它的 `estimated_minutes` 是 60，`cadence` 是 weekly，跟 `core-portfolio-weekly` 同一個節奏長度；但 `api_profile` 標成 `mixed`——不像 `swing-opportunity-daily` 整條線都靠 FMP 燒錢，也不像 `market-regime-daily` 完全免費，這條路徑一部分靠 API、一部分純算，混著走。`required_skills` 只鎖了兩支：`kanchi-dividend-sop`、`trader-memory-core`；另外四支——`value-dividend-screener`、`dividend-growth-pullback-screener`、`kanchi-dividend-us-tax-accounting`、`kanchi-dividend-review-monitor`——全部列成 `optional_skills`。

跟 `core-portfolio-weekly` 的分工，序章已經點過一句：維護既有持股是那一條的事，這一條找的是全新的候選。換一個角度看同一件事：`core-portfolio-weekly` 問的是「我手上這些配置對不對」，`kanchi-dividend-weekly` 問的是「市場上還有沒有值得加進來的名字，而且我願不願意替它背書」。兩條線唯一交會的地方，是前者的 `holdings_snapshot` 可以選擇性地餵給這條的第 4、5 步，作為既有持股的參考脈絡——但候選的盡職調查本身完全不需要它。這條線也自己框住了範圍：`when_not_to_run` 明講 v1 只處理美股上市的配息股，不涵蓋日股或其他市場，也不是在主張「Kanchi 式篩選是一套會賺錢的策略」——這是一套有紀律的候選來源程序，不是買進訊號。

而它的時間尺度，是全書五大流派裡拉得最長的一個。`kanchi-dividend-sop` 自己定的節奏只有三檔——每週 15 分鐘看股息與新聞變化、每月 30 分鐘重跑篩選、每季 60 分鐘用最新財報做深度安全複核——沒有日內、沒有盤中，連「每天」都不存在。`dividend-growth-pullback-screener` 講得更直白：這是給願意接受 5 到 10 年總報酬視角的人用的工具，短線交易（6 個月以下）不適用；`dividend_growth_compounding.md` 整份文件的例子都拉到 10 年、20 年——微軟從 2010 到 2020、Visa 從 2012 到 2022。VCP 找的是隨時可能突破的壓縮型態，Stockbee 找的是幾天內就會兌現的動能爆發；Kanchi 找的，是十年後才看得出差異的複利。

## 方法論

Kanchi 是誰？上游文件給的線索很節制，寫多少就只能說多少。`kanchi-dividend-sop` 的 `description` 把這套方法稱為「Kanchi-style dividend investing」，對應的日文原詞是「かんち式配当投資」——一套日本市場的配息投資風格，這支 skill 的工作是把它轉譯成一套可重複執行的美股操作程序。除此之外，九份素材裡唯一補上一句出處性質資訊的，是 `valuation-and-one-off-checks.md` 的一行備註：「Kanchi's original Japan-style filter uses PER x PBR」——原始版本用本益比乘股價淨值比（`PER x PBR`）做核心估值濾網。沒有生平、沒有書名、沒有訪談連結——不像 Minervini 有兩本著作可查、O'Neil 有 IBD 方法論可引、Bonde 至少在三份 SKILL.md 的 description 裡被指名——這裡能核實的只有「日本市場配息流派」與「原始估值工具是 `PER x PBR`」這兩件事，其餘不腦補。

`kanchi-dividend-sop` 把這套方法拆成五步，`kanchi-dividend-weekly.yaml` 自己稱它「Kanchi's 5-step method」。Step 1 是殖利率濾網：只認「常規」遠期殖利率——最近一次已宣告的常規股息乘上配息頻率再除以股價——刻意不用容易滯後、又會把特別股息混進去的 TTM 或 `lastDividend`。Step 2 是成長與安全性，依產業分派不同的判斷模組，銀行、受監管公用事業各有專屬邏輯。Step 3 是估值，同樣依產業對應不同倍數（見下段）。Step 4 是回顧性的一次性項目濾網，抓資產出售、訴訟和解、稅務認列這類墊高獲利的一次性效果；Step 4b 補上前瞻性的一半，掃描尚在發生或剛發生的結構性事件——併購、股權稀釋、槓桿變化——回顧性的 Step 4 抓不到這些。Step 5 才談進場：殖利率高於五年均值加上一個 alpha（預設 +0.5pp），或估值倍數回到目標，兩者任一觸發，分三批 40%、30%、30% 進場；若還有未解決的下單前阻斷項，或 `t1_blocked` 成立，第一批會被卡住或縮到 20% 以內的試單。

**原著 vs 實作。** 唯一能拿原始版本跟這裡的實作直接對照的地方，就是 Step 3 估值。原始的日本版 Kanchi 濾網統一用 `PER x PBR`；`valuation-and-one-off-checks.md` 把它按美股產業拆成四種：銀行與保險改用 `P/TBV`（有形帳面價值），文件說明理由是美股銀行的有形帳面比 `PER x PBR` 更站得住腳的估值錨；REIT 用 `P/FFO` 或 `P/AFFO`；資產輕量的成長股用遠期 `P/E` 搭配 `P/FCF` 與五年區間；成熟的現金牛型公司則看 `P/FCF` 搭配殖利率相對五年均值的位置。文件補了一句處理分歧的原則：幾個指標對不上的時候，判 `HOLD-FOR-REVIEW`，不要硬湊出一個 `PASS`。原著給的是一把統一的尺；實作換成了四把不同的尺——理由很直接，`PER x PBR` 量不出美股銀行股真正的價值錨。

兩支輔助 screener 不是 Kanchi SOP 的一部分，是餵候選給它的兩條不同管道，服務兩種不同的存股目標。`value-dividend-screener` 找的是「現在就要領息」的名字：`P/E` 低於 20、`P/B` 低於 2。殖利率門檻是一個文件跟程式碼對不上的活例子——`screen_dividend_stocks.py` 裡 `screen_stocks()` 的實際呼叫參數是 `dividend_yield_min=3.0`，跟兩階段篩選、FMP-only 篩選兩段 workflow 步驟說明裡寫的「3%+」「>=3.0%」，以及輸出 JSON 的 `metadata.criteria` 互相一致；但 SKILL.md 的報告範本、`screening_methodology.md` 的正式門檻表，以及 SKILL.md「Advanced Usage」段落裡那組已經過期的程式碼示例，寫的都是 3.5%。git 歷史證實這支腳本原本確實是 3.5%，在加入 FINVIZ 整合的那次修改裡改成了 3.0%，文件沒有跟著更新。三年期股息成長門檻是同一種落差的第二個例子：`screening_methodology.md` 寫 3 年 CAGR 至少 5%，但腳本裡真正擋人的硬性條件是 `div_cagr < 4.0` 就跳過——實際門檻是 4.0%，不是 5%。營收與 EPS 仍要求正向趨勢。`dividend-growth-pullback-screener` 反過來找「現在殖利率不高、但成長快」的名字：三年股息年複合成長率至少 12%、起始殖利率門檻只要 1.5%，鎖定的是還在回檔的強勢股——`RSI` 40 以下。這兩種目標，相當貼近 `default-thresholds.md` 自己列出的三檔 profile 兩端：income now 殖利率下限 4.0%、growth first 只要 1.5–2.5%。

## 機制

三支 skill 的資料來源都以 FMP 為主，程度不一。`kanchi-dividend-sop` 只有 `build_entry_signals.py` 明講需要 `FMP_API_KEY`；`value-dividend-screener`、`dividend-growth-pullback-screener` 兩支輔助 screener 都支援 FINVIZ Elite 兩階段篩選——先用 FINVIZ 粗篩、FMP 再做細部分析，能把 FMP 呼叫量壓低六到九成，但兩支都聲明 FINVIZ 是選配，FMP 才是硬性前提。這正是 `api_profile: mixed` 的來歷。

`default-thresholds.md` 把 Step 1、Step 2 的預設數字攤成一張表：遠期殖利率門檻 3.5%（Step 1 核心濾網，跟 `value-dividend-screener` 那組 3%、3.5% 是各自獨立的預設值，不是同一個數字）；極端殖利率 8.0% 以上強制進深度覆核；EPS 支付率上限 70%（70–85% 進入 caution 區）；FCF 支付率上限 80%（超過 100% 視為高風險）；利息覆蓋倍數下限 3.0x（低於 2.5x caution）。組合限制另外列了一組：最多 15 到 30 檔持股、單一部位成本不超過 8%、單一產業不超過 25%、REIT、電信、公用事業合計的高殖利率桶不超過 35%——這些都是預設值，使用者可以覆寫，沒有明講覆寫理由時就照這張表走。

`build_entry_signals.py` 有兩個容易被忽略的必要參數。`--yield-floor` 是強制項——這是 Step 1 的殖利率閘門，不給這個參數，每一列都會 fail-safe 到 `STEP1-RECHECK`，沒有任何一列有機會拿到 PASS 級的判定。`--events-json` 不給的話，Step 4b 的結構性事件掃描對每一列都視為 `SKIPPED`；如果同一列的 Step 5 訊號已經觸發（`TRIGGERED`），這個 `SKIPPED` 會把它封頂在 `HOLD-REVIEW`——絕不會安靜地放過。

`kanchi-dividend-weekly.yaml` 六步的骨架：第 1、2 步分別是兩支輔助 screener，`optional: true`，各自產出 `high_yield_candidates`、`pullback_candidates`；第 3 步 `kanchi-dividend-sop` 才是核心，`decision_gate: true`，同時吃前兩步的產出，但 `manual_review` 講得很清楚——兩支 screener 都是可選的，一份手動提供的股票清單，走第 3 步一樣有效。序章已經記過這一步的判定分級：`CLEAN-PASS`、`PASS-CAUTION`、`CONDITIONAL-PASS` 可以往下走，`HOLD-REVIEW`、`STEP1-RECHECK`、`FAIL` 就地停住。這裡補一層還沒講過的細節——`STEP1-RECHECK` 跟 `FAIL` 不是同一種停止：殖利率卡在門檻附近（正負 0.20pp 以內）又缺乏可信來源確認最新股息，只會判 `STEP1-RECHECK`，絕不直接判 `FAIL`；真正的硬性 `FAIL` 留給股息政策浮動、確認減配、或停止配息這幾種情況。`HOLD-REVIEW` 則是另一條路徑的終點——調整後 EPS 抓不到資料、四季內完成的併購讓 GAAP EPS 失真又沒走調整路徑、或 Step 4b 掃到重大結構性事件，都會落在這一級，而不是直接判死。

第 4、5 步都是可選的：`kanchi-dividend-us-tax-accounting` 給稅務與帳戶配置建議，`manual_review` 特別提醒這只是參考，不是權威判斷，行動前要找稅務專業或券商對帳單核實；`kanchi-dividend-review-monitor` 對既有持股跑異常檢查，產出 `review_queue`——第 4、5 步都會用到 `core-portfolio-weekly` 的 `holdings_snapshot`；但一支還沒持有的全新候選本來就沒有異常監控要看的持股證據，第 5 步會直接跳過。第 6 步 `trader-memory-core` 收斂：把 `kanchi_candidates` 登記成 `IDEA` 論點，再用 `link_report()` 把第 3 步存下的股票備忘錄（一頁式、手寫，`stock-note-template.md` 格式）附加上去。這裡有個容易漏掉的地方——備忘錄不會自動嵌進 `kanchi_candidates` 的 JSON 裡，只存成檔案；漏了 `link_report()` 這道呼叫，論點的 `linked_reports` 裡就沒有這份備忘錄的紀錄，即使它確實寫過。跟序章記下的規則一樣，這一步最多只能到 `IDEA` 或 `ENTRY_READY`，真實成交之前，狀態機不會相信任何論點已經生效。

## 判讀與誤用

高殖利率不等於便宜，這是 Kanchi SOP 最先擋的陷阱。`default-thresholds.md` 把 8.0% 以上的殖利率標成強制深度覆核的門檻；`valuation-and-one-off-checks.md` 的 Step 4 checklist 列了五個一次性項目——資產出售或處分利得、訴訟和解或稅務一次性效果推高 EPS、毛利擴張跟營收品質對不上、管理層反覆把關鍵獲利項目標成「非經常性」、股息靠舉債或資產變現撐著——五項裡有兩項以上是 `YES`，就要降評或直接拒絕。Step 1 的 `special_dividend_flag`、`variable_policy_flag`、`cut_flag`、`suspension_flag` 從資料端就先攔掉了另一種常見誤讀：把特別股息、浮動配息政策、已經減配或停止配息的名字，誤算進穩定的常規殖利率裡。

回檔進場不等於接刀，這是 `dividend-growth-pullback-screener` 一直在強調的分界。`rsi_oversold_strategy.md` 講得直接：`RSI` 低不是買進的理由，是時機——先靠 12% 以上的股息複合成長率、正向的營收與 EPS 趨勢、低於 100% 的支付率把公司篩過一輪，`RSI` ≤40 只負責決定「現在」是不是好的進場點。文件自己舉的反例最有說服力：奇異（GE）在 2017 到 2018 年間反覆出現 `RSI` 超賣訊號，但同一時間股息從 0.96 美元一路砍到 0.12 美元——基本面已經惡化，`RSI` 訊號因此完全不可靠。`RSI` 越極端，建議的進場方式反而越保守：低於 30 的極端超賣區，要等 `RSI` 回升過 30 再進、先用五成部位試單；30 到 35 之間可以進滿倉，但停損放寬到 5% 到 8%；36 到 40 的輕度回檔，停損可以收緊到 3% 到 5%。

這一流派的賣出紀律不在這一節的範圍——`kanchi-dividend-review-monitor` 的 T1 到 T5 異常分級屬於 `core-portfolio-weekly` 管既有持股的地界，一句帶過即可。

## 延伸閱讀

- [`skills/kanchi-dividend-sop/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/kanchi-dividend-sop/SKILL.md)
- [`skills/kanchi-dividend-sop/references/default-thresholds.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/kanchi-dividend-sop/references/default-thresholds.md)
- [`skills/kanchi-dividend-sop/references/valuation-and-one-off-checks.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/kanchi-dividend-sop/references/valuation-and-one-off-checks.md)
- [`skills/value-dividend-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/value-dividend-screener/SKILL.md)
- [`skills/value-dividend-screener/references/screening_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/value-dividend-screener/references/screening_methodology.md)
- [`skills/dividend-growth-pullback-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/dividend-growth-pullback-screener/SKILL.md)
- [`skills/dividend-growth-pullback-screener/references/rsi_oversold_strategy.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/dividend-growth-pullback-screener/references/rsi_oversold_strategy.md)
- [`skills/dividend-growth-pullback-screener/references/dividend_growth_compounding.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/dividend-growth-pullback-screener/references/dividend_growth_compounding.md)
