# 1.3 底部的確認訊號：FTD

## 場景

修正已經持續好幾週，`market-regime-daily` 每天照樣把四步跑完，這陣子 `exposure_decision` 多半落在 `restrict` 或 `cash-priority`。但這條 workflow 本身不負責回答「底部到了沒有」——它問的是「今天能不能冒新的風險」，兩個問題不一樣。

於是在這四步之外，Agent 另外每天做一件事：檢查 QQQ 與 S&P 500 有沒有出現 Follow-Through Day（FTD）。這不是 `market-regime-daily` 的第五步——`skills-index.yaml` 裡 `ftd-detector` 的 `workflows` 欄位是空的，它沒有被排進任何一條 workflow。它是修正之後、regime 檢查之外，Agent 主動加開的一項背景監控，目的只有一個：判斷眼前這波反彈，是不是那種夠格被機構認可的反彈。

## 方法論

FTD 是 O'Neil 在《How to Make Money in Stocks》裡定義的訊號，`ftd_methodology.md` 開宗明義把它稱為「最重要的單一訊號」：根據 IBD 的歷史分析，沒有一次新的牛市或可持續的漲勢，是在沒有 FTD 的情況下開始的。

判定分四步，天數與門檻都寫死。第一步先確認有沒有夠格的修正：指數收盤跌幅至少 3%，且下跌期間至少有 3 個下跌日；S&P 500 或那斯達克任一達標即可。修正裡收盤價最低的那一天是 swing low——注意是收盤價，不是盤中低點——它必須是局部低點（前後交易日收盤都比它高），而且往前 40 個交易日內能找到那波至少 3% 的下跌與 3 個下跌日。

第二步是 rally attempt 的 Day 1：swing low 之後第一個「上漲日」——收盤高於前一日收盤；或用替代條件，收盤落在當日振幅的前 50%（`(收盤 - 最低) / (最高 - 最低) ≥ 0.50`），即使沒收在昨收之上，只要盤中大幅收復也算數。Day 2、Day 3 不必是上漲日，但收盤絕不能跌破 Day 1 的盤中低點——這條規則很嚴，破了就整個 rally attempt 作廢，回頭找新的 swing low 重新計日。

第三步是 FTD 窗口，Day 4 到 Day 10。Day 4–7 是「prime window」，歷史上成功率較高；Day 8–10 仍然算數，但統計上偏弱；過了 Day 10 沒等到 FTD，這一波 rally 就不再是傳統意義的 FTD，即使後來真的走成一波漲勢，可信度也明顯打折。真正的 FTD 必須同時滿足兩個條件：漲幅至少 1.25%（1.25–1.49% 是最低門檻，1.50–1.99% 是建議門檻、可信度較高，2.00% 以上算強訊號），而且成交量要高於前一日——這一條是硬性的，沒有量增，漲幅再大也不算 FTD。2022 年 10 月是個乾淨的例子：swing low 落在 10 月 13 日，Day 1 是 10 月 14 日（+2.6%），FTD 出現在 Day 6（10 月 21 日，+2.4%，放量），屬於 prime window，後來被視為確認了那一輪熊市的結束。

「不確認就不加碼」聽起來像膽小，實際上是在等一個特定的證據。Day 1 到 Day 3 的漲勢誰都看得到，但看得到的漲勢不等於機構在買——`ftd_methodology.md` 把「在 FTD 確認之前搶進」列為最常見的錯誤，緊接著第二常見的錯誤是「忽略成交量」：只看漲幅、不看量增，會把還沒有機構承接的反彈誤判成底部確認。等到 Day 4 之後才動作，付出的代價是少賺開頭那幾天，換到的是一個可以被證偽的判準。

## 機制

Agent 執行 `ftd-detector` skill，靠 `rally_tracker.py` 裡的 `track_rally_attempt()` 與 `detect_ftd()` 把上面的規則寫成一個狀態機：`NO_SIGNAL → CORRECTION → RALLY_ATTEMPT → FTD_WINDOW → FTD_CONFIRMED`，另外兩條失敗分支——`RALLY_FAILED`（跌破 swing low，或 Day 2、Day 3 收盤跌破 Day 1 低點）、`FTD_INVALIDATED`（收盤跌破 FTD 當日低點）。`get_market_state()` 對 S&P 500 與 QQQ 各跑一次這套狀態機，再合成一個 `combined_state`——單一指數出現 FTD 就足以觸發訊號，兩個指數在幾天內先後確認，質量分數會額外加 15 分，代表更廣的機構認可。

資料面，`ftd_detector.py` 呼叫 FMP API 抓 S&P 500（`^GSPC`）與 QQQ 各 60 天以上的歷史 K 線，再各抓一次即時報價，合計四次呼叫，遠低於免費額度每日 250 次的上限。質量分數（0–100 分）按權重表合成：Day 4–7 底分 60、Day 8–10 底分 50；漲幅達 2.0%／1.5%／1.25% 三個級距分別加 15／10／5 分；成交量高於 50 日均量再加 10 分；雙指數同時確認加 15 分；再依 `post_ftd_monitor.py` 算出的 FTD 後續體質做加減。80 分以上是「Strong FTD」，建議倉位 75–100%；60–79 分「Moderate」，50–75%；40–59 分「Weak」，25–50%；40 分以下視同沒有 FTD 或已失敗，建議倉位壓到 0–25%。整套分析輸出成 `ftd_signal_report`——這是 `skills-index.yaml` 登記的正式產出，附帶 JSON 與 Markdown 兩份報告檔。

FTD 確認之後，監控沒有結束。`post_ftd_guide.md` 把接下來 5 個交易日訂為觀察窗：`count_post_ftd_distribution()` 追蹤這段期間有沒有出現派發日（跌幅至少 0.2%、成交量高於前一日）；`check_ftd_invalidation()` 檢查有沒有收盤跌破 FTD 當日低點——這是一條硬停損，一旦觸發就判定 FTD 失效，不嘗試攤平或硬撐，而是等新的 swing low 重新開始；`detect_power_trend()` 則檢查三個條件是否同時成立——21 日 EMA 高於 50 日 SMA、50 日 SMA 近 5 個交易日斜率為正、股價站上 21 日 EMA——三個全滿足才算 Power Trend，通常在成功的 FTD 之後 2 到 4 週才會發展出來，代表最高信心的確認。

## 判讀與誤用

`post_ftd_guide.md` 不迴避這件事：FTD 是必要條件，不是充分條件。約 75% 的 FTD 最終會失敗，真正走成可持續漲勢的大約只有 25%。質量分數的用途正是把這個失敗率篩薄——分數 80 分以上的 FTD，成功率約 45–50%；60–79 分約 30–35%；60 分以下只剩 10–15%。就算篩到最高分那一級，也還是低於五成的勝率；之所以整體期望值仍然為正，是因為配合停損管理之後，贏的部位賺得比輸的部位賠得多。

派發日出現的時間點也有自己的失敗率：FTD 後第 1 天出現派發日，約 85% 會失敗，建議立刻降倉；第 2 天約 80%，降到防禦水位；第 3 天約 65%，明顯收緊停損；第 4 天約 50%，中度謹慎；第 5 天約 45%，正常監控；如果前 5 天完全沒有派發日，失敗率降到約 35%，可以提高信心。這張表本身就是「FTD 不是全清訊號」的證據——確認之後的頭幾天，比確認那一天更容易看出訊號是不是假的。

也因為這樣，曝險模型是漸進式的，不是一次到位：FTD 當天只建議動用目標曝險的 25%，挑 1–2 檔從標準底部突破的領先股先試單，並以 FTD 當日低點當初始停損參考；前 5 天沒有派發日，才加到 50%，加碼其他領先股，並把原有部位的停損拉到損益兩平；趨勢確認、突破持續有效，才加到 75%；要等 Power Trend 真正成形（通常是 FTD 後 2–4 週），才會給到 100%。換句話說，FTD 給的許可是「允許開始試探」，不是「全倉進場」——就算是最高分的 Strong FTD，第一天能動用的也只有四分之一的目標倉位。

FTD 訊號與 1.5 節的 `exposure_decision` 之間，目前沒有被接成同一條管線——`ftd-detector` 在 `skills-index.yaml` 裡的 `workflows` 欄位是空的，它的判斷不會自動餵進 `exposure-coach`。姿態的最終決定權，仍然在每天早上 `market-regime-daily` 第四步跑出來的那句 `allow` / `restrict` / `cash-priority`；FTD 只是 Agent 自己額外準備的一份背景判讀。`post_ftd_guide.md` 在與 Market Top Detector 的互動說明裡寫了同一種分工：FTD 已確認，但頂部風險分數依然偏高，建議用更小的部位謹慎進場，而不是照質量分數的建議全額加碼。放在跟 exposure-coach 的關係上同樣成立——FTD 說「可以開始試探」，如果今天的姿態是 `restrict` 或 `cash-priority`，試探的空間本身就先被壓縮了。

## 延伸閱讀

- [`skills/ftd-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/ftd-detector/SKILL.md)
- [`skills/ftd-detector/references/ftd_methodology.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/ftd-detector/references/ftd_methodology.md)
- [`skills/ftd-detector/references/post_ftd_guide.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/ftd-detector/references/post_ftd_guide.md)
