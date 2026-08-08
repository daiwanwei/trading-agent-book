# 3.4 人與 Agent 的分工

前三節分別看過部位計算、圖表決策閘、與三道 fail-closed 閘門各自的 verdict。這一節把鏡頭拉遠，看的不是某一步特有的設計，而是寫進上游 repo 全部 11 條 `workflows/*.yaml` 骨架裡的通則：Agent 算什麼、人守什麼、以及為什麼這條線畫在這裡。

## Agent 做什麼

Agent 做的事，說到底都是同一件事的不同版本：把資訊變成一個可稽核的判斷。1.5 節的 `exposure-coach` 讀廣度、上升趨勢參與度、頂部風險三份報告，收斂成一句 `allow`／`restrict`／`cash-priority`；3.1 節的 `position-sizer` 把「願意虧多少」換算成股數；3.3 節的斷路器讀 thesis YAML，算出 `TRADING_ALLOWED`／`COOLDOWN`／`HALTED`；`pre-trade-discipline-gate` 把六項檢查收斂成 `GO`／`NO_ACTIONABLE_ORDERS`／`REVIEW_REQUIRED`／`NO_GO`。全部都是計算：讀資料、套規則、輸出一個明確值，換一組輸入就能重跑一次拿到同一個答案。

這件事在 workflow 裡有一個共用的標記。用 grep 掃過全部 `workflows/*.yaml`，`decision_gate: true` 一共出現 30 次，分布在全部 11 條 workflow——每一條至少一個，最多的 `shapiro-contrarian.yaml` 與 `stockbee-ep-daily.yaml` 各有 5 個。上游 schema（`docs/dev/metadata-and-workflow-schema.md` 的校驗規則 `WF005`）對這個標記只要求一件事：必須帶一句非空的 `decision_question`。也就是說，`decision_gate: true` 保證的是「這一步問了一個明確的問題」，不保證「這一步的答案已經被誰確認過」。

這正是這一節要說清楚的分界線：`decision_gate: true` 是 Agent 停下來、把問題攤開的地方——不是 Agent 自己拍板決定的地方。斷路器算出 `HALTED`，那是計算結果；接下來要不要真的暫停交易，是另一件事。

## 人做什麼

Agent 停下來之後，人要做兩件事：讀懂那個 verdict，以及做那個 verdict 換不來的動作——下單。

先看 verdict 這一半。每一個 `decision_gate: true` 步驟最終要有人看過、認可，而不是讓輸出直接流向下一步——`market-regime-daily.yaml` 的 `manual_review` 第一條就是「確認輸出不是拿來當買賣訊號」；`swing-opportunity-daily.yaml` workflow 層級的 `manual_review` 清單裡有一條對應第 7 步的檢查：「篩選器通過但週線不明確者一律否決」；`kanchi-dividend-weekly.yaml` 第六步的 `decision_question` 寫死論點在真正成交之前不得轉為 `ACTIVE`。這些都不是驗證器能自己核對的事——沒有任何程式會去確認交易者真的讀過那張圖、真的接受了那個 `restrict` 姿態。

再看下單這一半，這是整套系統裡唯一「不可轉讓」的動作。用 grep 掃過全部 `workflows/*.yaml`，逐字寫著「no auto-execution／placed manually」的只有 3 條——`stockbee-ep-daily.yaml`、`swing-opportunity-daily.yaml`、`shapiro-contrarian.yaml`，同一句話：「All orders are placed manually at the broker; no auto-execution.」另外兩條走到下單這一步的 workflow 用了不同措辭、同一個意思——`core-portfolio-weekly.yaml` 的 `manual_review` 要求「確認再平衡的單是在券商手動輸入，不是自動執行」；`kanchi-dividend-weekly.yaml` 兩處寫著「每一筆買進都在券商手動輸入」。11 條 workflow 裡，真正走到「下單」這一步的是這 5 條，沒有一條讓 Agent 碰到券商 API。其餘 6 條——`market-regime-daily`、`monthly-performance-review`、`multi-asset-opportunity-daily`、`stockbee-20pct-study-daily`、`stockbee-fluency-loop`、`trade-memory-loop`——本來就停在姿態、假說或事後檢討，不涉及新單，通篇也找不到「order」這個字。

`docs/dev/metadata-and-workflow-schema.md` §2.4 講 `prerequisite_workflows` 時補了一句更廣義的話：驗證器不檢查前置 workflow 是否真的先跑過，「是交易者的責任（未來也會是 Navigator 的責任）」。順序如此，執行也是如此——序章寫過一句話，這裡把它正式展開：承擔後果的人，必須是按下按鈕的那一個。Agent 交出 verdict，人交出那一下點擊；兩件事誰都不能替誰做。

## 為什麼這樣切

這條分工線不是技術做不到自動化才退而求其次的妥協。上游確實有能連上券商 API 的 skill——`portfolio-manager` 走 Alpaca——但它只出現在週末的組合檢視流程裡，沒有被接到任何一條當日下單流程的末端。能做的事，選擇不做，才是設計。

3.3 節引過斷路器 `SKILL.md` 對自己的定位——「a recommendation and recordkeeping tool」，明文拒絕替使用者做出「不准交易」這個決定，只負責把數字算清楚、把紀錄留下來。放到這一節看，這句自我描述不只是斷路器一個 skill 的定位，是整個分工哲學的縮影：工具負責計算與記錄，不負責替人承擔那個決定。

把紀律外包給程式，看起來省事，代價是人會漸漸失去對規則本身的所有權——如果「不能超過 2% 風險」只是螢幕上一個擋住去路的紅字，而不是自己理解過、認同過的邊界，第一次遇到情緒夠強的行情，人只會想辦法繞過那個紅字，而不是遵守它。留一道人工確認，逼的是人每次都要重新面對「我真的同意這個判斷嗎」，而不是把責任交給一個永遠不會被追究的演算法。

還有一個通則，把這條分工線縫進了整本書的下一部。用 grep 掃過全部 11 條 `workflows/*.yaml`，`journal_destination: trader-memory-core` 出現 11 次，一條不少——不管是姿態判斷、篩選流程、組合檢視、存股盡調、平倉檢討還是月度總結，每一條 workflow 的終點都寫著同一個目的地。這不是巧合：第四部要檢討的，正是這一節切開的兩半——Agent 的判斷對不對、人的執行守不守規矩——而這兩半唯一能被檢討的方式，是先被寫進同一本帳。

走到這裡，可以把四部合起來看一次。第一部問的是市場：今天能不能冒新的風險。第三部問的是自己：這一筆該冒多大、以及最後真的要不要按下去。兩者問的都是「自己這一邊」的問題，一個對外看盤面，一個對內看帳戶與行為。中間的第二部只做一件事——做什麼：把姿態允許的空間，填進具體的候選名單。後面的第四部收在另一端——學什麼：把這一節切開的判斷與執行，事後攤開來檢討，變成下個月的規則。四部合起來，才是一個完整的循環：問市場、選標的、擔風險、學教訓，然後回到問市場。

## 延伸閱讀

- [`workflows/swing-opportunity-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml)
- [`workflows/core-portfolio-weekly.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/core-portfolio-weekly.yaml)
- [`workflows/kanchi-dividend-weekly.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/kanchi-dividend-weekly.yaml)
- [`workflows/stockbee-ep-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/stockbee-ep-daily.yaml)
- [`workflows/shapiro-contrarian.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/shapiro-contrarian.yaml)
- [`docs/dev/metadata-and-workflow-schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/docs/dev/metadata-and-workflow-schema.md)
- [`skills/drawdown-circuit-breaker/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/drawdown-circuit-breaker/SKILL.md)
