# 5.3 審查與否證

## 場景

5.2 留下的 `strategy_drafts/*.yaml`——那份 `core` 變體的 breakout 樣本，帶著 `stop_loss_pct: 0.07`、`take_profit_rr: 3.0`、`time_stop_days: 20`——輪到 `edge-strategy-reviewer` 接手。跑一次 `review_strategy_drafts.py --drafts-dir reports/edge_strategy_drafts/ --output-dir reports/`，資料夾裡多出一份 `review.yaml`：`summary` 底下是 `total`、`PASS`、`REVISE`、`REJECT`、`export_eligible` 五個計數；底下 `reviews` 陣列逐份草稿列出 `draft_id`、`verdict`、`confidence_score`、`export_eligible`、`findings`、`revision_instructions`。SKILL.md 把這支腳本的位置寫得直接——它是 `edge-strategy-designer` 產出物進匯出管線之前的最後一道品質關卡，Prerequisites 只要求草稿 YAML 檔案，外加 `Python 3.10+` 與 `PyYAML`。想更嚴格一點，還有一個 `--strict-export` 旗標：符合匯出資格的草稿只要背著任何一條 `warn`，判決就從可能的 `PASS` 降成 `REVISE`——多一道自己選擇加開的關卡，只為了守住真正要出管線的那一批。

## 方法論

八項準則各自算分，但判準不是單純加權平均及格。`review_criteria.md` 寫死一條硬規則：C1（Edge Plausibility）或 C2（Overfitting Risk）只要判到 `fail`，不管另外六項分數多高，直接 `REJECT`——這跟第三部斷路器「多條規則同時觸發、回傳最嚴格那個狀態」是同一種脾氣：壞消息不會被好消息平均掉，一票就能否決。`confidence_score` 要跨過 70 分門檻才夠格拿 `PASS`，但門檻不是唯一條件——判準原句是「confidence_score >= 70 and no "fail" findings」，分數再高，只要背著一條 `fail`，照樣過不了關；跌破 35 分則不論其他，直接 `REJECT`；剩下的中間地帶才是 `REVISE`，附一份修正指示，等修完再送審一次。這條「一票否決加雙重條件」的判準，把研究這一端的紀律，套進跟第三部 fail-closed 閘門同一種形狀。

`backtest-expert` 站在更早一步，把同一種懷疑態度寫進核心哲學——目標不是找紙上最賺的策略，是找壞得最少的策略；SKILL.md 給的時間分配是兩成拿來想點子，八成拿來想辦法打破它。`residual-edge-analyzer` 接在 `backtest-expert` 之後，SKILL.md 自己把定位寫成一句話：「Treat this as a falsification gate after backtest-expert, not as trade authorization」——它算出的四種狀態標籤，仍然可能被一個獨立的 `decision_eligibility` 攔下來：就算統計結果好看，只要資料來源、成本基準、樣本量或共線性任一項有未解的警告，判定照樣落回 `REVIEW_REQUIRED`——跟斷路器的 `PARTIAL` 資料品質同一個道理：把「不確定」和「確定沒事」分開處理，前者一律先擋。`strategy-pivot-designer` 則守在迭代迴圈的出口：`backtest-expert` 反覆調參數調到停滯，不代表可以無限調下去——停滯偵測會逼出一次結構性 pivot，不是繼續在同一組參數附近打轉。

## 機制

八項準則的權重分布：C1 Edge Plausibility 20、C2 Overfitting Risk 20、C3 Sample Adequacy 15，C4 Regime Dependency、C5 Exit Calibration、C6 Risk Concentration、C7 Execution Realism 各 10，C8 Invalidation Quality 5，總和 100。嚴重度分三檔：分數 60 以上判 `pass`；30 到 59 判 `warn`；低於 30 判 `fail`。C1 的 `fail` 條件是 thesis 空白或少於 5 個字；不到 10 個字又沒帶 `momentum`、`reversion`、`drift`、`earnings`、`breakout`、`gap`、`volume`、`sentiment` 這類領域字眼，算 generic，判 `warn`。C2 的算法是條件數字遊戲：`conditions` 加 `trend_filter` 總數超過 12 條直接判 `fail`（10 分）；超過 10 條判 `warn`（40 分）；10 條以下才是 `pass`（80 分）；條件裡每出現一個帶小數點的精確門檻——像「RSI > 33.5」而非「RSI > 30」——再扣 10 分，最低扣到 0。C3 用一條公式估年度交易機會：以 252 個交易日為底，條件裡有 sector 篩選就除以 3，regime 不是 Neutral／Unknown／空值再除以 2，再乘以 0.8 的條件數次方、0.85 的 trend_filter 數次方，結果低於 10 判 `fail`（10 分），低於 30 判 `warn`（40 分），30 以上才 `pass`（80 分）。C5 卡出兩條各自能單獨判 `fail`（10 分）的紅線：`stop_loss_pct` 超過 0.15，或 `take_profit_rr` 低於 1.5。C7 認的可匯出家族只有兩個——`pivot_breakout` 與 `gap_up_continuation`——`export_ready_v1` 標 true 但 entry_family 不在這兩者之內，同樣判 `fail`。

`overfitting_checklist.md` 把過擬合的紅旗歸成五類：條件數過多（10 條起是警戒線，12 條以上幾乎必然過擬合）；門檻寫得太精確（小數點門檻像「RSI > 33.5」「volume > 1.73 * avg」，暗示是照歷史資料硬湊出來的，「RSI > 30」「rel_volume >= 1.5」這種整數或半步門檻才算合理）；regime 過窄，只在單一市場狀態下設計卻沒跨 regime 驗證；估計樣本量過低，年度不到 10 次機會就統計上不可靠；出場參數不對稱，停損寬過 15% 暗示進場時機本身有問題，報酬風險比低於 1.5 則需要不切實際的高勝率才能打平。對應的緩解建議同樣列了五條：把條件數砍到只剩必要篩選；改用整數或行為意義明確的門檻（像 RSI 30/70、50 日均線）；跨多個 regime 與時間段驗證；把年度樣本量拉到 30 次以上；停損控制在 10% 以內，目標抓 2:1 以上的報酬風險比。

`backtest-expert` 對樣本內外紀律的要求更硬。走前向分析（walk-forward）分四步：在訓練期（例如第一到三年）最佳化參數，拿到驗證期（第四年）測試，再往前滾動一次，最後比較樣本內與樣本外表現；警訊寫得明白——樣本外表現低於樣本內的一半、需要頻繁重新最佳化、參數在不同期間劇烈變動，三者任一出現都算危險信號。樣本量門檻分三級：絕對底線 30 筆交易，理想值 100 筆，高信心水準要 200 筆以上；測試年期同樣分級，最低 5 年，理想 10 年以上，還要跨過至少一個完整市場週期。SKILL.md 把研發時間比例寫成一句口訣：兩成生成點子，八成拿去打破它。

`residual-edge-analyzer` 拆的是全書最技術的一段，但骨架其實是一個生活化的問題：一檔策略的報酬，有多少只是跟著宣告好的基準（大盤、動能、等權重或使用者自訂因子）一起漲跌，有多少是基準之外自己多出來的部分？`methodology.md` 給的模型是 `r_t = alpha + beta * f_t + epsilon_t`——策略報酬拆成截距 `alpha`、對每個基準的載荷 `beta`，加上殘差 `epsilon`。先扣掉 beta 那部分跟著基準走的報酬，剩下才問：這個 `alpha`（年化後）相對於剩下的殘差波動（同樣年化），比值站不站得住——這是「殘差 edge 比率」，回答的是扣掉大盤這股水流之後，這艘船自己划出去多遠、划得穩不穩。因為報酬本身常帶自相關與變異數不齊一，普通最小平方法算出的標準誤差容易低估風險、讓 t 值看起來比實際更顯著；`methodology.md` 因此堅持用 HAC（Newey-West）調整過的標準誤差，`hac_lags: "auto"` 用 `floor(4 * (n/100)^(2/9))` 這條公式決定要往回看幾期。滾動穩定度的檢查一樣守著 fail-closed 的脾氣：預設至少要 12 個滾動窗才報告，只有 1 個窗的話，正 alpha 比例只會是 0 或 1，這個數字完全不帶資訊量，直接判 `RESIDUAL_FRAGILE`，不會被拿來充當證據。`RESIDUAL_EDGE`、`BASELINE_EXPLAINED`、`RESIDUAL_FRAGILE`、`INSUFFICIENT_EVIDENCE` 這四種狀態標籤是給統計結果貼的診斷標籤，`decision_eligibility` 才是真正決定能不能拿去做決策的閘門，兩者故意分開讀。

往前一步，`strategy-pivot-designer` 接手的是調參調到走不動的時候。四個停滯偵測各自咬著不同數字：`improvement_plateau`（severity high）看最近 K=3 次迭代的 `total_score` 全距是否小於 3；`overfitting_proxy`（medium）要求 Expectancy 維度分數 ≥15、Risk Management 維度分數 ≥15、Robustness 維度分數 <10，且紅旗清單裡出現 `over_optimized` 或 `short_test_period`，至少要跑過 2 輪才有意義；`cost_defeat`（medium）要求期望值 <0.3、獲利因子 <1.3，且滑價已經測試過，同樣至少 2 輪；`tail_risk`（high）只要最大回撤超過 35%，或 Risk Management 維度分數 ≤5，第一輪就能觸發。四個觸發之上還有一張建議表，優先序寫死：分數低於 30、已跑過 3 輪以上、最近三次分數單調不升，判 `abandon`；只要有任一觸發成立，判 `pivot`；否則才是 `continue`。動手設計 pivot 用三種手法——假設反轉（依觸發反著改對應模組，例如 `cost_defeat` 就縮短持有期、換高流動性標的）、原型切換（依 `hypothesis_type`、`mechanism_tag`、`entry_family` 查對照表，跳到結構不同的策略原型）、目標重構（改寫成功的定義，例如把最大化 Sharpe 換成最小化最大回撤）；三者的分數用 `combined = 0.6 * quality_potential + 0.4 * novelty` 算出，且同一個目標原型最多只留一份提案。

## 判讀與誤用

`confidence_score` 跨過 70、又沒背著任何一條 `fail`，判成 `PASS`，說的仍然只是這份草稿通過了審查腳本能檢查到的八個面向，不是這個機制被驗證能賺錢——跟 5.2 讀 `export_ready_v1` 的分寸一樣，`PASS` 是待否證假說闖過的第一關，不是終點。容易被混淆的是兩組相似的分數線：C1 到 C8 每一項各自用 60／30 分界 `pass`／`warn`／`fail`，整份草稿的總分卻用 70／35 分界 `PASS`／`REVISE`／`REJECT`——兩組門檻數字接近卻不是同一把尺，套錯層級容易誤判某份草稿的真實處境。

`residual-edge-analyzer` 在 `skills-index.yaml` 裡標的 `status` 是 `beta`，不是 `production`；同一份分析算出 `RESIDUAL_EDGE` 這麼漂亮的標籤，也該連著這個版本狀態一起讀，不能當成跟 `backtest-expert` 或審查腳本同等成熟的判定。狀態標籤本身也容易被單獨截斷來讀：只看到 `status: RESIDUAL_EDGE` 就以為證據夠了，忽略了旁邊那個獨立算出的 `decision_eligibility`——後者只要碰到資料來源、成本基準、樣本量或共線性任一項未解的警告，照樣落回 `REVIEW_REQUIRED`，兩個欄位必須一起讀才算完整。

停滯偵測的四個觸發也不是同一起跑線：`improvement_plateau`、`tail_risk` 第一輪迭代就能觸發，`overfitting_proxy`、`cost_defeat` 卻要求至少 2 輪歷史——這不是疏漏，是刻意的不對稱：回撤失控這種結構性風險值得立刻喊停，判斷是不是過擬合這種事，沒有足夠的迭代歷史就先不評斷。`--strict-export` 同樣容易被誤讀成整體判準變嚴——它只在一個窄範圍生效：草稿本來就符合匯出資格、又背著至少一條 `warn` 的時候，才會被多降一級，八項準則本身的計分方式完全沒變。

## 延伸閱讀

- [`skills/edge-strategy-reviewer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-reviewer/SKILL.md)
- [`skills/edge-strategy-reviewer/references/review_criteria.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-reviewer/references/review_criteria.md)
- [`skills/edge-strategy-reviewer/references/overfitting_checklist.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/edge-strategy-reviewer/references/overfitting_checklist.md)
- [`skills/backtest-expert/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/backtest-expert/SKILL.md)
- [`skills/backtest-expert/references/methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/backtest-expert/references/methodology.md)
- [`skills/residual-edge-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/residual-edge-analyzer/SKILL.md)
- [`skills/residual-edge-analyzer/references/methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/residual-edge-analyzer/references/methodology.md)
- [`skills/strategy-pivot-designer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/strategy-pivot-designer/SKILL.md)
- [`skills/strategy-pivot-designer/references/stagnation_triggers.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/strategy-pivot-designer/references/stagnation_triggers.md)
- [`skills/strategy-pivot-designer/references/pivot_techniques.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/strategy-pivot-designer/references/pivot_techniques.md)
