# 導讀：怎麼讀一個 skill，以及 agent 的角色

序章走完了一週。接下來五部會依決策順序，一章一章拆開這一週裡用到的工具。

但在跨進第一部之前，有一組問題值得先回答：這 71 個東西，本身長什麼樣？它們彼此是同一種東西嗎？如果不是，分幾種？以及——上游 repo 裡除了 skill，還有沒有別的「角色」？

這一章不談任何交易方法。它只做一件事：把後面三十章會反覆出現的那些名詞，先攤開來看一次結構。讀完之後再進第一部，每一章開頭引用的 `SKILL.md` 與 `references/`，就不會只是路徑，而是知道那裡面裝了什麼、為什麼裝在那裡。

## 一個 skill 長什麼樣

上游每一個 skill 都是一個目錄，裡面最多四樣東西——這在 [`CLAUDE.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/CLAUDE.md) 寫成了強制規格：

`SKILL.md` 是唯一必要的檔案，開頭一段 YAML frontmatter，只有兩個關鍵欄位：`name` 必須與目錄同名，`description` 決定這個 skill 在什麼情況下會被觸發。這兩件事不是慣例而是硬性檢查——[`.pre-commit-config.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/.pre-commit-config.yaml) 裡有一個叫 `skill-frontmatter` 的 hook，名字對不上或描述空著，commit 會被擋下來。

`references/` 放知識，`scripts/` 放程式，`assets/` 放樣板。這條界線劃得比看起來重要：references 是寫給 Claude 讀的領域知識——類股輪動的歷史型態、技術分析的判讀框架、新聞來源的可信度分級；scripts 是拿去執行的程式，負責打 API、抓資料、產報告。一句話總結上游的分工：**scripts 處理 I／O，references 處理知識**。

真正值得記住的是這四樣東西的載入順序，上游把它叫作漸進式載入，一共四層：

1. 只有 frontmatter 先進 Claude 的脈絡，用來判斷「這個 skill 該不該被叫起來」
2. 判斷成立，`SKILL.md` 的本文才載入
3. references **依分析需要**條件式載入，不是全部倒進來
4. scripts 只在被執行時跑，**永遠不會**被自動讀進脈絡

為什麼要這麼麻煩？因為脈絡是有限的。71 個 skill 如果全文都常駐，還沒開始分析就先把空間吃光了。分層的意思是：平常只留一行描述，需要時才展開本文，真的要那份知識時才去讀那份 references。這也解釋了後面三十章的一個寫作習慣——每章引用的往往是某個 skill 的 `references/` 底下某一份特定檔案，而不是整個 skill：因為在真實執行時，被讀進去的也正是那一份。

還有一個推論值得先講：`SKILL.md` 的本文是寫給 Claude 執行的指令，不是寫給人看的說明書。上游要求它用祈使句——「分析這張圖」「產出報告」，而不是「你應該……」或「Claude 會……」。所以直接讀 `SKILL.md` 會覺得語氣有點怪，那不是翻譯腔，是因為你讀的本來就是一份要被執行的稿子。

## 七種功能原型

71 個 skill 不是同一種東西。但「分幾種」不該憑感覺定，[`skills-index.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills-index.yaml) 裡每個 skill 都有一個 `integrations[]` 欄位，每筆帶一個 `type`——這是上游自己定義的分類軸，拿它來切最誠實。

按 `type` 統計 71 個 skill（一個 skill 可以有多個 integration，所以下面是「有幾個 skill 帶到這個 type」，不是互斥的百分比）：

| type | skill 數 | 這一類在做什麼 |
|---|---:|---|
| `calculation` | 33 | 純運算，不對外要資料 |
| `market_data` | 30 | 抓行情、基本面、日線 |
| `local_file` | 12 | 讀本地 CSV／JSON／YAML |
| `web` | 5 | WebSearch 或 WebFetch |
| `image` | 4 | 吃圖表截圖 |
| `screener` | 4 | 走 FINVIZ 之類的篩選服務 |
| `broker` | 2 | 連券商 API |

把這張表折成功能原型，大致是七種：**感測器**量外部世界（市場廣度、上升趨勢參與度）；**篩選器**把宇宙收斂成候選名單（VCP、CANSLIM）；**閘門**讀上游報告吐出一個 verdict；**計算器**做純數學（部位大小）；**記憶**維護狀態（論點的生命週期）；**詮釋者**需要有人看圖才動得了；**編排器**負責叫其他 skill。

這裡面有一個數字值得停下來看。整份索引裡，`integrations` **只有** `calculation` 一種、完全不對外要資料的 skill 有 28 個。而輸出欄位裡帶著 decision 或 gate 字樣的 skill——`exposure-coach`、`drawdown-circuit-breaker`、`pre-trade-discipline-gate`、`contrarian-setup-gate`——一共 4 個。

**這 4 道閘門，全部落在那 28 個純計算的 skill 裡面，一個不漏。**

這不是巧合，是設計。閘門是整條決策鏈上「說不」的那一環，而它們從構造上就不依賴網路、不依賴 API 額度、不依賴任何可能超時或回傳半截資料的外部服務。第三部要講的 fail-closed 哲學，在這一層已經先被實現了一次：一道會因為網路斷線而失效的閘門，不是閘門。

順帶一提那 2 個帶 `broker` 的——`portfolio-manager` 與 `parabolic-short-trade-planner`。整個 repo 裡摸得到券商 API 的就這兩個，而它們摸到的是什麼、不能摸什麼，3.4 節已經算過帳。

## 四個角色包：skillsets

再往上一層，[`skillsets/`](https://github.com/tradermonty/claude-trading-skills/tree/main/skillsets) 有四個 YAML，把 skill 綁成角色包：

| skillset | required | recommended | optional |
|---|---:|---:|---:|
| `market-regime` | 3 | 2 | 6 |
| `swing-opportunity` | 6 | 3 | 3 |
| `core-portfolio` | 2 | 3 | 2 |
| `trade-memory` | 2 | 2 | 1 |

三層分級是這裡最有用的資訊。以 [`market-regime`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/market-regime.yaml) 為例：required 只有 `market-breadth-analyzer`、`uptrend-analyzer`、`exposure-coach` 三個——少一個，這個角色就不成立；recommended 兩個是 `market-top-detector` 與 `macro-regime-detector`；剩下六個 optional 是加分項。所以「要開始跑市場狀態」的最小裝備是三個 skill，不是十一個。

要注意的是，上游同時存在三種正交的切法，讀的時候別混在一起：

- **8 個 category**（`market-regime`、`core-portfolio`、`swing-opportunity`、`trade-planning`、`trade-memory`、`strategy-research`、`advanced-satellite`、`meta`）——每個 skill 歸屬**一個**，是分類
- **4 個 skillset**——是角色包，講「扮演這個角色要裝哪些」
- **11 條 workflow**——是執行順序，講「照什麼次序跑、在哪裡停下來問」

同一個 skill 會同時出現在這三種切法裡，位置不衝突。本書五部走的是第三種——決策順序；附錄 A 走第一種；這一節講的是第二種。

## 真正的 subagent：agents/

前面講的都是 skill。但上游還有一個目錄，本書前面三十章一次都沒提到——[`agents/`](https://github.com/tradermonty/claude-trading-skills/tree/main/agents)，裡面只有兩個檔案，卻是整個 repo 裡唯一真正意義上的「角色扮演」。

[`scenario-analyst`](https://github.com/tradermonty/claude-trading-skills/blob/main/agents/scenario-analyst.md) 的 frontmatter 指定 `model: sonnet`，本文第一句要它扮演一位有二十年以上資歷的中長期股票組合基金經理人。它收一則新聞標題，建構未來十八個月的情境，做 1st／2nd／3rd-order 的產業衝擊分析，然後選股。

[`strategy-reviewer`](https://github.com/tradermonty/claude-trading-skills/blob/main/agents/strategy-reviewer.md) 同樣是 sonnet，同樣是基金經理人——但**是另一位**。它的職責寫得毫不客氣：對既有分析做批判性檢視，指出盲點、誤讀，以及被忽略的替代情境。

兩者怎麼串起來，寫在 [`commands/scenario-analyzer.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/commands/scenario-analyzer.md) 的執行程序裡：第三步用 Agent 工具、`subagent_type: "scenario-analyst"` 跑主分析；第四步用 `subagent_type: "strategy-reviewer"`，而餵給它的 prompt 是**第三步分析結果的全文**。

這個設計值得說清楚。第二個 agent 拿到的不是原始題目，是第一個 agent 的完整結論——它的工作不是重做一次分析，而是**攻擊那個結論**。這跟 skill 之間的關係完全不同：skill 是流水線，上游的 artifact 往下游流，下游信任上游；這兩個 agent 是對抗關係，後者存在的理由就是前者可能錯。

一個 skill 是「一套被封裝的方法」，一個 agent 是「一個被賦予立場的人格」。上游 71 個 skill，agent 只有兩個——而這兩個之所以需要人格，正因為它們做的是最無法演算法化的事：判斷一則新聞十八個月後會怎麼發酵，以及判斷另一個人的判斷錯在哪裡。第五部 5.3 節談審查與否證時會再碰到同一個母題，只是那裡的否證對象是策略草稿，不是情境分析。

## 這些角色共同的邊界

四層講完，有一條線貫穿全部：不管是純計算的閘門、連券商的組合管理、還是有二十年資歷人格的基金經理人 agent，沒有任何一個角色被授權替人按下最後那個按鈕。

這條線怎麼畫、為什麼畫在這裡、以及 `decision_gate: true` 到底保證了什麼又沒保證什麼——3.4 節整章在算這筆帳，這裡不重複。讀完那一章再回頭看這一章的七種原型，會多看到一件事：原型的差別在於「資訊怎麼進來」，而它們的共同上限在於「判斷到哪裡為止」。

現在可以進第一部了。週一早上六點半，第一件事是量市場的體溫。

## 延伸閱讀

- [`CLAUDE.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/CLAUDE.md)
- [`skills-index.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills-index.yaml)
- [`skillsets/README.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/README.md)
- [`skillsets/market-regime.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/market-regime.yaml)
- [`agents/scenario-analyst.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/agents/scenario-analyst.md)
- [`agents/strategy-reviewer.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/agents/strategy-reviewer.md)
- [`commands/scenario-analyzer.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/commands/scenario-analyzer.md)
- [`.pre-commit-config.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/.pre-commit-config.yaml)
