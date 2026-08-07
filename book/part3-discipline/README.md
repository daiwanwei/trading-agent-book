# 開場：09:25，閘門之前

09:25，離開盤剩五分鐘。今天已經闖過兩道關卡：開盤前，1.5 節的 exposure gate 先給了一個不設限的姿態；`swing-opportunity-daily` 接手之後，第 1 步的斷路器也回了 `TRADING_ALLOWED`。桌上該有的東西也都齊了——`vcp-screener` 篩出的候選在 step 7 通過了週線驗證，變成 `validated_setups`；step 8 的 `position-sizer` 把它們換算成具體股數，寫進 `position_sizing`；step 10，`trader-memory-core` 把每一筆的 entry、stop、target 落成 `candidate_journal_entry`，論點已經寫死。三份 artifact 都攤在桌上，`swing-opportunity-daily.yaml` 卻還沒放行——第 11 步，`pre-trade-discipline-gate`，還沒開口。

這五分鐘，Agent 等的不是行情。行情用不著等，開盤前的報價早就看得到了。它等的是自己的判斷：書面計畫、預設停損、部位大小、近期虧損紀錄、市場 regime、斷路器，六項檢查全部通過，才吐得出一個 `GO`。少一項，就是 `NO-GO`——而 `NO-GO` 同樣是一個完整的答案，不是流程卡住。

第一部問的是市場：今天能不能冒新的風險。第二部問的是標的：該挑哪一檔。第三部問的是自己：這一筆該冒多大，以及最後真的要不要按下去——做多少、該不該做，是這一部從頭到尾要回答的問題。

## 本部地圖

**3.1 風險先行的部位計算**——從 step 8 開始：先定願意虧多少，再反推能買幾股，順序不能顛倒；這個數字之後會被 step 10 的論點與 step 11 的紀律閘門原樣核對一次。

**3.2 最後一眼：圖表決策閘**——回到 step 7。候選進部位計算之前，`technical-analyst` 要先在週線圖上篩一次；結構不明確，就算 screener 已經放行，照樣淘汰——這一關只做否決，不生產新的候選。

**3.3 三道閘門的 fail-closed 哲學**——把整週遇到的三道閘門並排看：1.5 節的 exposure gate、step 1 的斷路器、step 11 的紀律閘門。三者各自都會算出一個明確的 verdict——`exposure_decision`、`circuit_breaker_decision`、`pre_trade_discipline_decision`——但真正攔下違規下單的從來不是程式碼，而是願意照著 verdict 走的人。這正是 1.5 節與第一部實作章已經點破的事，這裡不重講一次，只把三道並排看一次它們共通的設計哲學。

**3.4 人與 Agent 的分工**——把前三節收攏成一句話：Agent 負責把判斷做成可稽核、可重複的 verdict；人負責讀懂那個 verdict，並承擔按下按鈕之後的後果。這個分工不是妥協，序章已經先點過名，這一節要把它攤開講。

實作章會把斷路器與 step 7 到 11 這五步實際跑一遍，拿到今天這一筆的 `GO` 或 `NO-GO`。
