# 開場：五大流派的偵查工具

07:35，兩道閘都亮了燈。第一部的姿態閘給出 `allow`（1.5 節）；`swing-opportunity-daily` 接手後，第 1 步的斷路器也回了 `TRADING_ALLOWED`（第三部會細講這兩道閘怎麼運作）。市場准了，帳戶也准了。第一部問過「今天能不能做」，這一刻，輪到第二部問下一個問題：該挑哪一檔？

[`swing-opportunity-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml) 把這個問題切成第 2 到第 6 步，五個步驟，同時攤開。第 2 步 `vcp-screener` 是唯一標成必跑的；第 3、4 步的 `stockbee-momentum-burst-screener`、`stockbee-exhaustion-hammer-screener`，第 5 步的 `canslim-screener`，第 6 步的 `theme-detector`，全部是 `optional`。跳過任何一個，流程照樣往下走，只是第 7 步能驗證的候選少一份來源。這五步不是接力，是同時派出去的五支偵查隊，各自用不同的方法在同一片市場裡找目標。

而 YAML 對這幾步輸出的態度異常一致：不管哪一個 screener 吐出多少候選，`manual_review` 一律定調——這是候選生成，不是訊號。真正的判斷留給第三部的週線驗證閘；這裡只負責把候選攤開。

## 本部地圖

**2.1 Minervini：波動收縮與突破**——對應第 2 步，唯一必跑的偵查隊。VCP（Volatility Contraction Pattern）找的是壓縮到臨界點、隨時可能突破的整理型態。

**2.2 O'Neil：CANSLIM 成長股**——對應第 5 步，可選。`canslim-screener` 找的是基本面與技術面同時發動的成長股。

**2.3 Stockbee：動能三部曲**——對應第 3、4 步，兩個都可選。`stockbee-momentum-burst-screener` 抓動能剛爆發的股票，`stockbee-exhaustion-hammer-screener` 反過來抓衰竭後的反手；一順一逆，是同一套方法論對同一種現象的兩種讀法。

**2.4 Kanchi：存股的紀律**——不在 `swing-opportunity-daily` 裡。它有自己的週末 workflow，[`kanchi-dividend-weekly`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/kanchi-dividend-weekly.yaml)：找的不是波段候選，而是值得長期持有的美股配息標的——五步精查，決策閘 fail-closed。

**2.5 Shapiro：站在人群的對面**——同樣不在 `swing-opportunity-daily` 裡，但分家分得更徹底。[`shapiro-contrarian`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/shapiro-contrarian.yaml) 連資產類別都換了：篩的是約六十五個期貨市場的 COT（Commitment of Traders）投機部位擁擠度，只有在週五 CFTC 報告公布後才跑。從擁擠度篩選、新聞反應驗證、週線反轉確認，到 `contrarian-setup-gate` 整合判定與論點登記，五道決策閘一路自成一局，沒有一步借用 `swing-opportunity-daily` 的任何步驟。Kanchi 至少還在美股裡找標的；Shapiro 連市場都換了。

**2.6 事件驅動衛星**——對應第 6 步，可選。`theme-detector` 做的是主題層面的交叉比對，替前面幾支隊伍的候選再多加一層篩子；它本身不是一支獨立的主力偵查隊，是衛星。

五大流派不是互斥的選單，不必也不該選一個當作正確答案。它們是同一片市場在不同狀態下遞出來的不同武器——緊縮突破、成長動能、爆發或衰竭、長期配息、逆勢做空，各自對應不同的行情、不同的持有期、不同的風險形狀。真正決定該拿哪一支的，是市場現在的樣子，不是偏好。

實作章會把第 2 到第 6 步真的跑一遍，看看今天這五支偵查隊各自帶回了什麼候選。
