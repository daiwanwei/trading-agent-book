# 2.3 Stockbee：動能三部曲

## 場景

07:35 兩道閘怎麼亮燈，前兩節已經交代過。`swing-opportunity-daily` 第 2 步 `vcp-screener` 收工之後，第 3、4 步同時攤開——五支偵查隊裡的第二支與第三支：`stockbee-momentum-burst-screener` 抓動能剛爆發的股票，`stockbee-exhaustion-hammer-screener` 反過來在賣壓耗盡的回檔裡找反手買點。兩步都標成 `optional: true`、`decision_gate: false`，`produces` 分別是 `momentum_burst_candidates`、`exhaustion_hammer_candidates`——跳過任一個，流程照樣往下走到第 7 步的週線驗證。

這兩支隊伍出自同一套語彙：Pradeep Bonde 的 Stockbee 風格短線交易。第三支親戚不住在同一個屋簷下——`stockbee-episodic-pivot-analyzer`（EP）不在 `swing-opportunity-daily` 的五步隊列裡，它有自己的 workflow，[`stockbee-ep-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/stockbee-ep-daily.yaml)：`cadence: daily`，但 `when_to_run` 寫得更窄——決算或新聞密集的日子，或有能改變市場認知的重大催化劑出現時才跑，不是每天例行掃描全市場。三支隊伍看的是同一種現象的三個切面：動能剛炸開的股票（momentum burst）、炸開背後有沒有站得住腳的催化劑（EP）、動能炸過頭之後賣壓耗盡了沒有（exhaustion hammer）。

## 方法論

三份 methodology 文件都把方法歸給同一個人。三份 SKILL.md 的 description 都用「Stockbee-style」稱呼這套語彙；momentum burst 與 exhaustion hammer 的 description 更進一步點名 `Pradeep Bonde`，EP 的 description 沒有點名，這個名字要到本文「When to Use」清單才出現。**原著 vs 實作。**跟 2.1、2.2 不一樣的地方要先說清楚：VCP 的 `minervini_entry_rules.md` 列了 Minervini 兩本書當 Sources，CANSLIM 的 SKILL.md 明講計分系統「Adapted from IBD MarketSmith proprietary system」；這三支 Stockbee skill 的九份參考文件裡，沒有一份給出書名、文章或訪談出處，方法只以「Stockbee-style」「Pradeep Bonde」帶過，沒有更進一步的引用鏈——這裡沒有一本可具名的原著能拿來對照實作，唯一能驗證的落差，是方法論散文跟計分系統之間的落差，見下段 exhaustion hammer 的討論。

`momentum_burst_methodology.md` 把核心假設寫成一句話：某些股票在一段區間收縮之後會炸出短而急的動能，真正有用的漲幅常發生在接下來幾個交易日，而非一段長期趨勢。它定義三種觸發家族：4% 突破——收盤價至少比前一日收盤高 4%，當日量高於前一日、且高於流動性下限；金額突破——收盤價減開盤價至少達到設定門檻，預設 $0.90，適合股價較高、百分比漲幅不到 4% 但金額本身有意義的股票；區間擴張——當日振幅大於前三個交易日的每一天，前一日振幅還沒被拉開，且量能確認這次擴張。

`stockbee-exhaustion-hammer-screener` 反過來看同一種現象：鎖定「流動性好、有前期動能或機構持股背景的股票，近期高點後歷經數日或數週賣壓，最後一段破底震出弱手，收盤前買盤進場，留下長下影線、收在當日區間上緣」——`exhaustion_hammer_methodology.md` 用這五步敘述型態，但沒有給出下影線、實體大小或收盤位置的具體百分比門檻；這些幾何細節目前只出現在腳本與 `scoring_system.md` 的計分項目名稱裡，不在這份方法論的散文段落中——跟 VCP 把 dry-up ratio 分成 0.30、0.50、0.70 三個門檻直接寫進 `vcp_methodology.md` 不一樣，這是一個真實存在的文件落差。文件特別提醒不篩選每一根 hammer：結構性偏弱的股票裡出現的 hammer，多半只是下跌中繼的停頓，這裡鎖定的是強勢股在賣壓耗盡後才會出現的買盤。操作時機定得很窄——正常交易時段收盤前約兩分鐘的近收盤掃描，最後一根 K 棒可以是即時資料商的臨時日 K、FMP 報價衍生的估算 K 棒，或收盤後用於覆盤與建模型書的正式日 K。

`stockbee-episodic-pivot-analyzer` 分析的是 Day 1 Episodic Pivot：由明確催化劑觸發的價量重估事件。`ep_methodology.md` 列出十種 EP 類型——`EARNINGS_EP`（財報加速最強，尤其是首次明顯加速或優於預期又上修財測）、`GUIDANCE_EP`、`FDA_EP`（FDA 核准或三期成功，跳空風險高）、`M_AND_A_EP`（併購，上檔常被交易價格封頂）、`CONTRACT_EP`、`PARTNERSHIP_EP`、`ANALYST_EP`（通常較弱，除非印證更大主題）、`PRODUCT_EP`、`STORY_EP`（AI、加密貨幣、核能、太空、機器人、電動車、國防等題材，基本面確認度常較低）、`SQUEEZE_EP`（軋空，視為高風險）。Day 1 品質檢查表給出具體數字：同日漲幅或跳空至少 4%；成交量放大理想值是均量 3 倍以上或絕對成交量 900 萬股以上；收盤落在當日區間上緣；到 EP 當日低點的風險小到能負責任地設定部位；股價原本被冷落、正在打底、或還沒過度延伸；流動性足夠支撐實際的進出。`catalyst_quality.md` 從事件類型、文字線索、上游可選評級三者，組出一個 35 分的催化劑品質分量：財測上修、FDA 核准、首次明顯的獲利加速、重大合約或監管核准屬於高品質；併購、產品發表、策略夥伴、軋空屬於中等或視情境而定；分析師調升、純故事/題材、含糊新聞屬於較弱一級；文字裡出現稀釋、增發、調查、訴訟、辭職、調降等字眼，即使股價當下反應正面，也要打折看待。

## 機制

三個 screener 的輸入模式都留了 FMP 即時掃描與離線 JSON 兩條路。momentum burst 的 Mode A 用 `--fmp-universe --max-symbols 300` 掃美股，Mode B 給明確代號清單，Mode C 吃離線 `--prices-json`。掃完之後把設定品質拆成七個加權分量合成 0–100 分：觸發強度 20、成交量擴張 15、設定品質 25（前段整理長度與寬度、前一日窄幅或收黑、量能乾涸）、收盤位置 10、風險距離 15、失敗過濾 10（近期 4% 破底、觸發前已連三日走高、結構鬆散）、市場閘門 5。分數換算五級：90–100 分 A、80–89 分 A-，兩者通過圖表複核後標 `ACTIONABLE_DAY1`；70–79 分 B 標 `MANUAL_REVIEW`；55–69 分標 `WATCH_ONLY`；55 分以下 `REJECTED`。進場基準是最新收盤價——這是一支盤後/近收盤的篩選器，不是即時工具；停損基準是觸發日低點；`risk_pct_to_stop = (entry − stop) / entry × 100`；交給 `position-sizer` 的公式是 `position_size = account_risk_dollars / (entry_reference − stop_reference)`，篩選器本身不決定最終股數。出場模板：觸發日低點失守就出場，3–5 個交易日後覆盤，單一交易日漲幅達 10% 以上要主動保護獲利，完全反轉或撐過數個交易日仍無跟隨買盤視為失敗的爆發。下游建議流程：`stockbee-momentum-burst-screener → technical-analyst → position-sizer → breakout-trade-planner（可選）→ trader-memory-core`。

exhaustion hammer 的三種輸入模式相同，額外多一個 `--use-quote-latest` 選項——用一次額外的報價呼叫換取近收盤估算 K 棒，準確度取決於資料商的即時性。計分同樣是 0–100，六個分量：品質/流動性 20（股價、20 日均額美元成交量、市值、可選的基金與機構持股資料）、前期動能 15（近期高點、20/60 日強度、相對 50 日均線的位置）、回檔耗竭 20（回檔深度、短期破底反轉、近期賣壓、量能確認）、鎚形幾何 25（長下影線、小實體、強勢收盤位置、從當日低點回升、有限的上影線）、風險距離 15、市場閘門 5。分數帶：90–100 分 A、82–89 分 A-，皆需圖表/新聞/風險複核後標 `ACTIONABLE_CLOSE_BUY`；70–81 分 B 標 `MANUAL_REVIEW` 或隔日鎚形高點確認；55–69 分 `WATCH_TOMORROW`；55 分以下 `REJECTED`。兩支日常隊伍都用 `--market-gate allowed/neutral/restrictive` 控制市場分量，`restrictive` 時市場分量直接歸零。

EP 吃三種輸入：Mode A 純催化劑/事件 JSON；Mode B 直接吃 `earnings-trade-analyzer` 的輸出；Mode C 用催化劑 JSON 疊加 `stockbee-momentum-burst-screener` 的 JSON，重複利用裡面的當日漲幅、成交量、收盤位置、風險距離欄位。35 分的催化劑品質分量疊上價量確認，輸出五種狀態：`ACTIONABLE_DAY1`（催化劑強、價量確認、風險可控）、`DAY1_WATCH`（催化劑不錯但需要圖表/脈絡再確認）、`DELAYED_EP_WATCH`（事件夠強但 Day 1 風險或收盤品質不合格，等新底部或回檔）、`CATALYST_WATCH`（催化劑可能重要但價量還沒確認）、`REJECT`。`handoff_rules.md` 把交接寫成具體規則：`ACTIONABLE_DAY1` 與高品質 `DAY1_WATCH` 送進 `technical-analyst`，圖表複核要淘汰長上影線/當日回吐、明顯套牢賣壓、混亂的低流動性走勢、催化劑之前已經走了一大段、或停損距離超出風險模型的候選；給 `position-sizer` 的公式是 `risk_per_share = entry_reference − ep_day_low`，若 EP 當日低點離得太遠，不強做，留在 `DELAYED_EP_WATCH` 等回檔。也可以反過來送回 `stockbee-momentum-burst-screener`，確認同一檔股票是否同時出現 4% 突破、金額突破、區間擴張、成交量擴張、收在最高點附近——兼具催化劑品質與動能爆發確認的候選通常最強。財報/財測型 EP 若 Day 1 漲幅太強、追價已不划算，可在 `pead_handoff=true` 時送進 `pead-screener`，做一到五週的紅 K/延遲反應監控——這條交接留給後面事件驅動的篇幅（2.6）再展開。

## 判讀與誤用

`swing-opportunity-daily.yaml` 的 `manual_review` 對兩支日常偵查隊各留了一條規則，序章已引過兩者共通的核心——輸出只當候選生成，這裡把各自不同的那一半攤開：momentum burst 要求圖表驗證與風險距離複核；exhaustion hammer 除了圖表驗證，還額外要求確認回檔不是被摧毀論點的新聞事件引發、並驗證到當日低點的風險。兩份 methodology 也各自列了「這支腳本不做什麼」：momentum burst 不下單、不保證後續跟進、不取代人工看圖、不驗證新聞或催化劑、不模擬盤中滑價或 level-2 流動性、不決定最終部位；exhaustion hammer 不下單、不建議自動執行、不驗證報價的即時新鮮度、不自己發掘催化劑或新聞、不取代圖表覆核或風險計算。兩支隊伍的共通點是：它們都只在乎價與量，新聞是誰的事完全沒交代。

這正是 EP 存在的理由，但 EP 自己也把邊界劃得很清楚。SKILL.md 明講：這支 skill 不會自己找新聞——如果沒有人提供催化劑，要先用使用者慣用的新聞或研究流程蒐集事件脈絡；`skills-index.yaml` 對 `catalyst_events_json` 的註記重複同一件事：這是使用者提供或上游生成的催化劑紀錄，這支 skill 本身不發掘新聞。`ep_methodology.md` 補了更直接的一句：這支 skill 不決定買不買，只排序和分類候選；買進前要先過人工催化劑覆核、圖表驗證、風險部位計算三關。`catalyst_quality.md` 留了五個人工覆核問題：這是單日頭條還是站得住腳的重估？相對市場原本的預期，這件事意不意外？它有沒有改變營收、獲利、潛在市場、存續機率或機構認可度？事件發生前股價是不是已經走了一大段？EP 當日低點能不能當一個現實的停損？

三支 skill 在 `skills-index.yaml` 裡都標成 `status: beta`，複核時值得多留一分餘地。`entry_exit_rules.md` 的實務提醒也適用在三支隊伍上：分數再高都不是獨立成立的買進理由，被拒的候選要留著，失敗案例是校正判讀直覺的材料。`handoff_rules.md` 對 `trader-memory-core` 的交代劃出同一條線：只登記通過人工複核、或刻意留在延遲觀察名單上的候選，不要把每一則低品質頭條都塞進論點庫——想做廣泛學習，另開一份模型書或研究紀錄。

## 延伸閱讀

- [`skills/stockbee-momentum-burst-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-momentum-burst-screener/SKILL.md)
- [`skills/stockbee-momentum-burst-screener/references/momentum_burst_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-momentum-burst-screener/references/momentum_burst_methodology.md)
- [`skills/stockbee-momentum-burst-screener/references/entry_exit_rules.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-momentum-burst-screener/references/entry_exit_rules.md)
- [`skills/stockbee-episodic-pivot-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-episodic-pivot-analyzer/SKILL.md)
- [`skills/stockbee-episodic-pivot-analyzer/references/ep_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-episodic-pivot-analyzer/references/ep_methodology.md)
- [`skills/stockbee-episodic-pivot-analyzer/references/catalyst_quality.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-episodic-pivot-analyzer/references/catalyst_quality.md)
- [`skills/stockbee-episodic-pivot-analyzer/references/handoff_rules.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-episodic-pivot-analyzer/references/handoff_rules.md)
- [`skills/stockbee-exhaustion-hammer-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-exhaustion-hammer-screener/SKILL.md)
- [`skills/stockbee-exhaustion-hammer-screener/references/exhaustion_hammer_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-exhaustion-hammer-screener/references/exhaustion_hammer_methodology.md)
