# 4.3 教練看的是行為不是損益

## 場景

月初第一個週末，`monthly-performance-review` 走到第 3 步。前兩步已經把上個月的交易收斂成 `monthly_aggregate`，再由 `signal-postmortem` 把整月結果按根因重新掃過一輪，收斂成 `aggregate_postmortem`——序章交代到這裡，鏡頭直接跳去第 5 步的 `dual-axis-skill-reviewer`，中間這一步留了白。這裡要把它補上：第 3 步是 `trade-performance-coach`，同樣是決策閘，同樣可選。

這不是它第一次登場。`trade-memory-loop` 的第 3 步早就是同一個 skill——4.2 已經確認過，第 2 步的 `signal-postmortem` 必經，第 3 步的 `trade-performance-coach` 可選，兩者的 `decision_gate` 都標成 `true`，差別只在跳不跳過。單筆平倉那天可以先放過這一步；月初這個週末，三十天份的 `monthly_aggregate` 與 `aggregate_postmortem` 已經攤在桌上，要不要把它們轉成教練的判斷，就是這一節要回答的問題。

## 方法論

教練的方法論起手式，是把「這筆賺了還是賠了」跟「這筆做得對不對」拆成兩條不相干的軸線。`review-framework.md` 把話說得很直白：一筆嚴守流程卻虧損的交易可以被接受，一筆違規卻剛好賺錢的交易，違規本身仍然是嚴重的流程問題——輸贏本身換不掉這個判斷。

支撐這句話的是一套五軸審查模型：論點品質、流程遵循、風險紀律、執行品質，以及行為模式，五軸各自對應不同輸出，行為模式只是其中一軸，不是教練的全部。這五軸底下還藏著一套比已經在 4.2 定型的那組根因（論點品質／執行／市場環境／隨機性）更細的分類：教練自己的根因清單是 `thesis_quality`、`execution`、`risk_sizing`、`market_environment`、`rule_violation`、`randomness`、`unknown` 七項——`signal-postmortem` 在平倉當天問的是大方向錯在哪，教練接著往下多問一層：風險部位算錯，還是規則本身被打破，兩件事拆開算。

風險紀律這一軸另外配了一張獨立清單：`risk-review-checklist.md` 把單筆風險、整體曝險、週虧損上限、連續虧損、regime 閘門、停損有沒有被動過、加碼減碼、相關性群聚，八項各自定義 `warning`／`critical` 門檻，還明文示範怎麼用字——好的寫法是「實際風險是 1.8R，對照設定上限 1.0R」，不好的寫法是「這筆單子很蠢」。教練核對的是規則有沒有被遵守，不是替輸贏貼道德標籤，這句示範把方法論那頭的抽象原則落到了寫報告的具體筆法上。

行為模式這一軸落地成十個標籤：`fomo_entry`、`revenge_trade`、`premature_exit`、`overconfidence_after_winner`、`stop_moved`、`size_creep`、`unknown_size_discipline`、`hesitation`、`rule_drift`，以及代表「沒查到任何模式」的 `no_pattern_detected`——不是心理診斷，是綁著證據的假設，每一條都要求「可能模式」這種語氣，外加一個反思問題。

跟教練並排的，是另一個純粹算數字的角色。`weekly-performance-digest` 每週把已平倉的論點滾成一份 `weekly_performance_digest`：勝率、期望值、獲利因子、R 倍數、MAE／MFE 平均，全部是描述性統計。它自己的「不該用在哪」寫得很清楚：單筆深度檢討找 `trade-performance-coach`，訊號準確度分類找 `signal-postmortem`，它自己只負責把數字算出來，不做買賣建議也不做流程判斷。教練看行為，週摘要看數字——這正是這一章標題那句話的另一種寫法。

## 機制

輸入端，教練吃的是同一組三類證據，不管出現在哪個工作流裡。`trade-memory-loop` 第 3 步吃 `closed_thesis_record` 加 `postmortem_findings`；`monthly-performance-review` 第 3 步換成月度版本，吃 `monthly_aggregate` 加 `aggregate_postmortem`。`SKILL.md` 自訂的輸入格式裡還留了第三類——`journal`，裝著反思文字（`reflection`）與情緒標記（`emotions`），行為標籤要引的「日誌寫著『不想錯過』」這類證據，就是從這裡取得：論點、事後檢討、日誌，三條線匯進同一份審查。

第 5 步替每個可能的行為模式配上證據與信心程度，才進第 6 步：把發現轉成具體、暫時、綁著時限的操作準則，像「接下來兩筆風險上限 0.5R」「進場前必須先有論點紀錄」這類可觀察、下一筆交易前就能對照檢查的句子。單筆情境的 `decision_question` 問的是下一個交易時段的 `next_session_operating_rules` 該接受、修改、保留，還是只記錄；月度情境問同一組動詞，對象換成下個月的 `next_month_operating_rules`。第 7 步收尾——每一份報告都要有 `human_decision_gate`，四個選項 `accept_rules`／`modify_rules`／`defer`／`journal_only`，預設值是最後一個。

同一個月度流程裡，第 5 步交給 `dual-axis-skill-reviewer`，這一步留給 5.5 整章開展；它的產出 `skill_review_findings` 匯入第 6 步。值得留意的是，第 6 步宣告要 `consumes` 的只有 `aggregate_postmortem`、`hypothesis_revalidation` 與 `skill_review_findings` 三項——教練在第 3 步產出的 `monthly_performance_coach_report`、`monthly_behavior_patterns`、`next_month_operating_rules` 並不在這份清單裡。換句話說，`rule_changes_for_next_month` 要不要真的採納教練那份 `next_month_operating_rules`，YAML 沒有替你接好這條線。

## 判讀與誤用

這些準則寫出來是要被遵守的，不是寫完就收進報告歸檔了事。`human_decision_gate` 的預設值是 `journal_only`——這件事本身就是一個提醒：如果每次都選預設，準則永遠停在「記下來」那一步，沒有人真的照著做。好的準則被要求「可觀察、綁時限」，正是為了逼下一次交易前有一個明確的檢查點，而不是變成一條讀過就忘的自我期許。

刪掉沒用的準則，本身也算一份輸出，不是失敗。月度收斂那一步的提醒不只是把不管用的規則加進清單，同時要求：清單只進不出，準則的數量遲早膨脹到沒有人記得住，遵守率反而更低；該撤的撤，該降級的降級，跟新增規則同樣重要。

還有一種誤用值得提防：把「證據不足」讀成「證據確鑿」。`unknown_size_discipline` 這個標籤本身代表風險紀律查不出來——原始風險數字或風險計畫兩者有一項缺了，不是查出了什麼毛病。教練的指引也講得很清楚：審查品質分數低的時候，不該對行為標籤過度解讀；證據薄弱，該給的是低信心，不是硬湊一個模式出來。

教練的守則裡還寫死一條，不因虧損而說教或羞辱使用者，行為標籤永遠只能用「可能模式」這種語氣，不能替使用者貼上人格標籤。這條守則跟五軸模型只看流程、不看輸贏，其實是同一件事的兩面——教練評的是規則有沒有被遵守，不是這個人值不值得被信任。

## 延伸閱讀

- [`skills/trade-performance-coach/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-performance-coach/SKILL.md)
- [`skills/trade-performance-coach/references/review-framework.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-performance-coach/references/review-framework.md)
- [`skills/trade-performance-coach/references/behavior-tags.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-performance-coach/references/behavior-tags.md)
- [`skills/trade-performance-coach/references/risk-review-checklist.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-performance-coach/references/risk-review-checklist.md)
- [`skills/trade-performance-coach/references/output-contract.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trade-performance-coach/references/output-contract.md)
- [`skills/weekly-performance-digest/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/weekly-performance-digest/SKILL.md)
- [`skills/weekly-performance-digest/references/weekly-digest-metrics.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/weekly-performance-digest/references/weekly-digest-metrics.md)
