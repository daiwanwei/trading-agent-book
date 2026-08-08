# 首頁：這本書在說什麼

有一個 AI 交易 Agent，它每天早上六點半開始工作。

它做的第一件事不是找股票，而是量市場的體溫，決定今天該不該冒風險。姿態允許，偵查工具才出動；名單出來了，還得再過三道閘門，才輪到人打開券商介面。收盤後記帳，週末檢視存股，平倉後寫檢討，月底把一個月的錯誤歸類成下個月的規則，研究日再回頭改進自己用的工具。

這本書寫的就是這一週。

素材來自 [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)——收錄 71 個交易 Claude Skills 的開源專案。這本書不是它的翻譯，而是一次策展：把散落在 71 個目錄裡的方法論，依照上游 [`workflows/`](https://github.com/tradermonty/claude-trading-skills/tree/main/workflows) 定義的真實決策順序重新串起來。你看到的不會是工具清單，而是一條決策鏈。

## 怎麼讀

**只想看懂**：讀序章，再讀五部的開場與敘事章節，不必安裝任何東西。

**想動手跑**：每一部的最後一章都是「實作」，列出指令、API 需求與產出檔案位置。從第一部的 `market-regime-daily` 開始最好：十五分鐘跑得完，完全免 API。

## 五部地圖

- **第一部　市場狀態**——今天能不能做？廣度、參與度、頂部與底部訊號，收斂成一個 `exposure_decision` 姿態。
- **第二部　選股**——做什麼？五大流派的偵查工具，從 Minervini 的 VCP 到 Shapiro 的逆勢管線。
- **第三部　風險與紀律**——做多少、該不該做？部位計算、圖表決策閘，與三道 fail-closed 閘門的設計哲學。
- **第四部　交易記憶**——平倉之後學什麼？論點的生命週期、誠實的事後檢討，與把行為變成資料。
- **第五部　策略研究**——Agent 如何進化？從觀察到假說、到策略草稿、到審查與否證，終點是 Agent 改自己的 skills。

## 這本書的立場

承襲上游專案，三句話，序章會展開：

**輸出是姿態，不是訊號。** `exposure_decision` 說 `allow`，意思是「今天可以考慮風險」，不是「買這一檔」。

**所有訂單由人手動下。** 上游 [`swing-opportunity-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml) 的 `manual_review` 講得斬釘截鐵：訂單一律在券商手動輸入，不自動執行。Agent 的工作止於 GO / NO-GO。

**本書不提供投資建議。** 這裡談的是決策流程怎麼設計、閘門為什麼要 fail-closed，不是該買什麼。
