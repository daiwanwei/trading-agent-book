# 2.6 事件驅動衛星

## 場景

前五節的偵查隊，不管必跑還是可選，都掛在規律的節奏上——有的每個交易日早上跑一遍，有的固定在每週某一天跑一遍。這一節的四支隊伍不一樣：它們的機會窗跟固定節奏無關，是被事件觸發——有公司公告財報，或者股價走到某種極端行為的時候，才有東西可篩；平常時候，篩子就是空的。

這也是為什麼它們在整個系統裡的掛法，跟 2.1–2.5 節的主力偵查隊不一樣。`theme-detector` 是唯一一個在 `swing-opportunity-daily.yaml` 裡有自己編號步驟的：第 6 步，`optional: true`，`produces: theme_candidates`——README 開場已經點過它的定位：不是獨立主力，是替前面幾支隊伍的候選再多加一層篩子的衛星。`earnings-trade-analyzer` 在 `stockbee-ep-daily.yaml` 裡也有編號位置——第 2 步，同樣 `optional: true`，`produces: earnings_candidates`；但 `pead-screener` 只出現在這份 YAML 開頭的 `optional_skills` 清單裡，沒有自己的編號步驟——它接的是第 4 步 `stockbee-episodic-pivot-analyzer` 產出的 `pead_handoff_candidates`，這條線 `downstream_hints` 標明指向 `swing-opportunity-daily`。2.3 節留了一句伏筆：財報型 EP 若 Day 1 漲幅太強、追價已不划算，`pead_handoff=true` 時就送進 `pead-screener` 做一到五週的紅 K 監控——這裡接手。第四支，`parabolic-short-trade-planner`，在 `skills-index.yaml` 裡 `workflows` 欄位是空的，翻遍現有的 workflow YAML 也找不到它的名字——它不掛在任何一條每日或每週的管線上，只能單獨呼叫。四支隊伍，四種掛法，共通點只有一個：都是被財報或極端價格行為觸發的事件驅動衛星，不是天天巡邏的主力。

## 方法論

`earnings-trade-analyzer` 用一套 5 因子加權計分評估財報後反應：Gap Size（財報跳空幅度，不分方向，權重 25%）、Pre-Earnings Trend（財報前 20 個交易日報酬率，權重 30%——五個因子裡權重最高）、Volume Trend（財報前後 20 日均量對 60 日均量的比值，權重 20%）、MA200 Position（權重 15%）、MA50 Position（權重 10%）。`scoring_methodology.md` 把 Pre-Earnings Trend 排第一順位的理由寫得很直接：財報前的動能是財報後能否延續的最強預測指標，量能確認（20%）驗證的是機構有沒有真的參與這波跳空，兩根均線分量合計 25%，確認股票本身站在有利的趨勢結構裡。五項合成 composite score，換算四級：A（85–100）強力反應、B（70–84）值得觀察、C（55–69）訊號混雜、D（0–54）弱勢設定。

`pead-screener` 篩的是 Post-Earnings Announcement Drift（財報後漂移）——`pead_strategy.md` 把這個異常現象的學理出處列得很清楚：Ball 與 Brown（1968）最早記錄到股價會朝財報意外的方向持續漂移長達 60 天；Bernard 與 Thomas（1989）進一步量化，財報意外幅度最高十分位的股票在公告後 60 天內平均跑贏最低十分位約 4%，漂移在前 2–3 週最強，市值較小、流動性較差的股票漂移更明顯；Foster、Olsen 與 Shevlin（1984）確認漂移幅度跟意外幅度成正比。文件把漂移歸因於市場對新資訊的系統性反應不足——分析師錨定舊估計調整不夠、機構與散戶處理資訊的速度不同步、流動性限制讓大額買盤無法一次到位。`pead-screener` 選擇用週線而非日線篩選，理由是週線能濾掉盤中雜訊、貼近機構分批建倉的節奏；核心型態是紅 K 回檔：財報跳空 3% 以上收出一根綠色週 K，隨後可能再漲一到兩週，接著一根收黑的回檔週 K（紅 K）出現，最後當某一根綠色週 K 收盤價站上紅 K 高點，代表回檔結束、漂移趨勢恢復。

`theme-detector` 用三維計分模型判斷市場主題：Theme Heat（0–100，方向中立的主題強度，由 Momentum 35%、Volume 20%、Uptrend 25%、Breadth 20% 加權合成）、Lifecycle Maturity（Emerging／Accelerating／Trending／Mature／Exhausting 五個階段，由 Duration、Extremity Clustering、Price Extreme Saturation 各 25%，加 Valuation 15%、ETF Proliferation 10% 合成）、Confidence（Low／Medium／High，量化基礎層疊加跨產業廣度修正，script 自身最高只能算到 Medium，Claude 用 WebSearch 做敘事驗證才能拉到 High）。

**進階選讀。** `parabolic-short-trade-planner` 從反面切入同一種事件驅動邏輯——做空耗竭，而不是追多動能。方法論改編自 Qullamaggie 的三種「永恆」放空設定，核心論點是：拋物線走勢終將均值回歸崩落，但在漲勢還在噴出時就放空，是最快虧錢的方式，所以整套框架的目的是延遲進場，直到耗竭訊號真正確認。這是一段進階內容，管線分三階段——Phase 1 `screen_parabolic.py` 每日掃描並用 5 因子計分（MA Extension 30、Acceleration 25、Volume Climax 20、Range Expansion 15、Liquidity 10）分出 A–D 等級，Phase 2 `generate_pre_market_plan.py` 產生盤前計畫，Phase 3 `monitor_intraday_trigger.py` 監控盤中三種觸發型態是否成立——細節留給上游文件，這裡不展開。放空天生是不對稱的風險：多頭部位虧損上限是本金全部歸零，放空部位的理論虧損沒有上限，股價能漲多高沒有天花板，這正是整套方法論寧可延遲進場也不追高的根本原因。

## 機制

`pead-screener` 支援兩種輸入模式。Mode A 直接呼叫 FMP 財報日曆，預設回溯 14 天、監控窗口 5 週；Mode B 吃 `earnings-trade-analyzer` 輸出的 JSON（`schema_version` 須為 "1.0"），用 `--candidates-json` 指定檔案、`--min-grade B` 篩掉 C／D 級。`SKILL.md` 特別標出一個排程陷阱：預市／美股 cron 例行任務該優先用 Mode B——Mode A 拉的是 FMP 全球財報日曆，可能把 API 額度花在非美股標的上，回傳一堆弱勢、不具操作意義的外國掛牌，還沒排到真正要看的美股名單就先燒完額度；如果還是用了 Mode A，且腳本回報額度被砍或出現非美股代碼，要把 PEAD 輸出標成降級、只能人工複核，不當乾淨候選來源使用。

`earnings-trade-analyzer` 跑完寫出 `earnings_trade_analyzer_YYYY-MM-DD_HHMMSS.json` 與對應的 Markdown；`pead-screener` 寫出 `pead_screener_YYYY-MM-DD_HHMMSS.json`／`.md`，每檔候選帶著四階段分類之一：MONITORING（財報後跳空但紅 K 尚未出現）、SIGNAL_READY（紅 K 已形成，等突破）、BREAKOUT（本週綠 K 收盤價站上紅 K 高點，可操作訊號）、EXPIRED（超過 5 週監控窗口，效果已明顯減弱）。

`theme-detector` 的資料流以 FINVIZ 為主幹，分兩種模式：Elite 模式用 CSV 匯出端點，涵蓋每個產業的完整股票清單，請求間隔 0.5 秒，資料即時，約 2–3 分鐘跑完 14 個以上主題，但需要每月 39.50 美元的訂閱；Public 模式改用網頁爬蟲，每個產業只能拿到約前 20 檔（依市值排序的第一頁），請求間隔拉到 2 秒避免觸發封鎖，資料延遲 15 分鐘，約需 5–8 分鐘，不需要任何 API key。FMP 是另一項可選整合，只用來補 P/E 估值資料算 Lifecycle 的 Valuation 分量；沒有 FMP，就退回 FINVIZ 自己的預估本益比當替代。跑完的 Step 4 是唯一非自動化的一步：針對 Theme Heat 排名前 5 的主題，用 WebSearch 搜尋敘事佐證，確認訊號是量化面跟敘事面同時強，才能把 Confidence 從 Medium 拉到 High。

## 判讀與誤用

財報意外本質上難以預測，這條偏差會直接反映在管線的資料品質上。`earnings-trade-analyzer` `SKILL.md` 專門留了一段降級處理：排程跑批時如果端點回傳 404、財報日曆離譜地空、或 API 額度耗盡導致計分沒跑完，不能直接回報「今天沒有財報反應」——要先用更窄的流動性條件重試一次，還是不行，才退到 FMP 穩定端點做未經計分的粗略排序，並且明確標成「初步／未評級」，不能替這些候選標上 A／B／C／D 等級。另一個真實存在的陷阱：篩選器可能印出「Candidates after filtering: 0」並正常結束，卻沒有寫出 JSON 檔案——這種情況下不能拿一個不存在的檔案去跑 PEAD Mode B，要老實說明沒有產生已評分的分析結果。

PEAD 的出場規則寫得很具體：停損設在紅 K 低點下方，是硬停損，不是心理關卡；主要目標是 2R（進場價加上兩倍風險距離）；部位大小依風險控管，單筆不超過帳戶 1–2%，同時不能超過 20 日均額成交量（ADV20）的 1%，避免一天出不掉；同時持有的 PEAD 部位上限 3–5 個，跨產業分散，避免財報季集中在同一批相關股票上。監控窗口預設 5 週，效果在第 1–3 週最強、第 4–5 週明顯衰退；如果股票財報跳空後從未出現像樣的紅 K 回檔——`entry_exit_rules.md` 特別點名這種「gap-and-go」型態不算 PEAD 候選，因為沒有紅 K 就沒有明確的風險定義點。

放空端的風險控管也是據實寫死的：`parabolic-short-trade-planner` 從不下單，Phase 3 判定觸發後仍只是給出具體的進場價、停損與股數，實際扣扳機前，要先確認券商的可借券位置、SEC Rule 201 的 SSR 狀態、以及交易所現行的日內保證金規則——FINRA 已從 2026 年 6 月 4 日起用日內保證金標準取代舊有的當沖次數與最低權益要求，但券商端的過渡期允許延到 2027 年 10 月 20 日，跟 2.1 節下單規劃提到的過渡期是同一件事。

`theme-detector` 沒有 FINVIZ Elite 也能跑，但 Public 模式每個產業只看得到前 20 檔，可能漏掉小型股的參與訊號，執行時間也拉長到 5–8 分鐘——FINVIZ Elite 是建議而非必要，這點跟前五節倚賴 FMP 免費額度的篩選器不一樣。另一個容易誤讀的地方是方向標籤：一個主題被判定 LAG（落後），代表它相對其他主題表現較弱，不代表絕對報酬是負的，更不是放空建議——`theme_detection_methodology.md` 把這點寫得很白：LAG 主題適合減碼，不是拿來當放空訊號用。

## 延伸閱讀

- [`skills/earnings-trade-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/earnings-trade-analyzer/SKILL.md)
- [`skills/earnings-trade-analyzer/references/scoring_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/earnings-trade-analyzer/references/scoring_methodology.md)
- [`skills/pead-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/pead-screener/SKILL.md)
- [`skills/pead-screener/references/pead_strategy.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/pead-screener/references/pead_strategy.md)
- [`skills/pead-screener/references/entry_exit_rules.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/pead-screener/references/entry_exit_rules.md)
- [`skills/theme-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/theme-detector/SKILL.md)
- [`skills/theme-detector/references/theme_detection_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/theme-detector/references/theme_detection_methodology.md)
- [`skills/parabolic-short-trade-planner/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/parabolic-short-trade-planner/SKILL.md)
- [`skills/parabolic-short-trade-planner/references/parabolic_short_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/parabolic-short-trade-planner/references/parabolic_short_methodology.md)
