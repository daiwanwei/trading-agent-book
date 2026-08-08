# 開場：研究日

前四部的開場都釘著一個時間點：週一 06:30、07:35 兩道閘、09:25 閘門之前、某個星期三下午平倉的那一刻。研究日沒有這根釘子。組成第五部管線的六個 skill——`edge-candidate-agent`、`edge-hint-extractor`、`edge-concept-synthesizer`、`edge-strategy-designer`、`edge-strategy-reviewer`、`edge-pipeline-orchestrator`——`skills-index.yaml` 裡全部標成 `timeframe: research`，不是 `daily`，也不是 `ad-hoc`；六筆 `workflows` 欄位清一色是空陣列，沒有一條像 `market-regime-daily` 那樣規定它幾點該跑、跑不跑要看今天的 exposure 姿態。開盤鐘管不到它，斷路器也管不到它。

今天要處理的原料不是報價，是第四部留下的東西：一筆一筆平倉後的分類、月底才浮現的規則變更、還沒被驗證過的觀察與異常。研究日要把這些原料變成新的工具，而不是新的部位。

## 本部地圖

**5.1 從觀察到假說**——`edge-candidate-agent` 掃出 `market_summary.json`、`anomalies.json` 與一批 `tickets/`，`edge-hint-extractor` 再從裡頭抽出 `hints.yaml`。這一步只找「哪裡不對勁」，還不承諾任何交易邏輯。

**5.2 從假說到策略草稿**——`edge-concept-synthesizer` 把 tickets 與 hints 合成 `edge_concepts.yaml`；`edge-strategy-designer` 再把抽象概念寫成一份份 `strategy_drafts/*.yaml`。假說第一次有了可以被否掉的具體形狀。

**5.3 審查與否證**——`edge-strategy-reviewer` 給每份草稿判 `PASS`／`REVISE`／`REJECT`。`REVISE` 觸發修正、再送審，最多兩輪（迴圈本身住在 5.4 的 orchestrator）；兩輪後還過不了的不是直接淘汰，是降級成 `research_probe`——留一條線索，不留一個承諾。

**5.4 整條管線自動化**——`edge-pipeline-orchestrator` 把前三節接力串成一輪自動執行，連審查—修正的迴圈都自己跑；只有同時滿足 `PASS`、`export_ready_v1`、可匯出的 `entry_family` 三個條件，才會被寫成 `strategy.yaml` 與 `metadata.json`，並附一份完整的 `pipeline_run_manifest.json` 執行紀錄。

**5.5 Agent 改進自己的 skills**——目標從「找新策略」換成「修舊工具」。`dual-axis-skill-reviewer` 在 `skills-index.yaml` 裡歸在 `category: meta`，跟前四節那批 `strategy-research` 分屬不同抽屜——它評的不是某個 edge 概念站不站得住，是某個 skill 本身寫得好不好。兩條線之間確切怎麼交會，留給後面的章節細看。

實作章會挑一批真實觀察，把六個 skill 接力跑一遍，從第一份 `anomalies.json` 一路走到匯出的 `strategy.yaml`。

第一部問今天能不能做，第二部問做什麼，第三部問做多少，第四部問學到了什麼——四個問題全部發生在同一週的節奏裡，答案隔天就能兌現。第五部的問題不一樣：Agent 要怎麼變得比上週更好？這個問題不必今天有答案，卻是前四部值得日復一日重複下去的原因。五個問題湊在一起，才是這本書真正要畫的那個環。
