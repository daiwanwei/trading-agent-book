# 3.2 最後一眼：圖表決策閘

## 場景

`swing-opportunity-daily.yaml` 第 7 步，`skill: technical-analyst`。這一步吃進去的候選最多——`consumes` 一次列了五個來源：step 2 `vcp-screener` 必產出的 `vcp_candidates`，加上 step 3 到 6 四個標成 `optional: true` 的篩子分別產出的 `momentum_burst_candidates`、`exhaustion_hammer_candidates`、`canslim_candidates`、`theme_candidates`。無論上游哪幾個 skill 真的跑了、篩出了誰，這一步都要把它們攤在同一張週線圖前重新過一遍。`decision_gate` 標成 `true`，輸出只有一個 artifact，`validated_setups`，而且是必產出。這批倖存者，就是 3.1 已經交代過的、下一步 `position-sizer` 拿去換算股數的那個輸入。

step 7 跟前面五步不一樣的地方，不在於篩得更嚴，而在於篩的東西完全變了。step 2 到 6 讀的是數字——估值門檻、動能分數、成交量爆量條件、CANSLIM 七要素、主題曝險；step 7 讀的是一張圖。同一個候選能不能活到 `validated_setups` 裡，取決於它的週線結構「看起來」乾不乾淨——這是整條 pipeline 裡唯一一個由視覺判讀主導、而非由公式算出結果的關卡。

## 方法論

`technical-analyst` 的 `SKILL.md` 開頭把定位寫得很窄：「analyzing weekly price charts... Use this skill when the user provides chart images」。Prerequisites 只有一條實質要求——「User must provide weekly timeframe chart images for analysis」——旁邊直接註明「No API Keys Required: This skill analyzes user-provided images; no external data fetches」。`technical_analysis_framework.md` 的 Core Principles 第三條重申同一件事：「All analysis uses weekly charts for medium to long-term perspective」。週線是刻意的選擇，不是隨手用的時框——短天期的雜訊被濾掉，留下的是能撐得住一筆波段交易的結構。

框架文件把判讀拆成幾個面向：趨勢（用高點/低點是墊高還是走低來判斷方向，配合均線排列判斷強弱）、支撐壓力（同一價位要有 2-3 次觸及才算數，跌破的支撐可能反過來變成壓力）、均線（20 週、50 週、200 週三條，看價格站在哪一側、均線本身的斜率，以及有沒有出現黃金交叉或死亡交叉）、成交量（價漲量增才是健康確認，價漲量縮是警訊）、型態（反轉如 hammer、engulfing，或延續如旗形、三角），最後綜合成 2-4 個機率情境，機率總和要求等於 100%。這套語彙本身沒有替 step 7 定義任何及格線——它只是 Claude 判讀一張圖時共用的詞彙表。

值得特別點出：這份框架文件全文沒有出現「Stage」這個字，也沒有點名 Weinstein 或 Minervini 的歸屬。step 7 要找的「Stage 2 上升趨勢」，其定義來自 workflow 自身的 `decision_question`，不是 `technical-analyst` 自己的參考文件——這正是下一節要講的機制。

框架文件最後還留了一節行為提醒，跟前面六個判讀面向平行、但性質不同：避免確認偏誤，同時考慮多頭與空頭的可能；讓圖說話，不要硬套型態；承認不確定——不是每張圖都會給出清楚訊號。這幾條提醒不是判讀的技術內容，但它們正是稍後 step 7 那條「不明確就否決」規則的注腳。

## 機制

`decision_question` 只問一件事：候選裡誰有「乾淨的週線結構」，能通過人工複核。及格的結構只有三種：Stage 2 上升趨勢、tight base（緊縮的整理區），或是 Stockbee 式從受控底部展開的區間擴張。三選一，符合其中一種就算過關；一種都套不上，就不過。exhaustion hammer 候選還要多一道檢查——`decision_question` 要求回檔不具論點破壞性、且風險到當日低點是可以承受的；`manual_review` 把這一點講得更具體，明講要確認回檔不是由會摧毀論點的新聞事件引發。這不是額外加碼的審查，而是因為 exhaustion hammer 這個型態本身就長在一次急拉之後的回檔裡，光看「有沒有 Stage 2 結構」不足以分辨它究竟是趨勢真的轉弱，還是健康的獲利了結。

`manual_review` 另有一條更直白的規則：篩選器通過但週線不明確的候選一律否決，即使 screener 已經放行。這句話界定了這一步的權限邊界——它從不新增候選，只從上游五個篩子已經給出的名單裡刪人。

判讀由誰做、用什麼工具做，`SKILL.md` 分得很清楚。`technical-analyst` 唯一的 CLI 入口 `scripts/check_weekly_price_action.py`，屬於一個完全獨立、附加式的「Contrarian Confirmation Mode（Shapiro Step 3）」——只在明確要求逆勢確認時才啟動，Guardrails 明講「the existing chart-analysis workflow above is unchanged」。在那個模式底下，圖表仍是主要輸入，腳本只是「chart-primary, script-fallback」裡的備援：沒有圖可讀、或想要一個可稽核的確定性結果時才會跑它。`swing-opportunity-daily` 第 7 步用的是前者，也是唯一一種——純圖表分析工作流。換句話說，`validated_setups` 這份名單是 Claude 一張一張讀圖判讀出來的，背後沒有任何演算法腳本替它做篩選。

## 判讀與誤用

這一步的本質是否決權。它不生產候選——五個上游 skill 已經把候選生出來了；它能做的唯一動作是刪除。把它想成一個篩子而不是一台生成器，是理解 pipeline 為什麼在這裡放一個 `decision_gate: true` 的關鍵：在 step 1 到 step 7 之中，只有 step 1 的斷路器與 step 7 這裡的 gate 標成 true，中間五個候選生成步驟（step 2 到 6）全部是 false。

「篩選器通過但週線不明確者一律否決」這句規則，字面上看很嚴苛——沒有「先觀察一天再說」的選項。但正是這種沒有例外的措辭，讓它比較安全。「不明確」本身不是一種等待補完的資訊缺口，而是判讀當下就存在的證據：結構看不清楚，往往代表底部還沒走完、或突破還沒確認，多等一天不會讓圖變乾淨，只會讓人在等待裡悄悄說服自己看見了原本不存在的訊號。`SKILL.md` 的 Objectivity Requirements 早就把這條防線寫進分析師的行為準則——「Express uncertainty clearly when signals are ambiguous」；`decision_question` 做的事，是把這份誠實的不確定，直接翻譯成一個可執行的否決，不留給交易者用意志力去填補的空間。

這裡還有一個容易被誤讀的例外。`technical-analyst` 的核心原則之一是「Pure Chart Analysis」——只看圖，不引入新聞、基本面或市場情緒，`SKILL.md` 與框架文件都把這條原則寫在最前面。但 exhaustion hammer 那道額外檢查，要求判斷回檔是不是由摧毀論點的新聞事件引發——這件事無法只靠盯著 K 線回答。把「純圖表分析」套用到這一項檢查上、拒絕引入任何外部脈絡，會誤解 step 7 真正的要求：這道 gate 對大多數候選堅持圖表獨立判讀，唯獨對 exhaustion hammer 明確容許、甚至要求跨出圖表去核對新聞脈絡。

`technical-analyst` 還有另一條完全不同的路徑：在 Shapiro 逆勢流程第 3 步，同一張週線圖被拿來確認的不是突破結構，而是價格行為的反轉訊號（見 `contrarian-confirmation-checklist.md`）——這條路徑跟本章的候選驗證用途無關，留到第二部 2.5 再展開。

## 延伸閱讀

- [`skills/technical-analyst/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/technical-analyst/SKILL.md)
- [`skills/technical-analyst/references/technical_analysis_framework.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/technical-analyst/references/technical_analysis_framework.md)
- [`skills/technical-analyst/references/contrarian-confirmation-checklist.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/technical-analyst/references/contrarian-confirmation-checklist.md)
- [`workflows/swing-opportunity-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml)
