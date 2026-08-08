# 4.2 誠實的事後檢討

## 場景

`trade-memory-loop` 是逐筆觸發的：一個部位收尾，不論是全部出清還是只賣掉一部分，這條迴圈就會被叫起來；還沒平倉的論點不算數，那是 `trader-memory-core` 該直接處理的事，跟這條迴圈無關。第 1 步先把結果收斂成 `closed_thesis_record`，`decision_gate` 是 `false`——README 開場已經講過，這一步只負責記錄，不做判斷。真正的判斷從第 2 步才開始：`signal-postmortem` 接手 `closed_thesis_record`，`decision_gate` 是 `true`。這一節要講的，就是這一步實際在做什麼。

## 方法論

一筆交易的結果，跟做出這筆交易的過程，是兩件可以完全脫鉤的事。運氣好的時候，一個站不住腳的判斷照樣能賺錢；運氣差的時候，一套邏輯嚴謹、執行到位的計畫也可能倒賠。`signal-postmortem` 在這裡被賦予的任務，是把這兩件事拆開來看，而不是拿損益的正負號直接倒推誰做得對。

第 2 步的 `decision_question` 只問一件事，但要求給出唯一答案：這筆結果該歸咎給哪一項——是當初的假設本身有漏洞（論點品質），是下單、停損的動作沒照計畫落實（執行），是當下的大盤風向翻了（市場環境），還是壓根沒有值得歸咎的原因，就只是機率（隨機性）？四選一，不能都選，也不能都不選。把機率也擺進選單，是最容易被輕視、卻也最重要的一筆設計——它承認有一部分交易結果，事後怎麼拆解都找不到值得複製或修正的地方，硬要湊一個理由出來，才是對檢討這件事本身不誠實。

`mae_pct`、`mfe_pct` 這兩個數字，在這一步開始派上用場——4.1 已經定義過它們，這裡不重講，只講詮釋。放進事後檢討，它們補的是出場價一個數字看不出來的東西：出場點只留下路徑的終點，`mae_pct`、`mfe_pct` 則把整段路徑攤開——停損被打到之前，價格究竟逼近過多深；達到目標之前，帳面浮盈又曾經衝到多高。同一個 `pnl_pct`，配上不同的 `mae_pct`、`mfe_pct`，指向的根因可能完全不同：一路小幅震盪、乾脆照計畫出場，跟中途大幅逆行又爬回來停損，兩者外觀相同，但後者更值得回頭檢查停損距離或部位管理有沒有調整空間。

## 機制

`signal-postmortem` 自己的分類軸，跟 `trade-memory-loop` 拿它來做的事，其實是兩把不同的尺，容易被誤認成同一件事。

`SKILL.md` 與 `outcome-classification.md` 定義的，是訊號準確度這把尺：`postmortem_recorder.py` 拿 `predicted_direction` 跟 5 日、20 日的 `realized_returns` 對照，判進四個正式類別之一——`TRUE_POSITIVE`（方向猜對）、`FALSE_POSITIVE`（方向猜錯，依虧損幅度再分 `MILD` 與 `SEVERE`，跌破 −2% 才算 `SEVERE`）、`MISSED_OPPORTUNITY`（訊號沒被採用，但事後看報酬達到 2% 以上）、`REGIME_MISMATCH`（訊號失準的主因是持有期間市場 regime 真的換了，不是判斷本身出錯）；報酬絕對值低於 0.5% 記作 `NEUTRAL`——這仍是走完整套流程後的正式分類，只是不計入 `TRUE_POSITIVE`／`FALSE_POSITIVE` 的命中率統計；只有訊號根本沒被採用、事後看也不會獲利，才歸 `SKIPPED`，直接省了整套 `postmortem`。這一把尺答的是「方向猜對了沒有」。

`trade-memory-loop` 第 2 步要的不是這件事。它的 `decision_question` 問的是上一段那組四選一的根因——假設本身、下單執行、大盤風向，還是機率，產出 `postmortem_findings`——名字對不上 `outcome_category` 的四個類別，量的也不是同一個維度：一筆 `TRUE_POSITIVE` 背後完全可能只是猜對了方向的運氣；一筆 `FALSE_POSITIVE` 背後的論點也可能完全站得住，只是市場環境變了。這正是 `REGIME_MISMATCH` 被單獨列出來、不併進 `FALSE_POSITIVE` 的理由——把「方向錯了」跟「判斷本身錯了」分開算，兩份文件在各自的層級上，其實守的是同一種分寸。

`postmortem_findings` 產出後，`downstream_hints` 指向 `monthly-performance-review`，供月度做模式層級的彙整；在 `trade-memory-loop` 內部，它還跟 `closed_thesis_record` 一起餵給可選的第 3 步——`trade-performance-coach`，把 `findings` 轉成下一個交易時段可以遵循的 `next_session_operating_rules`。哪一條規則該貼上哪個標籤，留給 4.3 整章展開，這裡先記下它是 `postmortem_findings` 的下一站。

跟這條路徑平行、服務對象卻不同的，是 `feedback-integration.md` 記載的另一條迴路：`postmortem_analyzer.py` 從累積的 `postmortem` 記錄產出 `weight_feedback.json`，餵給 `edge-signal-aggregator` 校準每個來源 skill 的權重——樣本數不到 20 不動、權重被夾在 0.3 到 2.0 之間，不完全關掉一個 skill，也不無限放大它；另一份 `skill_improvement_backlog.yaml` 流向 skill 改進迴圈，樣本數門檻降到 15。這兩份輸出服務的是所有 skill 產生的訊號整體，跟 `trade-memory-loop` 這裡專門對單一已平倉論點做根因判斷，是同一個 skill 底下兩種不必混為一談的用法。

`outcome-classification.md` 還留了兩種容易被含糊帶過的邊界狀況，要求老實記下來，不能省略。出場早於原本設定的持有天數時，報酬要用實際持有天數換算，並標記 `early_exit` 為 `true`，附上 `early_exit_reason`——停損出場、達標出場，或臨場自行決定；股價因隔夜消息跳空開盤時，另外記下 `gap_event` 與 `gap_pct`，不讓跳空造成的落差跟正常走勢的報酬混在一起計算。這兩個欄位存在的理由，跟四選一的根因分類是同一套邏輯：與其把結果硬套進一個乾淨好看的敘事，不如把當時真實發生的條件都留下痕跡。

## 判讀與誤用

`manual_review` 列的三條提醒，說的其實是分類這件事最容易失手的地方。獲利的單子容易讓人把功勞全記在判斷上，卻不去問這筆錢有多少成分靠的是手氣；虧損的單子容易讓人把責任推給市場不配合，卻迴避論點本身可能真有破綻。隨機性作為正式選項，恰好卡在這兩種傾向的中間——它不是拿來幫失誤開脫的萬用理由，也不是拿來否定一次正確判斷的藉口，只在事後怎麼拆解都找不出可歸咎、可修正的地方時才成立。如果每一筆不順眼的結果都往隨機性裡塞，這四選一的分類就失去意義，累積起來餵給 `monthly-performance-review` 或 `weight_feedback.json` 的統計，也只是包了一層數字外衣的猜測。

`when_not_to_run` 還堵死了另一條退路：即使平倉那天是進帳，也不允許因為心情好就把這一輪分類跳過不做。誠實的事後檢討不是只在虧損時才啟動的補救程序，它對每一筆平倉一視同仁——差別不在有沒有 `decision_gate`，`trade-performance-coach` 那一步同樣標成 `true`；差別在於第 2 步 `signal-postmortem` 是必經的，第 3 步 `trade-performance-coach` 是可選的——分類這一關，沒有跳過的餘地。

## 延伸閱讀

- [`skills/signal-postmortem/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/signal-postmortem/SKILL.md)
- [`skills/signal-postmortem/references/outcome-classification.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/signal-postmortem/references/outcome-classification.md)
- [`skills/signal-postmortem/references/feedback-integration.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/signal-postmortem/references/feedback-integration.md)
- [`workflows/trade-memory-loop.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/trade-memory-loop.yaml)
