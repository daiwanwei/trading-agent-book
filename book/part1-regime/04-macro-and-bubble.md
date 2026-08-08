# 1.4 更長的視野：宏觀 regime 與泡沫

## 場景

週日晚上，下週還沒開盤。過去六天，`market-regime-daily` 每天早上把四步跑完，`exposure_decision` 一天一個 `allow` / `restrict` / `cash-priority`，管的都是「今天」。但這個 workflow 從來沒問過一個更慢的問題：現在市場所在的這個結構性環境，還會持續多久；而如果它已經漲到一個危險的心理階段，該怎麼提早準備。

Agent 這時候另外跑兩個 skill，兩者都不在四個每日步驟裡。`macro-regime-detector` 出現在 `market-regime-daily.yaml` 的 `optional_skills` 清單裡，但翻遍 `steps:` 底下的四個步驟——`market-breadth-analyzer`、`uptrend-analyzer`、`market-top-detector`、`exposure-coach`——沒有一步的 `skill:` 欄位填的是它。它被登記在這條 workflow 的周邊，卻沒有被排進任何一次執行；`skills-index.yaml` 裡它的 `workflows` 欄位寫著 `market-regime-daily`，對應的正是這種「掛在旁邊、不進四步」的關係，而不是被排進某個具體步驟編號。`us-market-bubble-detector` 的處境更乾淨：它的 `workflows` 欄位是空陣列 `[]`，跟任何一條 workflow 都沒有登記關係。

這兩個 skill 回答的問題也跟前三節不同。1.1 到 1.3 問的都是「這幾天到幾週的證據夠不夠」；這一節問的是「接下來一季，預設姿態該偏攻還是偏守」。今晚跑出來的東西，不會改變明天那張單，改的是往後幾個月看盤時，心裡那把尺該怎麼擺。

## 方法論

`macro-regime-detector` 的核心假設是：跨資產比率比絕對價位更早反映資金在往哪裡挪。它盯 6 組比率——市場集中度（RSP/SPY）、殖利率曲線（10Y-2Y 利差）、信用狀況（HYG/LQD）、規模因子（IWM/SPY）、股債關係（SPY/TLT 及其相關係數）、類股輪動（XLY/XLP）——`indicator_interpretation_guide.md` 給了兩個具體的「領先」實證：HYG/LQD 惡化領先 2020 年崩盤約 2 週、領先 2008 年危機約 3 個月；IWM/SPY 的小型股轉強，通常在經濟復甦成為市場共識之前 3 到 6 個月就已經開始。這就是「為什麼看比率不看絕對點位」的理由——信用市場與規模因子動得比股價指數本身早。

`us-market-bubble-detector` 用的是另一套框架：`bubble_framework.md` 重述的 Minsky/Kindleberger 五階段模型——Displacement（新技術或政策鬆綁帶來合理的價格上漲）、Boom（價漲→媒體曝光→新參與者→流動性擴張的自我強化循環）、Euphoria（敘事變成「常識」，質疑者被貼上過時標籤，槓桿與新股發行氾濫）、Profit Taking（早期資金開始獲利了結，但群眾仍在追高）、Panic（趨勢破位確認，強制平倉引發連鎖反應）。文件把泡沫定義成一種群眾心理階段的轉換，而不是價格本身的高低——反覆用的比喻是「計程車司機也在聊股票」：當資訊擴散到最外層、非投資人都在給建議時，代表最後一批買盤已經進場，需求即將枯竭。`us-market-bubble-detector/SKILL.md` 把量化評分機制標為「Revised v2.1」，但那些版本修訂的細節——放寬或收緊的具體分數——寫在 `SKILL.md` 裡，不在 `bubble_framework.md` 這份理論框架文件裡，兩者的分工是理論歸理論、評分規則歸 `SKILL.md`。

## 機制

`macro-regime-detector` 把 6 組比率的每一組都算出一個 0–100 分的分項分數，但這個分數量的是「轉換訊號的強度」，不是「好或壞」——0–20 分是穩定、沒有轉換訊號，80–100 分是交叉、動能、加速三者同時對齊的強確認訊號。算法分三層：第一層看比率的 6 個月均線與 12 個月均線的交叉（黃金交叉或死亡交叉，0–40 分，越近期權重越高）；第二層比較 3 個月與 12 個月的變化率，抓早期反轉（0–30 分）；第三層檢查交叉、短期動能、均線間距擴大三個訊號是否同時成立（0–30 分）。6 個分項再按固定權重合成——市場集中度 25%、殖利率曲線 20%、信用狀況 15%、規模因子 15%、股債關係 15%、類股輪動 10%——餵進一棵決策樹，把當下狀態分類成 Concentration（集中）、Broadening（擴散）、Contraction（收縮）、Inflationary（通膨型）、Transitional（過渡型）五種 regime 之一，信心度依最高分規則得分分四級：≥4 高、≥3 中、≥2 低、<2 極低。運算全部發生在月頻率——抓 600 天的日線，取每月最後一個交易日降頻成約 24 個月度點，再算 6 月與 12 月均線；`macro-regime-detector/SKILL.md` 自己的比較表把這個 1–2 年結構性視角，跟 1.2 節 `market-top-detector` 的 2–8 週戰術視角、1.1 節 `market-breadth-analyzer` 的當下快照並列，三者刻意站在不同的時間刻度上。跑一次約 10 次 FMP API 呼叫，抓 9 檔 ETF 加公債利率；`SKILL.md` 寫明 FMP API key 是必要條件，缺了會直接報錯，但個別 ETF 若 FMP 歷史價格端點抓不到資料，程式會自動退回 yfinance——這個退路存在，不代表可以跳過 FMP key。這裡有一處上游文件本身尚未同步的落差：附錄 A 沿用 `skills-index.yaml` 的登記，把這個 skill 的資料整合寫成 `yfinance_or_csv`、`recommended`（建議而非必要）；本節內容以直接描述程式行為的 `SKILL.md` 為準。

`us-market-bubble-detector` 完全不碰市場資料 API，它評的是使用者手動蒐集回來的指標。四階段流程：第一階段強制蒐集 Put/Call 比率、VIX、槓桿（融資餘額）、IPO 熱度等原始數據；第二階段照六個指標的固定門檻機械打分，每項 0–2 分、合計最高 12 分——例如 Put/Call < 0.70 記 2 分，VIX < 12 且指數在 52 週高點 5% 以內記 2 分；第三階段是質化調整，v2.1 把上限從 v2.0 的 +5 分收緊到 +3 分，且社會滲透度、媒體/搜尋熱度、估值脫節三項調整都要求可驗證的具體證據（Google Trends 倍數、雜誌封面日期），不能靠「敘事感覺很熱」就加分；第四階段把兩段分數相加得出 0–15 分的總分，對應五個風險階段：Normal（0–4 分，風險預算 100%）、Caution（5–7 分，70–80%）、Elevated Risk（8–9 分，50–70%，v2.1 新增的階段）、Euphoria（10–12 分，40–50%）、Critical（13–15 分，20–30%）。這套流程從頭到尾都是「使用者提供指標」，跟 macro-regime-detector 的自動抓取正好相反。

兩者的共同點，是都被排除在每天必跑的四步之外——一個掛在 `optional_skills` 卻沒有對應步驟，一個連掛都沒掛。它們服務的是每週或每季才需要回答一次的問題，硬塞進每天 15 分鐘的節奏裡，只會稀釋 `exposure-coach` 真正要處理的當日證據。

## 判讀與誤用

`regime_detection_methodology.md` 自己列的第一條限制寫得很直白：這套系統「刻意滯後」——月頻率意味著訊號會比日頻率指標晚幾週到幾個月才浮現，因為目標是結構性確認，不是搶先偵測。第二條限制是假訊號：正在收斂的均線可能產生一個轉換訊號，卻在真正交叉之前就反轉回去，所以永遠要看跨分項確認，而不是單一分項過線就下結論。`historical_regimes.md` 給了兩個具體的假訊號案例：2018 年第一季出現過擴散（Broadening）訊號，但第四季就被貿易戰與 Fed 緊縮政策打回原形；2015 年也出現過多個收縮訊號，但最終沒有真正惡化。這兩個案例合起來給出的操作結論是：訊號要撐住至少 3 個月以上，才值得當成高信心的重新配置依據。

泡沫分數同樣不能直接翻譯成「現在做空」。`bubble_framework.md` 在空單時機一節明講這是最容易出錯的地方——「基於主觀『太貴了』的提早放空」被列為 NG 樣板，理由是泡沫「維持不理性的時間，往往比你維持不破產的時間更長」。`SKILL.md` 把這句話落實成具體門檻：即使總分落在 13–15 分的 Critical 區間，放空也只是「建議」，前提是先確認 7 項複合條件（週線走低、成交量見頂回落、槓桿指標下滑、媒體/搜尋熱度見頂、弱勢股先破位、VIX 急升過 20、政策轉向訊號）裡至少 5 項成立，而且要求小倉位分批建立、靠後續確認再加碼，不是一次到位。

`historical_cases.md` 的 2017 年加密貨幣泡沫案例可以把這個門檻具體化。比特幣從 2017 年 1 月的 1,000 美元，一路推進到 6 月 3,000 美元、8 月 5,000 美元、11 月 10,000 美元；文件估算到 12 月中旬，六項量化指標加三項質化調整已經衝到 15/15 滿分，落在 Critical 區間——這跟 12 月 17 日出現的實際高點 19,783 美元幾乎是同一段時間窗。但滿分本身不是放空指令：`SKILL.md` 的邏輯要求即使在 Critical 區間，也要先看到 5/7 複合條件成立才「建議」放空，而不是分數見頂就進場。文件隨後也給出了另一種可執行的應對——不是猜頂，而是用機械化停利：12 月初以 ATR（20 日均幅）為基礎設定 1.5 倍係數的移動停損，停損價隨高點同步上移，價格真正反轉才出場，最終在比原始高點低約 11% 處出清，比起試圖精準抓頂的「完美情境」（不可能提前執行）更貼近可重複操作的紀律。2018 年 12 月，比特幣跌到 3,200 美元，較高點跌幅約 84%——滿分之後崩盤確實發生了，但發生的時間點，仍然要靠額外的確認條件去抓，不是分數本身告訴你的。

## 延伸閱讀

- [`skills/macro-regime-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/macro-regime-detector/SKILL.md)
- [`skills/macro-regime-detector/references/regime_detection_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/macro-regime-detector/references/regime_detection_methodology.md)
- [`skills/macro-regime-detector/references/indicator_interpretation_guide.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/macro-regime-detector/references/indicator_interpretation_guide.md)
- [`skills/macro-regime-detector/references/historical_regimes.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/macro-regime-detector/references/historical_regimes.md)
- [`skills/us-market-bubble-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/us-market-bubble-detector/SKILL.md)
- [`skills/us-market-bubble-detector/references/bubble_framework.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/us-market-bubble-detector/references/bubble_framework.md)
- [`skills/us-market-bubble-detector/references/historical_cases.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/us-market-bubble-detector/references/historical_cases.md)
