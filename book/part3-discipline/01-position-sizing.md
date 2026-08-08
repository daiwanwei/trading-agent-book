# 3.1 風險先行的部位計算

## 場景

`validated_setups` 剛從 step 7 送出來——這批候選已經在週線圖上被 `technical-analyst` 篩過一輪，結構不明確的都已經淘汰。`swing-opportunity-daily.yaml` 第 8 步接手，`skill: position-sizer`，`consumes: validated_setups`，`produces: position_sizing`。這一步的 `decision_gate` 標成 `false`——它不否決任何候選，只回答一個更窄的問題：這檔如果要買，買幾股。

這個問題聽起來像技術細節，其實決定了一筆交易能不能活過一次連續虧損。部位計算的順序是反過來的：不是先看股價多少、帳戶還有多少現金，算出能買幾股，而是先定「這一筆願意虧多少錢」，再用停損距離反推股數。這個「風險先行」的順序，一旦寫進 `position_sizing`，之後不會再被重算——它會在 step 10 `trader-memory-core` 登記投資仮說時被核對一次「風險是否與 position-sizer 的輸出一致」，在 step 11 `pre-trade-discipline-gate` 下單前的紀律檢查裡，再核對一次「部位大小」。這一節要展開的，就是 `position-sizer` 背後的三種算法，以及當交易標的換成期貨、`futures-position-sizer` 又用了什麼不同的算法。

## 方法論

`sizing_methodologies.md` 開頭把這件事講得很直接：部位大小是決定長期存活的單一最重要因素——一次好的選股配上壞的部位計算能毀掉一個帳戶；普通的選股配上正確的部位計算，反而能保住資本，等下一次機會。文件收錄三種算法，出處各自不同，適用情境也不同。

第一種是固定比例法（Fixed Fractional），由 Van Tharp 普及，Mark Minervini 與 William O'Neil 都嚴格奉行。公式是 `risk_per_share = entry_price - stop_price`、`dollar_risk = account_size * risk_pct / 100`、`shares = int(dollar_risk / risk_per_share)`——CLI 預設整股模式一律無條件捨去，只有搭配 `--fractional --share-precision N` 且券商支援時才捨去到指定小數位，同樣不會無條件進位。文件的範例：$100,000 帳戶，進場 $155.00，停損 $148.50，每股風險 $6.50，用 1% 風險額度算，$1,000 ÷ $6.50 得到 **153 股**，部位價值 $23,715（帳戶的 23.7%）。風險等級表把 0.25–0.50% 列為機構等級的保守操作，0.50–1.00% 是 Minervini 建議的區間，1.00–1.50% 用在已驗證的系統，1.50–2.00% 是多數策略的上限，超過 2% 直接標成「危險」。

第二種是 ATR 法，源自 1983 年 Richard Dennis 的海龜交易員系統，用波動度取代固定金額停損。公式是 `stop_distance = atr * atr_multiplier`、`stop_price = entry_price - stop_distance`、`shares = int(dollar_risk / stop_distance)`。倍數對應不同持有週期：1.0 倍是當沖等級的緊停損，1.5 倍是 2–5 天的波段，2.0 倍是海龜交易員的原始設定、也是多數波段交易的預設，2.5 倍拉到 2–8 週的部位交易，3.0 倍用在跨月的趨勢跟隨。文件用同一個帳戶示範：進場 $155.00，ATR(14) 是 $3.20，用 2.0 倍，停損距離 $6.40，1% 風險額度一樣是 $1,000，除下來是 **156 股**——同一筆風險預算，換成波動度算法多買了 3 股，因為停損比固定停損法（$6.50）略窄。

第三種是 Kelly 公式，1956 年 John L. Kelly Jr. 在貝爾實驗室提出，算的是給定勝率與賠率下，數學上最適合投入的資金比例。公式是 `R = avg_win / avg_loss`、`kelly_pct = W - (1 - W) / R`、`half_kelly = kelly_pct / 2`。文件的範例：勝率 55%、平均獲利 $2.50、平均虧損 $1.00，R = 2.5，Kelly = 0.55 − 0.45/2.5 = 0.37，即 37%；半 Kelly 是 18.5%，套在 $100,000 帳戶上是 $18,500 的風險預算。文件同時給了負期望值的例子：勝率 30%、平均獲利 $1.00、平均虧損 $1.50，R = 0.667，Kelly = 0.30 − 0.70/0.667 = −0.75，這種結果會被硬性砍到 0%——意思不是「少冒險」，是「這套系統不該被交易」。文件建議的順序：新策略先用 1% 固定比例法起步，跨不同波動度的標的比較時換 ATR 法，累積滿 100 筆以上交易紀錄後把 Kelly 當成風險上限的檢查，任何算法算出來的股數，最後都要再套一層組合限制。

## 機制

`position-sizer` 的 CLI 把三種算法包進同一支 `position_sizer.py`：輸入 `--entry`、`--stop`（或 `--atr`/`--atr-multiplier`，或 `--win-rate`/`--avg-win`/`--avg-loss`）、`--account-size`、`--risk-pct`，輸出的 JSON 裡有 `final_recommended_shares`、`final_position_value`、`final_risk_dollars`、`final_risk_pct`，還有一個 `binding_constraint` 欄位，標明最後是哪個限制卡住了股數。

風險算出來的股數只是候選之一，`sizing_methodologies.md` 另外定義兩層組合限制：單一部位上限 `max_shares = int(account_size * max_position_pct / 100 / entry_price)`；單一產業上限先算 `remaining_pct = max_sector_pct - current_sector_exposure`，再 `max_shares = int(remaining_pct / 100 * account_size / entry_price)`，三個候選股數取最小值。`SKILL.md` Step 5 給的範例把 `max-position-pct` 設 10%、`max-sector-pct` 設 30%、`current-sector-exposure` 設 22%——沿用方法論範例的 155/148.50 這筆交易套進去可以算出：部位上限 $10,000 ÷ $155 ≈ 64 股，產業上限剩餘的 8% 額度 $8,000 ÷ $155 ≈ 51 股，都比風險算出的 153 股更緊，51 股的產業限制會成為 `binding_constraint`——這正是「最嚴格的限制勝出」。

股票以外，`futures-position-sizer` 是另一個獨立的 skill，不是把 `position-sizer` 換個參數重跑。原因是期貨有乘數：同樣是最小跳動的一檔，`ES` 換算下來是 $12.50（乘數 50、跳動 0.25 點），`NQ` 只有 $5.00（乘數 20、跳動同樣 0.25 點），`ZB` 卻要 $31.25（乘數 1000、跳動只有 1/32 點）——直接把股票算法套在期貨上，風險可能被低估或高估 20 到 1000 倍。公式是 `risk_per_contract = stop_distance * multiplier * fx_rate`、`contracts = floor(risk_budget / risk_per_contract)`；`floor` 用的是精確有理數運算而不是浮點數除法，確保口數乘回風險絕對不會超過預算。文件的範例：`ES` 做多，進場 5000.25、停損 4980.00，停損距離 20.25 點（81 檔），乘數 50，每口風險 $1,012.50；帳戶 $100,000、風險 2%，風險預算 $2,000，算出 1 口，實際風險 $1,012.50（帳戶的 1.01%）。若風險比例只設 1%，風險預算 $1,000 連一口的門檻都不夠，狀態會回報 `NO_TRADE`、原因 `risk_below_one_contract`——但停損距離、每口風險這些數字仍完整寫進報告，只是交易被拒絕。乘數、tick size、tick value 這些規格來自一張涵蓋 23 個市場的核心對照表，每一列都對照交易所自己的官方合約規格頁或規則手冊（CME、Cboe、ICE）逐一驗證，不採信部落格或彙整網站的二手數字。

在 Shapiro 訊號鏈裡，`futures-position-sizer` 卡在管線第 4 步——把 `contrarian-setup-gate` 判定 `READY_FOR_PLAN` 之後的方向與失效價，換算成合約口數；完整的管線怎麼走，留到第二部 2.5 再展開。兩個 skill 有一個共同點：都不需要 API key，純本地計算，離線可跑。

## 判讀與誤用

部位計算保護的不是勝率，是單筆虧損的上限。`SKILL.md` 把這件事寫進第一條核心原則：「Survival first」——部位計算存在的目的是撐過連續虧損，不是把獲利最大化。

最常見的自欺，是把 risk-pct 調大。`SKILL.md` 的第二條原則是預設 1% 風險、非有特殊理由不超過 2%；`sizing_methodologies.md` 用連續 10 筆虧損算給你看差距：每筆 1% 風險，10 連虧的回撤是 9.6%，還能恢復；每筆 5%，回撤 40.1%，傷筋動骨；每筆 10%，回撤 65.1%，帳戶等於報廢。風險等級表裡超過 2% 直接標成「危險」，理由寫得很白：破產機率隨風險比例急遽上升。

Kelly 公式的風險在於它算出的是「數學上最適合」，不是「實務上安全」。全額 Kelly 追求長期幾何成長最大化，代價是極端波動，50% 以上的回撤並不罕見，文件直接寫「沒有專業基金真的用全額 Kelly」；半 Kelly 拿到大約四分之三的理論成長率，回撤降到溫和的 25–35%，是唯一被推薦拿來實戰的版本——`SKILL.md` 第六條原則就是「Half Kelly」。負期望值時 Kelly 會被砍到 0%，那不是保守的建議，是「別碰」的判決；把負 Kelly 硬解讀成「至少小額下注」，是對這個公式最常見的誤讀。

再往上一層，`SKILL.md` 提醒帳戶總風險（portfolio heat）不該超過 6–8%——單筆算得再精準，同時開太多部位一樣會把帳戶暴露在超額風險下；虧損的不對稱性也是同一個道理，50% 的虧損需要 100% 的獲利才能打平，這正是為什麼部位計算和停損紀律，比選股本身更決定長期存活。期貨那一邊的誤用更具體：把 `futures-position-sizer` 回報的 `NO_TRADE` 當成程式錯誤而略過警訊，其實那是刻意設計的 fail-closed 行為——沒有明確停損就不計算口數，風險預算不夠買一口也絕不會偷偷湊數硬算出一口。

## 延伸閱讀

- [`skills/position-sizer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/position-sizer/SKILL.md)
- [`skills/position-sizer/references/sizing_methodologies.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/position-sizer/references/sizing_methodologies.md)
- [`skills/futures-position-sizer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/futures-position-sizer/SKILL.md)
- [`skills/futures-position-sizer/references/sizing-methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/futures-position-sizer/references/sizing-methodology.md)
- [`skills/futures-position-sizer/references/futures-contract-specs.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/futures-position-sizer/references/futures-contract-specs.md)
