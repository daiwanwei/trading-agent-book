# 2.2 O'Neil：CANSLIM 成長股

## 場景

07:35 那兩道閘怎麼亮燈、`swing-opportunity-daily` 怎麼接手，2.1 已經講過。第 2 步 `vcp-screener` 收工之後，第 3、4 步的 Stockbee 篩子跟第 5 步的 `canslim-screener` 一起攤開——五支偵查隊裡，這是第四支，也是唯一同時碰基本面跟技術面的一支。`skill: canslim-screener`，`decision_gate: false`，`optional: true`，`produces: canslim_candidates`：跟第 2 步不一樣，這一步不是必跑項；跳過它，流程照樣往下走到第 7 步的週線驗證，只是候選清單裡少一份用財報數字撐腰的名單。

VCP 問的是「型態壓縮到臨界點了沒有」，純粹看價與量；CANSLIM 問的是另一個問題——這檔股票的動能背後，公司本身是不是真的在加速成長。Agent 想知道的不是「圖形漂不漂亮」，而是「這波漲勢有沒有基本面撐得住」。這正是 O'Neil 留給後人的整套系統：把「好股票」拆成七個字母，每個字母各自可以量化驗證。

## 方法論

CANSLIM 是 William O'Neil 提出的成長股選股系統，出處是《How to Make Money in Stocks》（第四版，2009）——`canslim_methodology.md` 開宗明義引用 IBD 對 1953 年至今大牛股的回溯研究：同時具備七項特徵的股票，未來 1 到 3 年平均漲幅落在 100–300%，不少個案超過 1,000%。`canslim-screener` 目前跑的是 Phase 3.1，七個字母全實作，用 O'Neil 的原始權重：C（Current Earnings）15%、A（Annual Growth）20%、N（Newness）15%、S（Supply/Demand）15%、L（Leadership/RS Rank）20%、I（Institutional）10%、M（Market Direction）5%——A 跟 L 並列最大權重。

C 是當季每股盈餘（EPS）年增率，O'Neil 的原始門檻是「至少 18–20%」；`scoring_system.md` 把這條規則接上營收年增率一起計分：EPS 年增 ≥50% 且營收年增 ≥25% 給滿分 100；EPS 30–49% 且營收 ≥15% 給 80 分；EPS 18–29%（踩到 O'Neil 的最低門檻）且營收 ≥10% 給 60 分；EPS 10–17% 只有 40 分；低於 10% 或轉負，0 分。A 是三年期 EPS 複合成長率（CAGR），O'Neil 原文說得更嚴——「過去三年，每一年都要成長 25% 以上」；量化實作把它折算成一個聚合指標：CAGR ≥40% 且三年沒有衰退年（stable）給基礎 90 分，30–39% 給 70 分，25–29%（踩到門檻）給 50 分，15–24% 給 30 分，低於 15% 或波動不穩定，0 分；穩定成長再加 10 分，但若營收 CAGR 低於 EPS CAGR 的一半，整體分數要打八折——這是防堵「靠回購灌水 EPS」的品質檢查。

N 看股價離 52 週高點多近，O'Neil 的邏輯是創新高代表沒有套牢賣壓：距離高點 5% 以內、且新高伴隨爆量（高於均量 40–50% 以上）給 100 分；10% 以內且有爆量 80 分；15% 以內或有爆量 60 分；25% 以內 40 分；超過 25% 只剩 20 分——新產品、新管理層等催化劑訊號只是加分項，不是主分數。S 是量能供需分析：抓過去 60 個交易日，把上漲日均量除以下跌日均量，比值 ≥2.0 是強力吸籌，給 100 分，1.5–2.0 給 80 分，1.0–1.5 中性給 60 分，0.7–1.0 給 40 分，0.5–0.7 是派發訊號給 20 分，低於 0.5 給 0 分。L 是相對強度，O'Neil 原話是「買 RS 評等 80 分以上的股票，避開低於 70 的落後股」；`canslim-screener` 自己算一套加權 RS——`Weighted RS = 0.40 × rel_3m + 0.30 × rel_6m + 0.30 × rel_12m`，近三個月表現權重最高，預設對比 `^GSPC`，可用 `--rs-benchmark` 換成 SPY、QQQ 等——算出的 RS 落點分五級：90 以上 100 分，80 以上 80 分，70 以上 60 分，60 以上 40 分，低於 60 只有 20 分。I 是機構持股，O'Neil 講的是一個甜蜜點：50–100 個機構持有人、持股佔比 30–60%，命中就是滿分 100；如果持股名單裡出現波克夏（Berkshire Hathaway）、Baupost、潘興廣場（Pershing Square）等知名機構，額外加 10 分。

M 是市場方向，O'Neil 的名言是：「你可以看對一檔股票，卻看錯大盤，一樣賠錢——四分之三的股票會跟著大盤走。」`market_calculator.py` 拿標普 500 距 50 日 EMA 的百分比分出五個桶：站上 EMA 2% 以上是強勢多頭；0% 到 2% 是多頭；-2% 到 0% 是盤整；-5% 到 -2% 是空頭；跌破 -5% 或 VIX 高於 30，直接判定熊市。強勢多頭疊加 VIX 低於 15 給滿分 100；一般多頭搭配 VIX 低於 20 給 80 分；單純多頭 60 分；盤整 40 分；空頭 20 分；熊市（或 VIX>30）直接 0 分——這是一條硬規則，M=0 的時候，不管另外六個字母多高分，都不准買。這正是第一部兩節分別展開的問題：1.2 節 `market-top-detector` 用派發日計數量化機構出貨的壓力，1.3 節 `ftd-detector` 判定一波反彈夠不夠格被視為機構回補——CANSLIM 的 M 分量不是另外發明一套市場判斷，是 O'Neil 同一本書裡的同一個問題，在這個 skill 裡的簡化實作。`market_calculator.py` 的公式還留了一個可選加分項——`follow_through_day_detected` 命中加 10 分，它的定義（漲幅至少 1.25%、成交量高於前一日、出現在反彈的 Day 4–10 窗口）跟 1.3 節 `ftd-detector` 判定 FTD 的三個數字完全一致；只是這裡它只是一個 +10 的加分選項，不是像 1.3 節那樣拆成完整的五態狀態機。

**原著 vs 實作。** 把 `canslim_methodology.md` 的敘述跟 `scoring_system.md` 的公式並排看，能看出幾個真正的落差。第一個落差在 A 分量：O'Neil 原文的規則是「過去三年，每一年都要成長 25% 以上」——這是逐年門檻；但實際計分只算三年期 CAGR 加一個「有沒有衰退年」的穩定性檢查，不驗證每一年是否個別站上 25%。一檔股票如果前兩年 EPS 完全沒有成長（0%）、第三年才暴衝 300%——EPS 從 1.00 元、1.00 元、1.00 元衝到 4.00 元，三年 CAGR = (4.00/1.00)^(1/3) − 1 ≈ 58.7%，落在「≥40%」的 90 分級距，且因為沒有任何一年是負成長，還能再加 10 分穩定性獎勵，封頂在 100 分——這在 O'Neil 逐年門檻的原意裡，前兩年完全不合格，實作的聚合指標卻給出滿分。第二個落差在 C 分量：O'Neil 引用的原始規則只有一句「EPS 年增至少 18–20%」，沒有提到營收；`canslim_methodology.md` 自己在「為什麼重要」段落把營收驗證列成一項獨立的品質檢查，但 `scoring_system.md` 把這項檢查直接焊進計分公式本身——60 分以上每一級都同時要求 EPS 與營收同步達標，把一條軟性提醒變成了硬性計分門檻。第三個落差更整體：`canslim-screener` `SKILL.md` 自己在「Data Source Attribution」寫明，方法論出處是 O'Neil《How to Make Money in Stocks》，但計分系統另外標注「Adapted from IBD MarketSmith proprietary system」——換句話說，七個字母該不該量化出自 O'Neil 的書，但 100/80/60/40/20/0 這幾組具體分數級距，是從 IBD 旗下 MarketSmith 這套商業工具的評分慣例移植過來的，不是書裡逐字給出的數字。

## 機制

`canslim-screener` 預設跑標普 500 市值前 40 大成分股（`screen_canslim.py`，可用 `--universe` 指定自訂清單），單檔股票要打 7 次 FMP API（公司概況、報價、兩次財報、90 天與 365 天歷史股價、機構持股），40 檔合計 280 次，再加上大盤資料（`^GSPC` 報價、`^VIX` 報價、`^GSPC` 52 週歷史）3 次，總共約 283 次——超過免費額度每日 250 次的上限；免費額度跑不完整 40 檔——要嘛用 `--max-candidates 35` 縮到 35 檔（35×7+3=248 次，壓在額度內），要嘛升級到 FMP Starter 方案（每月 29.99 美元、每日 750 次）才能跑滿 40 檔。機構持股（I 分量）如果 FMP 拿不到 `sharesOutstanding`，會自動切到 Finviz 網頁爬蟲補資料，把 I 分量的準確度從「只有持有人數、35/100」補到「有完整持股比例、60–100/100」；40 檔全跑約需 2 分鐘，Finviz fallback 每檔再加約 2 秒的速率限制。

執行順序上，M 分量最先算——如果偵測到熊市（M=0），腳本會先跳出警告，提醒使用者考慮加碼現金；接著才逐檔算 C、A、N、S、L、I 六個分量，L 分量需要額外抓 365 天的歷史股價做相對強度計算，是七個分量裡唯一需要長區間歷史資料的一項。每一分量算完，套進 Phase 3 加權公式（C×15% + A×20% + N×15% + S×15% + L×20% + I×10% + M×5%）合成一個 composite score，依分數排序、找出每檔股票最弱的分量（`weakest_component`），寫進 `canslim_candidates` 的 JSON 與 Markdown 兩份報告。`interpretation_guide.md` 另外列了一張及格門檻表——C≥60、A≥50、N≥40（距 52 週高點 25% 內）、S≥40（吸籌型態）、L≥50（RS 評等 60 以上）、I≥40、M≥40——七項全部達標才算合格候選；composite score 換算成七級評等：90 分以上 Exceptional+，80–89 Exceptional，70–79 Strong，60–69 Above Average，50–59 Average，40–49 Below Average，40 分以下 Weak。

## 判讀與誤用

`interpretation_guide.md` 把分數帶換算成明確的持倉建議：90 分以上進取到投資組合的 15–20%，80–89 分 10–15%，70–79 分 8–12%，60–69 分 5–8%，50–59 分只列觀察名單（信心夠高頂多 3–5%），40 分以下 0%。但這張表壓著一條前提：M 分量的否決權。文件自己舉的例子講得很白——一檔股票 C=100、A=95、N=98，composite 算出來 85.3 分（「Exceptional by fundamentals」），但 M=0（熊市）：買進之後大盤持續探底，股價還是跟著跌 20–30%，7–8% 的停損照樣被觸發。結論只有一句：composite 分數再高，M=0 的時候不准買，等 M 分量回到 40 分以上再進場。

90 分以上的 Exceptional+ 級距，`interpretation_guide.md` 定義得很嚴——七個分量同時站上 80 分以上（C、A、N、S、L、I、M 全部 ≥80），對照 `scoring_system.md` 給的百分位是「Top 1–2%」，這正是七項全滿型股票稀有的來源：composite score 是加權平均，任何一個分量特別弱，都可能被其他分量的高分拉平，掩蓋掉真正的風險——這也是文件反覆強調要看「最弱分量」（weakest component）而不是只看合成分數的原因：最弱分量是 C，代表下一季財報有失速風險，建議把停損收緊到 5–6%（而不是標準的 7–8%）；最弱分量是 N，代表股價離高點太遠、缺乏動能，該做的是等突破確認，不是撿便宜。`interpretation_guide.md` 列的常見誤讀也點出同一件事：把 60 分以下的股票當「便宜貨」搶進、只看合成分數不看最弱分量、無視 M 分量獨自判斷——這幾種誤用的共同點，都是把一個加權平均數當成保證，而不是七個獨立檢查裡最弱的那一關。

另一個評等表沒寫出來、但機制上看得出來的限制，是基本面資料的滯後性。C、A 兩個分量吃的是 FMP 的季度與年度財報（單檔 7 次 API 呼叫裡有兩次專門抓 income statement），只在公司公告當下更新；N、S 兩個分量吃的是每日股價與成交量，M 分量吃的是每日大盤與 VIX，三項都能隨盤中變化即時反映。composite score 裡有 35% 的權重（C 15%+A 20%）建立在更新頻率慢得多的數字上——這正是為什麼這份候選名單跟其他偵查隊一樣，只是候選生成，不是訊號：第 7 步的週線人工複核看到的 composite score，基本面那一截隨時可能還停在上一次財報公告的狀態。

## 延伸閱讀

- [`skills/canslim-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/canslim-screener/SKILL.md)
- [`skills/canslim-screener/references/canslim_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/canslim-screener/references/canslim_methodology.md)
- [`skills/canslim-screener/references/scoring_system.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/canslim-screener/references/scoring_system.md)
- [`skills/canslim-screener/references/interpretation_guide.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/canslim-screener/references/interpretation_guide.md)
