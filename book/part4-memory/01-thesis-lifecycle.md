# 4.1 論點的生命週期

## 場景

某一天早上，`swing-opportunity-daily` 走到第 10 步。前九步的來龍去脈，序章與第一到三部都交代過——`vcp-screener` 篩出候選、`technical-analyst` 在週線圖上驗證、`position-sizer` 算出股數。這裡要把鏡頭往前挪半步，看清楚「登記論點」這四個字底下實際發生了什麼。

`trader-memory-core` 不是把一段文字寫進某個共用檔案，而是呼叫 `ingest` 子指令，讀進候選的 JSON，交給對應的來源 adapter 轉譯成一份標準化的 thesis_data，再由 `register()` 在 `state/theses/` 底下生出一個全新的 YAML 檔案——這個檔案就是論點的出生證明，帶著自己的 `thesis_id`（`SKILL.md` 舉的例子形如 `th_aapl_div_20260314_a3f1`，把股票代號、論點類型與日期縫進同一個字串）。`register()` 本身是冪等的：靠一組指紋判斷同一筆候選有沒有登記過，同一份輸入重複跑第二次，不會生出第二個論點。不管候選來自哪一支 screener，落地那一刻的狀態只有一種——`IDEA`。

`kanchi-dividend-weekly` 第 6 步走的是完全不同的候選、完全不同的時間尺度，但落地動作一模一樣：`kanchi_candidates` 的判定同樣透過 `ingest` 落成一筆 `IDEA` 論點。差別在於，這裡的來源 adapter 在寫入之前多一道自己的守門——只收 `verdict` 落在 `CLEAN-PASS`、`PASS-CAUTION`、`CONDITIONAL-PASS` 的列，`HOLD-REVIEW`、`STEP1-RECHECK`、`FAIL`，或者根本沒有 `verdict` 欄位，一律跳過，連寫進 `state/theses/` 的資格都沒有。

## 方法論

一筆交易如果只留下一個進場價和一個出場價，能學到的東西很有限。`trader-memory-core` 把每一筆潛在交易當成一個可以被否證的假說來管理：先有想法（`IDEA`），想法要通過驗證才配拿到明確的進出場條件（`ENTRY_READY`），驗證過的想法要等真實成交才算兌現（`ACTIVE`），部位可以分批了結（`PARTIALLY_CLOSED`），直到完全出場、結果落地（`CLOSED`）；任何一站，只要支撐論點的前提垮了，都可以提前判死（`INVALIDATED`）。這六個狀態是 `thesis_lifecycle.md` 定義的完整集合，沒有更多、也沒有更少——不存在一個叫 `TERMINATED` 的獨立狀態；`terminate()` 是一個操作的名字，執行後的落點只會是 `CLOSED` 或 `INVALIDATED` 這兩個既有狀態之一，不是第七種狀態。

狀態機只准往前走。`IDEA → ENTRY_READY` 由 `transition()` 完成，但這個函式只認這一種轉換，`ACTIVE`、`PARTIALLY_CLOSED` 以及任何終態一律擋下。到 `ACTIVE` 只有一條路——`open_position()`，前提是論點正處於 `ENTRY_READY`，還得真的填上 `actual_price` 與 `actual_date`，沒有這兩個實際數字，這個函式就無法完成呼叫。到 `PARTIALLY_CLOSED` 靠 `trim()`：賣掉部分部位，`shares_remaining` 從 `shares` 往下扣；賣光剩下的部位，同一個 `trim()` 會直接把狀態送進 `CLOSED`，不用再多呼叫一次。`close()` 接受 `ACTIVE` 或 `PARTIALLY_CLOSED` 兩種起點，把累積損益結清。這三個狀態各自綁著一組不變量：`ACTIVE` 時 `shares_remaining` 必須等於 `shares`；`PARTIALLY_CLOSED` 時 `shares_remaining` 大於零、小於 `shares`；`CLOSED` 時 `shares_remaining` 等於零——不是註解裡的提醒，是每次存檔都會核對的條件。反過來，`IDEA`、`ENTRY_READY`、`ACTIVE`、`PARTIALLY_CLOSED` 這四個非終態的任何一站，都能因為 `kill_criteria` 被觸發而提前跳進 `INVALIDATED`，不必按順序走完前面每一站。而倒退永遠不被允許：`ACTIVE → IDEA`、`CLOSED → ACTIVE` 都會被擋下，`INVALIDATED` 一旦落定就是終局，不再接受任何轉換。

## 機制

整套系統只有三個指令入口，對應三支腳本：`ingest`（`thesis_ingest.py`）把外部輸出轉成論點；`store`（`thesis_store.py`）處理論點在生命週期裡的每一步操作；`review`（`thesis_review.py`）管到期提醒與事後檢討——它只做兩件事：列出 `next_review_date` 已到期的論點、產出 postmortem 報告。真正推進 `next_review_date` 的是 `store` 的 `mark_reviewed()` 子指令：這個值在登記時就等於 `created_at` 加上 `review_interval_days`，每次呼叫 `mark_reviewed()` 才會往後推進，複核狀態沿著 `OK → WARN → REVIEW` 這道階梯升級。`ingest` 認得七個來源：`kanchi-dividend-sop`、`earnings-trade-analyzer`、`vcp-screener`、`pead-screener`、`canslim-screener`、`edge-candidate-agent`，以及不靠任何 screener、給手動輸入用的 `manual`。每個 adapter 認得自己來源的原始欄位——`earnings-trade-analyzer` 的 `grade` 對到 `origin.screening_grade`、`pead-screener` 的 `stop_price` 對到 `exit.stop_loss`（`thesis_ingest.py` 的 `ingest_pead()` 明白寫著這是一次欄位名修正：真實輸出從沒有過 `stop_loss` 這個鍵，`field_mapping.md` 那一列本身已經落後於程式碼）——但殊途同歸，全部落在同一個 `IDEA` 起點。`manual` adapter 是為了 IBKR、Robinhood 這類允許碎股的券商準備的：只要求 `ticker`、`thesis_statement`、`thesis_type` 三個必填欄位，`entry_price`、`entry_date`、`shares` 先原樣存進 `origin.raw_provenance`，真正權威的進場價、日期與股數要等後面呼叫 `open-position` 才會寫進正式欄位——像每一個 adapter 一樣，`manual` ingest 永遠只生出 `IDEA`，不會替你把狀態往前推。`edge-candidate-agent` 的 adapter 還帶著 Phase 1 的限制：只收 `research_only=False` 且對應單一 `ticker`/`symbol` 的 ticket，`MARKET_BASKET` 或標成 `research_only` 的 ticket 會被跳過並留下警告——目前的論點記憶只認單一標的。

進場之後，`attach-position` 把 `position-sizer` 算出的 `final_recommended_shares`、`final_position_value`、`final_risk_dollars`、`final_risk_pct` 寫進 `position.shares`（連帶把 `shares_remaining` 設成同一個數字）、`position_value`、`risk_dollars`、`risk_pct_of_account`，但只收 `mode` 是 `shares` 的報告，budget 模式一律拒收；這個操作在 `IDEA`、`ENTRY_READY`、`ACTIVE` 都能跑，一旦論點進了 `PARTIALLY_CLOSED`、`CLOSED` 或 `INVALIDATED` 就會被擋下——再讓它覆寫，等於把已經賣掉幾筆的分批紀錄整個抹掉。`trim` 每執行一次，就在 `status_history` 追加一筆帳：賣了多少股（`shares_sold`）、什麼價位（`price`）、收回多少現金（`proceeds`，四捨五入到分）、這一筆的已實現損益（`realized_pnl`）。`outcome.pnl_dollars` 是所有這些 `realized_pnl` 的總和，`outcome.pnl_pct` 用進場價乘上原始股數當分母去除。事後檢討要用到的 `outcome.mae_pct`、`outcome.mfe_pct`（最大逆向與順向偏移）並非每次都有——只有設定了 FMP API key，`postmortem` 才會去抓歷史報價補上這兩個數字，沒有 key，這一欄就留白，`SKILL.md` 白紙黑字寫著它是選配。

期貨論點走的是另一套分派邏輯，但入口指令不變。只要 `position.asset_type` 等於 `futures`（或 `quantity_unit` 等於 `contracts`），`open-position`、`trim`、`close`、`terminate` 四個指令都會自動改用整數口數的 `quantity`/`quantity_remaining`，而不是可以帶小數的 `shares`/`shares_remaining`，損益公式也換成（出場價−進場價）× `multiplier` × 口數 × 方向號（多單 +1、空單 −1），而且只認美元計價的合約——非美元的 `contract_spec.currency` 會被直接拒絕，系統裡沒有匯率換算這一步。`attach-futures-position` 的重新綁定守門比股票版更嚴：只准在 `IDEA` 或 `ENTRY_READY` 執行，連 `ACTIVE` 都不放行，因為在 `ACTIVE` 狀態下重新綁定會整個蓋掉既有的部位物件，連 `direction` 一起覆寫，等於讓後面每一筆損益計算的正負號都翻過來。

還有一個不受狀態限制的例外——`link_report()`。不管論點正在 `IDEA` 還是已經 `CLOSED`，都能呼叫這個函式把一份補充報告掛進 `linked_reports`；記錄的完整性不因為狀態已經定案就被鎖死，事後補上一份遲來的分析，永遠有地方可以放。

## 判讀與誤用

「不到真實成交不進 `ACTIVE`」，序章與 2.4 節都已經從決策閘的角度講過一次；這裡要補的是它在程式碼層的另一半——這條規則不是靠人自律遵守的軟性提醒，而是寫死在函式簽章裡的硬性前提。`open_position()` 要求傳入 `actual_price` 與 `actual_date`，而且只接受正處於 `ENTRY_READY` 的論點；沒有這兩個實際數字，這個函式就無法完成呼叫，狀態停在原地。反過來，一旦真的進了 `ACTIVE`，狀態機也不再退讓——`ACTIVE → IDEA` 或 `CLOSED → ACTIVE` 這類回頭路一律被擋，論點只能往前走，不能靠改欄位悄悄退回「還沒發生」的狀態。這兩道限制合起來，才是「真實成交」四個字真正的重量：進不去靠前提檢查，退不回靠方向限制。

論點記錄不是寫給這一刻看的。4.2 的事後檢討要讀 `status_history` 與 `outcome`，4.3 的教練要讀整批論點的行為模式，4.4 的模型書要讀進出場當時記下的證據——這些下游全部假設上游的紀錄是誠實的。一筆晚了幾天才補寫的 `IDEA`、一份沒有掛上去的分析檔案、一次為了讓數字好看而多算的 `shares_remaining`，不會讓這一筆交易本身變好或變壞，但會讓後面所有從這批資料算出來的統計都失真——樣本本身壞了，建立在樣本之上的判斷就靠不住。這正是為什麼登記論點被放在第四部的第一節：它不是行政作業，是後面三節賴以成立的地基。

## 延伸閱讀

- [`skills/trader-memory-core/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trader-memory-core/SKILL.md)
- [`skills/trader-memory-core/references/thesis_lifecycle.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trader-memory-core/references/thesis_lifecycle.md)
- [`skills/trader-memory-core/references/field_mapping.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trader-memory-core/references/field_mapping.md)
- [`skills/trader-memory-core/assets/postmortem_template.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/trader-memory-core/assets/postmortem_template.md)
