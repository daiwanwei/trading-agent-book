# 1.5 收斂成一個姿態

## 場景

06:44，離 07:30 交棒給 `swing-opportunity-daily` 還有 46 分鐘。桌上躺著三份剛出爐的報告：`market_breadth_report`、`uptrend_report`、`top_risk_report`——1.1 到 1.2 節走過的三個 skill，各自留下的痕跡。三份報告量的是完全不同的東西：一份是今天到底有多少股票真的在漲，一份是上升趨勢的參與廣度，第三份（如果第 3 步沒被跳過）是頭部風險積累到什麼程度。三份都攤開了，卻沒有一份告訴 Agent 接下來該做什麼。

[`market-regime-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml) 的第 4 步「Decide exposure posture」把這三份 `consumes` 進去，交給 `exposure-coach`。這是全條 workflow 裡唯一一個 `decision_gate: true` 的步驟，YAML 把要回答的問題明文寫成 `decision_question`：「Given today's breadth, uptrend participation, and top risk, is new swing trade risk allowed, restricted, or cash-priority?」——翻成白話，就是拿這三份報告當證據，今天新的波段交易風險，該收斂成 allow、restrict，還是 cash-priority 這三個字裡的哪一個。

`exposure-coach/SKILL.md` 把這件事講得更直白：它要回答的是「solo trader 的核心問題」——現在該把多少資本投入股票部位——而且明講這個判斷發生在**任何個股分析開始之前**。三份報告收斂出的不是一支股票的買賣建議，是今天整個交易日允許承擔多少風險的天花板。這就是「姿態」（posture）這個詞，第一次在這本書裡拿到它的正式定義。

## 方法論

為什麼要把八個維度的分數收斂成一個詞，而不是把 breadth、uptrend、regime 這些原始分數整批攤出來，讓人自己判讀？`SKILL.md` 的 Key Principles 給了三條理由：Safety First——輸入不完整或彼此衝突時，預設更低的曝險；Regime Alignment——讓宏觀 regime 設定基準，其他訊號只在基準內微調；Actionable Output——永遠要產出一個明確的建議，而不只是把資料堆在一起。第三條點名了「一堆分數」的問題：資料聚合本身不是答案，沒有收斂成一個動作，使用者面對八個各說各話的分項，還是得自己再做一次仲裁——這正是決策疲勞的來源，也是這套設計刻意迴避的事。

`exposure_framework.md` 把仲裁規則分成兩層。第一層是訊號大致同向時：八個分項（regime 25%、top risk 20%、breadth 15%、uptrend 15%、institutional 10%、sector 5%、theme 5%、ftd 5%）用固定權重合成一個 composite score，分歧被平均掉。第二層才是真正的仲裁——`Recommendation Logic` 底下，REDUCE_ONLY 與 CASH_PRIORITY 各自用「OR」串起來三個條件，但第三個條件不一樣：REDUCE_ONLY 是 composite score 落在 30–49，或 top risk score 落在 25–39（提醒：這裡的 top risk score 是 `exposure_framework.md` 標記的「Top Risk Score (Inverted)」，跟 1.2 節「分數越高，頭部風險越高」的頭部風險分數方向相反，是一次獨立計算——不是把那個分數拿來做代數反轉，而是用派發日數與頭部機率另外訂了一張分級表——風險越高，這個分項的分數反而越低），或關鍵輸入缺兩項以上，任一項成立就觸發；CASH_PRIORITY 是 composite score 低於 30，或 top risk score 低於 25，或「regime 為 Contraction，且 top risk score 低於 50」同時成立，同樣任一項就觸發。也就是說，就算其他分項都健康，只要 top risk 這一項亮紅燈，composite 平均分數可能還撐在及格線之上，OR 邏輯照樣讓這一項單獨否決，把姿態往保守拉。`regime_exposure_map.md` 對訊號衝突的原則寫得更直接：預設採更保守的姿態、調降信心等級、把衝突寫進 rationale——不是取折衷，是靠向壞消息那一邊。

輸入缺漏被當成另一種形式的衝突處理。`exposure_framework.md` 的 Missing Input Handling 規定：缺的分項要從加權平均裡剔除、信心等級按比例調降，而且 Regime、Top Risk、Breadth 這三個「關鍵輸入」每缺一項，還要再扣 10% 的曝險上限——資料不完整不會被當成中性，而是被當成一種需要額外折讓的風險。

## 機制

`SKILL.md` 列出的五項輸出欄位，落到 JSON schema 裡分別是：`exposure_ceiling_pct`（0–100%，最大建議股票配置，也就是淨曝險上限）、`bias`（growth-vs-value 傾向，`exposure_framework.md` 的 Bias Determination 定義了 Growth、Value、Neutral 三種判定條件）、`participation`（BROAD 健康、對 NARROW 脆弱，參與廣度）、`recommendation`（NEW_ENTRY_ALLOWED、REDUCE_ONLY，或 CASH_PRIORITY 三選一）、`confidence`（HIGH、MEDIUM、LOW），外加 `component_scores`（八個分項原始分數）、`inputs_provided` 與 `inputs_missing`、一段 `rationale` 文字。workflow 的 `decision_question` 用 allow / restrict / cash-priority 三個詞問問題，落到 skill 自己的 schema 裡，寫的是更明確的三個枚舉值——同一個三選一，工作流層與 skill 層各自用了自己的詞彙。

Regime 是設定基準的那一層。`regime_exposure_map.md` 給五種 regime 各自的基準曝險與傾向：Broadening 80–100%、Growth 傾向；Concentration 60–80%、Quality Growth；Transitional 40–60%、中性偏防禦；Inflationary 50–70%、Value／實質資產；Contraction 10–30%、防禦／現金，直接對應 CASH_PRIORITY。這個基準不是固定的——`Within-Regime Adjustments` 列了四條微調：廣度與 regime 一致不調整，負向背離扣 10%、正向背離加 5%；頂部風險偏低加 10%、風險升高扣 15%、風險達臨界值直接強制 CASH_PRIORITY，不管 regime 多樂觀；法人強力買超加 5%、強力賣超扣 10%；FTD 訊號達臨界等級再扣 15%。這正是「Regime 設基準、其他訊號只在框內微調」這條原則的落地——除了 top risk 臨界值這個例外，連框都不保。

`exposure-coach` 這一步本身不碰任何付費 API——`skills-index.yaml` 把它的 integration 標成 `local_calculation`、`requirement: not_required`，備註是「synthesizes signals from other skills; pure calculation」。它吃的是別的 skill 已經產出的 JSON，純計算、離線可跑。但值得先點出一個結構性落差：`market-regime-daily` 只把 breadth、uptrend、top risk 三份報告接進第 4 步，`SKILL.md` 完整列出的八維度輸入表裡，regime、ftd、theme、sector、institutional 另外五項——1.3、1.4 節已經各自確認過，`ftd-detector` 與 `macro-regime-detector` 都沒有被排進任何一條 workflow 的步驟編號——沒有一項被這條每日 workflow 排進步驟。判讀時這件事有具體後果，留到下一節展開。

## 判讀與誤用

全書最重要的一句話，就藏在 `market-regime-daily.yaml` 的 `when_not_to_run` 裡：不要把這個輸出當成單獨的買賣訊號使用，`exposure_decision` 是一個姿態（allow / restrict / cash-priority），不是指令。**姿態不是訊號**——這五個字，是後面兩部都會反覆回扣的定義。訊號說的是「買這一檔」；姿態說的是「今天我願意讓多少風險上場」。`allow` 從來不等於「買」，它只是把後面找標的、驗證結構、算部位、寫論點那一連串動作的門解鎖；`restrict` 或 `cash-priority` 也不是「賣」的指令，只是把那扇門關上。

門關上之後，後果是具體的，但落實的方式值得說清楚。`market-regime-daily.yaml` 的 `manual_review` 清單最後一條明講：`exposure_decision` 偏限制時，就把第二部的 `swing-opportunity-daily` 往後延。`swing-opportunity-daily.yaml` 自己也在開頭列了一段 `prerequisite_workflows`，指名 `market-regime-daily` 與它的 `exposure_decision`——但那個區塊上方掛著一行註解：僅供參考，驗證器不檢查跨 workflow 的順序，細節見 `docs/dev/metadata-and-workflow-schema.md` §2.4；那份文件把話說得更白，順序有沒有被遵守，是交易者自己的責任，不是程式碼的責任。這正是序章已經點出的性格：這條前置關係是寫給人看的紀律，不是程式攔得住的東西。

姿態仍然是全書遇到的第一道 fail-closed 閘門，但它把守的方式，其實已經預告了第三部的答案：真正攔住風險的那幾道閘門，同樣不是靠程式碼把使用者鎖死，而是刻意設計成人與 Agent 都必須主動核對的檢查清單。系統選擇把攔截的責任交給人，不是因為它做不到別的，而是它認定這正是該由人承擔的那一段。

姿態不完整時，同樣要打折看待。三份報告裡，只有 breadth 與 uptrend 是每日必經、`required: true` 的步驟，top risk 是可選的；而上一節點出的另外五個輸入維度，沒有一項被這條每日 workflow 排進步驟。照 `exposure_framework.md` 自己的信心等級表，少於四個輸入就只能落在 LOW——就算三步都跑齊，也只有三份輸入，仍然不到 MEDIUM 需要的四份。把每天例行跑出來的姿態，直接當成跟八維度齊全時同等份量的判斷，是另一種常見的誤讀。

## 延伸閱讀

- [`skills/exposure-coach/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/exposure-coach/SKILL.md)
- [`skills/exposure-coach/references/exposure_framework.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/exposure-coach/references/exposure_framework.md)
- [`skills/exposure-coach/references/regime_exposure_map.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/exposure-coach/references/regime_exposure_map.md)
- [`workflows/market-regime-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml)
