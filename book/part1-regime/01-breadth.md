# 1.1 市場的心跳：廣度與參與度

## 場景

週一 06:31，[`market-regime-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml) 才啟動一分鐘。第一步「Analyze market breadth」把 `market-breadth-analyzer` 叫起來：它不看任何一檔個股的線圖，只讀 TraderMonty 公開在 GitHub Pages 上的兩份 CSV——一份約 2,500 列、回溯到 2016 年的逐日明細，一份 8 項指標的摘要——算出一份 `market_breadth_report`。不用 API key，也不花一毛錢。

一分鐘後，第二步「Analyze uptrend participation」把棒子交給 `uptrend-analyzer`。它讀的是另一份免費 CSV，Monty's Uptrend Ratio Dashboard 的每日輸出，追蹤大約 2,800 檔美股、11 個 GICS 產業，量出到底有多少比例的股票真的站在「上升趨勢」的定義裡，寫成 `uptrend_report`。

兩步都不是決策閘——`market-regime-daily.yaml` 把兩步的 `decision_gate` 都標成 `false`。它們不判斷今天能不能冒新的風險，只負責把兩把角度不同的體溫計讀數攤在桌上，留給第四步的 `exposure-coach` 去綜合判斷。

## 方法論

兩份參考文件對「廣度」的操作定義並不完全相同，值得先分清楚，再往下讀分數。

`breadth_analysis_methodology.md` 開宗明義：健康的漲勢應該是廣泛參與——很多股票一起漲；如果領漲的股票越來越少，往往是修正的前兆。它把這個直覺量化成「多少比例的 S&P 500 成分股站在 200 日均線之上」（用的是 EMA，不是 SMA），再取這條 0–1 比例線的 8 日與 200 日兩條移動平均。這不是教科書式的漲跌家數線，而是這份資料集自己的操作定義；文件本身沒有引用 McClellan 或 Lowry 一類的經典廣度理論家，出處就是 TraderMonty 的 `market-breadth-analysis` 資料集與它公開的原始圖表——包括文件裡提到的「Pink Zone」（200 日均線下彎、且 8 日均線跌破 200 日均線的粉紅背景區），那是這個上游圖表自己的視覺慣例，不是外部研究。文件唯一具體點名的實證，是「指數創新高但廣度卻在惡化」這種背離，曾經在 2000、2007、2021 三次歷史頭部之前出現過。

`uptrend_methodology.md` 的出處標得更具體：資料來自 `tradermonty/uptrend-dashboard` 這個 GitHub repo 與它的 Streamlit 儀表板，「上升趨勢」的定義本身借用 Finviz Elite Screener 的篩選邏輯——股價高於 10 美元、均量高於 10 萬股、市值高於 5,000 萬美元、股價站上 20 日與 200 日均線、50 日均線在 200 日均線之上（黃金交叉）、離 52 週低點已回升超過三成、近 4 週動能為正，八個條件同時成立才算數。同樣沒有引用學術文獻；它的權威性來自這套規則可以逐日重算、逐日驗證。

兩份文件的共同前提是：參與度比指數點位更誠實。指數可以被少數幾檔權值股扛著往上走，廣度告訴你這種漲勢底下到底站著多少人。

## 機制

兩個 skill 都不用 API key，輸入都是公開 CSV，但把「參與度」拆成分數的方式各自不同。

`market-breadth-analyzer` 的主程式 `market_breadth_analyzer.py` 先靠 `csv_client.py` 抓明細與摘要兩份 CSV，交給 `scorer.py` 合成六個分項，每個分項各有一支計分器：`trend_level_calculator`（目前廣度水準與 200MA 趨勢，25%）、`ma_crossover_calculator`（8MA 與 200MA 的交叉動能，20%）、`cycle_calculator`（在峰谷循環中的位置，20%）、`bearish_signal_calculator`（資料集內建的熊訊號旗標，15%）、`historical_context_calculator`（相對十年歷史的百分位，10%）、`divergence_calculator`（S&P 500 與廣度的背離，用 20 日與 60 日兩個窗口合成，10%）。任一分項缺資料，權重按比例分給剩下的分項；`report_generator.py` 把結果寫成 JSON 與 Markdown，`history_tracker.py` 再把每次的 composite score 存進 `market_breadth_history.json`，累積出 improving／deteriorating／stable 的趨勢判讀。它的 composite score 是 0–100 分制：**100 分是「最大健康度、廣泛參與」，0 分是「嚴重疲弱」**。

`uptrend-analyzer` 的主程式 `uptrend_analyzer.py` 靠 `data_fetcher.py` 抓 Uptrend Ratio Dashboard 的 CSV，`scorer.py` 合成五個分項：`market_breadth_calculator`（整體上升趨勢比例，30%）、`sector_participation_calculator`（多少產業真的參與，25%）、`sector_rotation_calculator`（景氣循環股與防禦股的力道對比，15%）、`momentum_calculator`（比例本身的斜率與加速度，20%）、`historical_context_calculator`（相對歷史分布的百分位，10%），`report_generator.py` 輸出報告。它的 composite score 同樣是 0–100 分，但方向是**分數越高、市場越健康**——SKILL.md 甚至直接拿它跟另一個 skill 對比：uptrend-analyzer 是「Higher = healthier」，Market Top Detector 是「Higher = riskier」。同一個 0–100 分制，不同 skill 的漲跌方向可能相反，這是往後每一章第一次提到某個 composite score 時，都要先講清楚範圍與方向的原因。

## 判讀與誤用

先看分數落在哪一區。`market-breadth-analyzer` 把 0–100 分切成五區：80–100 是 `Strong`（建議倉位 90–100%）、60–79 是 `Healthy`（75–90%，正常操作）、40–59 是 `Neutral`（60–75%，選擇性布局、收緊停損）、20–39 是 `Weakening`（40–60%，開始減碼、拉高現金）、0–19 是 `Critical`（25–40%，資本保全）。`uptrend-analyzer` 也是五區但用詞不同：80–100 `Strong Bull`（滿倉 100%）、60–79 `Bull`（80–100%）、40–59 `Neutral`（60–80%）、20–39 `Cautious`（防禦性 30–60%）、0–19 `Bear`（0–30%，資本保全）。兩張表看起來像同一件事的兩種說法，但兩邊的分項組成不一樣，同一天的分數未必同向。

分數本身不是免死金牌。`market-breadth-analyzer` 用「資料品質標籤」提醒使用者：六個分項全在叫 `Complete`，四到五個叫 `Partial`（要謹慎解讀），三個以下叫 `Limited`（信心低）。如果 8MA 剛轉弱導致 C1、C2 出現負向修正，報告會自動掛上 Caution 警語，提醒「正常操作」這類建議可能過度樂觀。`uptrend-analyzer` 則用獨立的 Warning System：Late Cycle（原物料類股同時領先景氣循環股與防禦股）、High Spread（產業間比例差距超過 40 個百分點）、Divergence（同組內部標準差超過 8 個百分點，或走勢方向不一致）三種警訊，各自扣分且可疊加，即使 composite score 本身還落在 `Bull` 區間，警訊亮燈也會把建議倉位往下修。composite score 只是入口，不看警訊與資料品質標籤就下結論，是最常見的誤用。

背離（divergence）在兩個 skill 裡問的是不同層次的問題。`market-breadth-analyzer` 的背離問的是指數 vs 廣度：指數上漲但廣度下跌，是最危險的窄基漲勢，2000、2007、2021 的頭部都出現過這個模式；如果 20 日窗口已經轉弱而 60 日窗口還健康，會觸發 Early Warning，代表結構性背離還沒顯現，但短線已經開始鬆動。`uptrend-analyzer` 的背離問的是同組產業內部：景氣循環股或防禦股這兩組裡，只要有成分產業的走勢跟組內多數方向不一致，就同時扣 Sector Rotation 分項 5 分、composite score 再扣 3 分，兩層疊加起來淨影響約 3.75 分——同一個詞，量的是完全不同的東西。

最後回到 workflow 本身劃的界線。`market-regime-daily.yaml` 的 `when_not_to_run` 講得很白：輸出不能當成獨立的買賣訊號，`exposure_decision` 是姿態，不是指令。這句話字面上指的是第四步的 `exposure_decision`，但 `market_breadth_report` 與 `uptrend_report` 離最終判斷還隔著一步——它們是餵給 `exposure-coach` 的證據，不是判斷本身。兩份報告單獨拿出來讀分數，更不構成任何買賣理由。

## 延伸閱讀

- [`skills/market-breadth-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-breadth-analyzer/SKILL.md)
- [`skills/market-breadth-analyzer/references/breadth_analysis_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-breadth-analyzer/references/breadth_analysis_methodology.md)
- [`skills/uptrend-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/uptrend-analyzer/SKILL.md)
- [`skills/uptrend-analyzer/references/uptrend_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/uptrend-analyzer/references/uptrend_methodology.md)
