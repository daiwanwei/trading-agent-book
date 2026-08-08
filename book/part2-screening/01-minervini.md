# 2.1 Minervini：波動收縮與突破

## 場景

07:35，開場那兩道閘都亮了燈（1.5 節；帳戶端的斷路器，第三部會細講），市場准了、帳戶也准了。`swing-opportunity-daily.yaml` 接手之後，第 2 步立刻被叫起來——五個偵查步驟裡，這是唯一標成必跑、不是 `optional: true` 的一個。`skill: vcp-screener`，`decision_gate: false`，`produces: vcp_candidates`。它不問「今天能不能冒風險」，那個問題第 1 步的斷路器已經問過；它問的是更窄、更具體的一件事：這一批 S&P 500 成分股裡，誰正壓縮到臨界點，隨時可能突破。

預設跑法很直接：`screen_vcp.py` 先抓齊整個 S&P 500 成分股，靠報價資料粗篩、依 Stage 2 可能性排序後截斷到前 100 名候選，才動用 FMP 的日線 OHLCV 完成整套判斷；免費額度（250 次呼叫/日）就夠用，想篩滿整個 S&P 500（`--full-sp500`）才需要付費層級。跑完之後，`reports/` 下多出一份 JSON 跟一份 Markdown，`vcp_candidates` 就是這份 JSON。第 3 到 6 步的其他篩子——Stockbee 動能爆發、Stockbee 衰竭反手、CANSLIM、主題偵測——各自平行跑，誰跳過都不影響這一步；但第 7 步週線驗證要看的候選清單裡，`vcp_candidates` 是唯一保證存在的一份。

這支唯一必跑的偵查隊，用的是哪一套辨識邏輯？答案是 Mark Minervini 的波動收縮型態（Volatility Contraction Pattern，VCP）。

## 方法論

VCP 由兩屆美國投資錦標賽冠軍 Mark Minervini 提出，出發點是 Stan Weinstein 的階段分析（Stage Analysis）：股票的生命週期分四個階段——第一階段築底（Accumulation/Basing）、第二階段上升（Advancing/Uptrend）、第三階段出貨（Distribution/Topping）、第四階段下跌（Declining/Downtrend）。`vcp_methodology.md` 講得很直接：只有第二階段值得買。判斷是不是第二階段，靠一張七點式 Trend Template：股價同時站上 150 日與 200 日均線；150 日均線高於 200 日均線；200 日均線至少連續 22 個交易日向上；股價站上 50 日均線；股價離 52 週低點至少拉開 25%；股價落在 52 週高點的 25% 範圍內；相對強度（RS）評等高於 70。七項裡通過六項（原始分數 ≥85）才算確認第二階段，可以往下看 VCP。

VCP 本身，是第二階段股票回檔又反彈，但每一次回檔的深度都比前一次淺——這個「波動收縮」訊號代表賣壓正被吸收、剩下的賣家逐漸耗盡、籌碼供給乾涸，突破的機率因此升高。文件對收縮結構定出具體規則：第一段回檔（T1）深度落在 8–35%（S&P 500 大型股；小型股可以到 50%）；第二段（T2）至少比 T1 再收緊 25%（比值 ≤0.75）；第三段（T3）同樣要比 T2 再收緊 25%；極罕見的第四段（T4）深度常常小於 5%。最少要有 2 段收縮，理想是 3 到 4 段、逐段收緊；整個型態長度落在 15–325 個交易日。收縮末端的高點是 pivot（樞紐點）——買點就在這裡：價格站上 pivot、成交量放大到 50 日均量的 1.5 倍以上，才算有效突破；停損設在最後一段回檔低點下方 1–2%，單筆風險落在進場到停損的 5–8% 之間。成交量的理想走勢是回檔階段量縮、接近 pivot 時「乾到極致」、突破當天放量到 50 日均量的 1.5–2 倍——文件把這個乾涸程度量化成 dry-up ratio（樞紐點前 10 根 K 棒均量 ÷ 50 日均量）：低於 0.30 是教科書等級，0.30–0.50 強，0.50–0.70 尚可，超過 0.70 就要謹慎。

**原著 vs 實作。** 把 `vcp_methodology.md` 的敘述跟 `scoring_system.md` 的計分規則並排讀，能看出 repo 把原著幾個方向性的判斷，量化成了具體數字表。Trend Template 在原著裡是一張七點清單，及格線是「通過六項」；`scoring_system.md` 把它拆成七等份、每項 14.3 分，再依通過項數換算成連續分數（7/7=100、6/7=85.8、5/7=71.5、4 項以下 ≤57），佔五分量 composite score 25% 的權重——原著問的是「過不過關」，實作問的是「差多少分」。收縮段數是同一種轉譯：原著只講「最少 2 段、理想 3–4 段、逐段收緊」這種方向性要求；`scoring_system.md` 卻定出一張固定對照表（4 段收縮基礎分 90、3 段 80、2 段 60、1 段或無效 0–40），再疊加修正項（最後一段收縮深度低於 5% 加 10 分、平均收縮比小於 T1 的 0.4 倍加 10 分、T1 深度超過 30% 減 10 分）。第三個差距更結構性：原著沒有「執行狀態」這個概念，VCP 分數高、結構乾淨就是好設定；repo 卻另外疊了一層 Execution State 引擎，把「型態多好」（`composite_score`）跟「現在能不能買」拆成兩條軸線，再用 State Cap 把過度延伸（Overextended，股價超過 pivot 10% 以上或超過 200 日均線 50%）、結構破壞（Damaged，跌破最後一段低點或跌破 50 日均線）這類狀態，強制把評等封頂在 Weak VCP 甚至 No VCP，不讓一個原本 90 分的型態，在股價已經追高之後還顯示「Textbook VCP」——這道封頂機制是 `scoring_system.md` 自己加上去的，`vcp_methodology.md` 沒有討論過。

## 機制

`vcp-screener` 的篩選分三個階段。Phase 1 Pre-Filter 只靠報價資料粗篩：股價高於 10 美元、離 52 週低點超過 20%、離 52 週高點在 30% 以內、均量高於 20 萬股，約 101 次 API 呼叫。Phase 2 Trend Template 對通過粗篩的標的抓 260 天歷史，套上面七點式檢查，約再 100 次呼叫。Phase 3 VCP Detection 不再呼叫 API，純粹在本地做型態分析、計分、產報告。三階段疊起來，composite score 由五個分量加權組成：Trend Template 25%、收縮品質 25%、成交量型態 20%、Pivot 接近度 15%、相對強度 15%。方法論裡那個單一的 dry-up ratio，機制把它拆得更細：成交量型態把 dry-up ratio 拆成三個區間分開計分——Zone A 是最後一段收縮期、Zone B 是 pivot 前 10 根扣除最後一根、Zone C 是最後一根——避免突破當天的爆量污染 dry-up 的計算，另外再算一個獨立的 Breakout Volume Score（放大 3 倍以上滿分 100、2–2.9 倍 80 分、1.5–1.9 倍 60 分）。Pivot 接近度用「距離優先」的原則評分：pivot 上方 0–3% 且有量能確認是滿分，超過 pivot 5% 以上不管量能多大都不再加分——這正是 Minervini「不追高於 pivot 5% 以上」的規則，量能是加分項，不是否決權。相對強度用 Minervini 加權法，近 3 個月佔 40%、6/9/12 個月各佔 20%，強調近期表現。

Composite score 換算成六級 Rating：90 分以上 Textbook VCP（1.5–2 倍常規部位）、80–89 分 Strong VCP（1 倍）、70–79 分 Good VCP（0.75 倍，需量能確認）、60–69 分 Developing VCP（只能觀察）、50–59 分 Weak VCP（僅監控）、50 分以下 No VCP（不具操作意義）。但這個分數會先被 Execution State 的 State Cap 卡過一輪——只有 Pre-breakout 與 Breakout 兩種狀態不設封頂。`entry_ready=True` 還要同時滿足：execution_state 不落在 Invalid、Damaged、Overextended、Extended、Early-post-breakout 之中；`valid_vcp=True`；距 pivot -8% 到 +3%；`dry_up_ratio ≤1.0`；`trade_status` 不是「BELOW STOP LEVEL」；風險百分比大於 0% 且不超過 15%。這批 entry_ready 的候選，連同尚未達標的候選，一起寫進 `vcp_candidates`。

第 9 步的 `breakout-trade-planner`（optional）接手，把候選變成可執行的下單計畫。這裡有個容易混淆的地方，第三部實作章已經核對過：`swing-opportunity-daily.yaml` 把這一步的 `consumes` 列成 `validated_setups` 與 `position_sizing`，但 `plan_breakout_trades.py` 的 `--input` 實際吃的是第 2 步 `vcp-screener` 輸出的 JSON——這支 script 自帶一套 Minervini Gate 與部位計算，不重讀 `position-sizer` 的輸出。Gate 要求 `valid_vcp=True`、`rating_band` 落在 good/strong/textbook、worst-case 風險（`risk_pct_worst`）不超過 8%；若已經處在 Breakout 狀態，還要多驗證量能確認、距 pivot 不超過 `max_chase_pct`（預設 2%）、目前價格不超過 worst_entry。進場價分兩層算：`signal_entry = pivot * (1 + pivot_buffer_pct / 100)` 是觸發買進的訊號價，`worst_entry = pivot * (1 + max_chase_pct / 100)` 是可接受的最差成交價；停損 `stop_loss = last_contraction_low * (1 - stop_buffer_pct / 100)`。Gate 判定與部位計算一律用 worst_entry，不用訊號價。風險規則跟 `vcp_methodology.md` 一致：單筆最高風險 8%，預設帳戶風險 0.5%，總部位熱度上限 6%，絕不追高於 pivot 2% 以上。部位倍數表這裡不再是原著的區間，而是收斂成單一數字：Textbook（90 分以上）固定 1.75 倍、Strong 1.0 倍、Good 0.75 倍、Developing 0 倍（只看不買）——1.75 倍正好落在 `vcp_methodology.md` 給出的 1.5–2 倍區間中點，是 repo 從那個區間裡選定的一個固定值。輸出兩種下單模式：pre_place 在開盤前就掛好 stop-limit 括號單，價格觸及 pivot 自動觸發；post_confirm 則等 5 分鐘 K 棒收盤確認（收盤價高於 pivot、收在該根 K 棒上緣 60% 以上、當下相對量能 ≥1.5 倍、追價不超過 2%）後才用限價單進場。`breakout-trade-planner` 的 `SKILL.md` 把這兩種輸出正式定名為『Alpaca-compatible order templates』：pre_place 對應 stop-limit bracket order，post_confirm 對應 limit bracket order，格式對齊 Alpaca 下單 API 的參數。`minervini_entry_rules.md` 的 Sources 只列了 Minervini 兩本書——《Trade Like a Stock Market Wizard》（2013）、《Think & Trade Like a Champion》（2017）——加上 TrendSpider 的 VCP 偵測器與 ChartMill 的策略文件；換句話說，這套進出場公式裡的具體百分比，有一部分來自公開掃描工具的實作，不是全部出自 Minervini 本人的著作。

## 判讀與誤用

`swing-opportunity-daily.yaml` 的 `manual_review` 把話講死：篩選器的輸出是候選生成，不是訊號；就算篩選器過了，只要週線結構不明確，第 7 步的人工複核照樣要淘汰。這句話對 `vcp-screener` 格外貼切，因為它自己也在做同一件事：`composite_score` 衡量的是型態「長得多標準」，不是「一定會突破」。90 分的 Textbook VCP，只代表七點式 Trend Template 幾乎全過、收縮段數理想、量能乾涸得漂亮——這是統計上更可能成立的設定，不是保證。`vcp_methodology.md` 自己列出的常見誤區也提醒這一點：在 pivot 之前搶進、忽略量能、停損設太寬、在錯誤的階段交易、T1 深度超過 35%、後一段收縮反而比前一段更深（這種情況根本不是 VCP）——都會讓分數再高的型態失敗。

State Cap 的存在，正是要防止「分數高」被誤讀成「現在能買」——Overextended、Damaged 這幾種狀態，不管 composite_score 算出來是多少，評等都會被強制打到 Weak VCP 甚至 No VCP。同樣的邏輯延伸到下單端：`breakout-trade-planner` 的 `SKILL.md` 明講，這些下單範本是規劃產物，不是券商許可——如果計畫可能造成當日對敲或動用融資，要先確認交易者自己的日內交易限制。2026 年 6 月 4 日起，FINRA 已經用日內保證金標準取代舊的當沖次數與 2.5 萬美元最低權益要求，但券商端的過渡期最晚到 2027 年 10 月才全部到位——規則本身正在變，範本不會替使用者確認自己的券商規則。

突破之後如果失敗——價格跌破 pivot、或跌破最後一段收縮低點——怎麼處理，不屬於這一節的範圍；那是斷路器與紀律閘門守的地盤（3.3 節）。這裡只負責把候選攤出來，連同它現在的分數與狀態，一起交給第 7 步的人工複核。

## 延伸閱讀

- [`skills/vcp-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/vcp-screener/SKILL.md)
- [`skills/vcp-screener/references/vcp_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/vcp-screener/references/vcp_methodology.md)
- [`skills/vcp-screener/references/scoring_system.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/vcp-screener/references/scoring_system.md)
- [`skills/breakout-trade-planner/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/breakout-trade-planner/SKILL.md)
- [`skills/breakout-trade-planner/references/minervini_entry_rules.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/breakout-trade-planner/references/minervini_entry_rules.md)
