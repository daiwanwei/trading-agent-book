# 1.2 頂部的三種徵兆

## 場景

廣度分數已經連續好幾天往下滑——不是崩跌，是那種一天比一天悶的鈍化。`market-regime-daily.yaml` 的第 1、2 步照樣跑完，`market_breadth_report` 與 `uptrend_report` 攤在桌上，但這兩份都不負責回答「風險是不是正在積累」這個問題。這時候，第 3 步「Check market top risk」才有理由被打開。

這一步在 workflow 裡標成 `optional: true`，`decision_gate: false`：不查，流程照樣往下走到第 4 步的 `exposure-coach`，只是它要合成 `allow` / `restrict` / `cash-priority` 這個姿態時，會少一份叫 `top_risk_report` 的輸入。查了，`exposure-coach` 就多一個角度可以參考；不查，也不是流程卡住，只是判斷的證據少一份。這一節要展開的，就是 `market-top-detector` 這個 skill 在這一步背後做的事，以及它跟另一個沒有排進這條 workflow、但方法論高度相關的 `ibd-distribution-day-monitor` 之間，怎麼互相印證。

## 方法論

`market-top-detector` 合成三套獨立成形的框架，出處各自不同。第一套是 O'Neil 的派發日（Distribution Day）理論，來自《How to Make Money in Stocks》：機構投資人的部位太大，沒辦法一天出清，於是留下一種特徵——指數在比前一天更高的成交量下收跌。`distribution_day_guide.md` 把條件寫死成兩條同時成立：**收盤跌幅至少 0.2%**，且**當日成交量高於前一日**。還有一種「停滯日」（stalling day）：量增，但漲幅不到 0.1%，代表機構在強勢中悄悄出貨，計分時只算半個派發日（0.5）。派發日滿 **25 個交易日**自動過期，只看這個滾動視窗內的數量。文件本身給了一張分級表：0–1 天健康、2–3 天需要留意、4 天是「O'Neil 的初步警訊」、5 天要開始減碼、6 天以上是重度派發，要積極護本。

第二套是 Minervini 的領導股惡化，出處是《Trade Like a Stock Market Wizard》與《Think & Trade Like a Champion》。核心觀察是：頭部不會一次到位，機構會先賣掉上一輪漲最兇的股票鎖利，所以真正的領導股會在指數還沒破位之前就開始鬆動。`market-top-detector` 拿一籃子成長／題材型 ETF 當領導股的代理——ARKK、WCLD、IGV、XBI、SOXX／SMH、KWEB、TAN——逐一檢查距 52 週高點的回落幅度（超過 10% 算警訊，超過 25% 算熊市區）、有沒有跌破 50 日與 200 日均線、有沒有出現一波比一波低的高點。當這籃子裡超過 60% 的 ETF 同時惡化，訊號會放大 1.3 倍——這不是單一標的的問題，是系統性的。

第三套是 Monty 的防禦類股輪動，出處是 monty-trader.com 的文章〈米国株 株式相場の天井の見極め方と下落局面でやるべきこと〉。邏輯是：頭部形成前，資金會從進攻型類股流向防禦型類股，即使整體持股比例沒變，機構已經開始收斂風險。防禦一邊是 XLU（公用事業）、XLP（民生消費）、XLV（醫療）、VNQ（不動產）；進攻一邊是 XLK（科技）、XLC（通訊服務）、XLY（非必需消費）、QQQ（那斯達克百大）。當防禦類股在 20 日滾動視窗裡的相對表現領先進攻類股 3 個百分點以上，就算強烈警訊。

三套框架各測一種不同的機構行為——賣壓的量（派發日）、賣的是什麼（領導股）、資金流向哪裡（輪動）——單獨一套都可能誤判，合起來才互補，這也是 `market_top_methodology.md` 把它們併成加權合成分數的理由。

值得先說清楚的是，`ibd-distribution-day-monitor` 對「派發日」的定義，跟上面 `market-top-detector` 用的那套，核心兩條件完全一致（跌幅 ≥0.2%、量增於前一日），但退場規則不同。`market-top-detector` 的 `distribution_day_guide.md` 只寫了一條退場規則——滿 25 個交易日自動過期；`ibd-distribution-day-monitor` 除了同樣的 25 個交易日過期，還多了一條「從派發日收盤反彈滿 5% 即失效」（預設用派發日之後的盤中高點判定，可切換成只認收盤價），且明文規定派發日當天自己的盤中高點不算數，一定要用「派發日之後」的價格才能觸發失效。反過來，`market-top-detector` 會計入的「停滯日」（量增但漲幅 <0.1%，算 0.5 個派發日），`ibd-distribution-day-monitor` 目前版本刻意不做這個判定，SKILL.md 直接寫明是 v1 範圍外。同一套 O'Neil 概念，兩個 skill 選了不同的落地細節。

## 機制

`market-top-detector` 把六個分項合成一個 0–100 分的 composite score：派發日累積（25%）、領導股健康度（20%）、防禦輪動（15%）、市場廣度背離（15%）、指數技術結構（15%）、情緒與投機（10%）。這裡延續 1.1 已經點出的方向提醒——`uptrend-analyzer` 的 SKILL.md 把兩者並排比較，寫的是「Higher = healthier」對「Higher = riskier」，`market-top-detector` 自己的報告產生器也直接寫死一句提醒：分數越高，頭部風險越高。分數落在哪一區，對應到 `report_generator.py` 給出的風險預算與建議動作：0–20 綠燈（維持 100% 正常操作）、21–40 黃燈（80–90%，收緊停損、減少新倉）、41–60 橘燈（60–75%，對弱勢部位獲利了結）、61–80 紅燈（40–55%，積極獲利了結）、81–100 危急（20–35%，最大防禦與避險）。跑一次大約需要 33 次 FMP API 呼叫，免費額度就夠；S&P 500 的 50 日均線廣度與 CBOE put/call 比率則要靠 WebSearch 手動蒐集，不是自動抓取。整段合成的結果寫進這一步的 `top_risk_report`，交給第 4 步的 `exposure-coach` 消化。

`ibd-distribution-day-monitor` 走的是另一條更窄、但更機械的路線——它只做派發日這一件事，不做六分項合成。核心輸出是 `d5_count`、`d15_count`、`d25_count`：分別數「經過天數 age_sessions ≤ N」的有效派發日紀錄，也就是實際檢查了 N+1 個交易日（含當日，age 0 到 N）。三個計數餵進一張分級表：`d25 ≤ 2` 是 NORMAL；`d25 ≥ 3` 是 CAUTION；`d25 ≥ 5`、或 `d15 ≥ 3`、或 `d5 ≥ 2`，任一成立就是 HIGH；`d25 ≥ 6`、或 `d15 ≥ 4`、或（21EMA 與 50SMA 同時跌破且 `d25 ≥ 5`），任一成立就是 SEVERE。QQQ 與 SPY 同時監控時採 QQQ 加權邏輯——任一指數 SEVERE 就整體 SEVERE，QQQ HIGH 就整體 HIGH，連 QQQ 正常但 SPY HIGH 也會把整體拉到 HIGH。這個 skill 一樣需要 FMP API key，免費額度（每日 250 次呼叫）跑一次 QQQ + SPY 就夠用。它不在 `market-regime-daily` 這條 workflow 裡，但方法論上是 `market-top-detector` 派發日分項的同源印證。

## 判讀與誤用

兩個工具都反覆提醒同一件事：數字是溫度計，不是賣出指令。`ibd-distribution-day-monitor` 的 SKILL.md 寫得直白——它產出的是風險管理建議，不是下單指令，也不負責宣告頭部已經形成，真正確認頭部要靠額外訊號（例如主要指數跌破 50 日均線、領導股同步破位）。`market-top-detector` 的歷史校準頁也留了同樣的但書：市場可以在「警戒區」停留很久才真正下跌，合成分數是決策的一個輸入，不是預測。

`historical_tops.md` 給的兩個案例可以互相對照。2022 年那一次，S&P 500 在 1 月 3 日見頂（4,796.56 點），但那斯達克早在前一年 11 月 19 日就見頂（16,057.44 點）——差了將近 11 個月。領導股代理 ARKK 更早，2021 年 2 月就已經見頂，比 S&P 500 早了 11 個月，是教科書等級的 Minervini 早期訊號。文件把當時的估計合成分數放在 68–78 分，落在紅燈區。2018 年第四季則是另一種樣貌：S&P 500 在 9 月 20 日見頂（2,930.75 點），跌幅約 20%，但這是一次修正而不是熊市——12 月見底後 V 型反彈，隔年 4 月就創了新高。文件估計那一次的合成分數只落在 47–57 分，橘燈區，不到紅燈，更不到危急。同一套框架，一次給出紅燈確認了長達近一年的領先背離，一次只給出橘燈，沒有過度反應成危急——這正是溫度計該有的樣子：讀數要跟著證據走，不是每次亮黃燈就假設要崩盤。

最常見的誤用，是把單一天的高分或單一次 SEVERE 分級當成立刻出清的訊號，而忽略這兩份報告本來就只是 `exposure-coach` 判斷姿態時的其中一項輸入，不是判斷本身。另一種誤用，是把第 3 步的「optional」讀成「不重要」——它確實可以跳過，但跳過的代價很具體：第 4 步會少一份輸入，而不是這份輸入從來沒有意義。

## 延伸閱讀

- [`skills/market-top-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-top-detector/SKILL.md)
- [`skills/market-top-detector/references/market_top_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-top-detector/references/market_top_methodology.md)
- [`skills/market-top-detector/references/distribution_day_guide.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-top-detector/references/distribution_day_guide.md)
- [`skills/market-top-detector/references/historical_tops.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-top-detector/references/historical_tops.md)
- [`skills/ibd-distribution-day-monitor/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/ibd-distribution-day-monitor/SKILL.md)
- [`skills/ibd-distribution-day-monitor/references/ibd_distribution_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/ibd-distribution-day-monitor/references/ibd_distribution_methodology.md)
