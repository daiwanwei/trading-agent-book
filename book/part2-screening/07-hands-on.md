# 實作：swing-opportunity-daily（篩選段）

07:40，第 1 步的斷路器已經回了 `TRADING_ALLOWED`（第三部實作章會細講這一步），`swing-opportunity-daily.yaml` 的第 2 到 6 步正式接手。這一章不再拆方法論——2.1 到 2.6 節已經把五大流派的邏輯講完——這裡只做一件事：把五支偵查隊實際跑一遍，看看今天各自帶回了什麼候選。第 7 步的週線驗證閘、第 8 步以後的部位計算與紀律閘門，屬於第三部的篇幅，本章只負責把候選攤出來，交給下一關。

## 兩種跑法

**(a) 在 Claude Code 對話中觸發。** 不用記指令，一句話描述今天想找的型態，Claude 會自己找到對應的 skill：
- 「幫我篩 S&P 500 裡壓縮到臨界點的 VCP」→ `vcp-screener`
- 「今天有沒有 4% 突破或區間擴張的動能股」→ `stockbee-momentum-burst-screener`
- 「哪些強勢股回檔後出現賣壓耗盡的鎚形反轉」→ `stockbee-exhaustion-hammer-screener`
- 「幫我找基本面加速、動能撐得住的成長股」→ `canslim-screener`
- 「現在市場上哪些主題最熱」→ `theme-detector`

**(b) 直接執行 script。** 下面五條指令，逐一對照五支 script 的 `--help` 輸出核對過旗標，在 repo 根目錄執行。兩種跑法背後是同一支 script、算出同一份報告，差別只在觸發方式。

## 篩選段 checklist

**Step 2・VCP（必跑，`decision_gate: false`）** 這隊在找什麼：S&P 500 裡誰正壓縮到臨界點、隨時可能突破。
```bash
python3 skills/vcp-screener/scripts/screen_vcp.py --output-dir reports/
```
不傳 `--universe` 就是預設先抓齊整個 S&P 500，粗篩排序後截斷到前 100 名候選（`--max-candidates` 預設 100）；`--output-dir` 本來就預設 `reports/`，這裡照慣例寫出來。產出：`reports/vcp_screener_<timestamp>.json` 與同名 `.md`，寫進 `vcp_candidates`。五步裡唯一不是 `optional: true` 的一步，跳過它，第 7 步能驗證的候選清單裡會少掉唯一保證存在的那一份。

**Step 3・Stockbee 動能爆發（optional）** 這隊在找什麼：動能剛炸開、4% 突破或區間擴張的股票。
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --fmp-universe --max-symbols 300 --output-dir reports/
```
產出：`reports/stockbee_momentum_burst_<timestamp>.json` 與 `.md`，寫進 `momentum_burst_candidates`。

**Step 4・Stockbee 衰竭反手（optional）** 這隊在找什麼：強勢股回檔到賣壓耗盡、留下長下影線的反手買點。
```bash
python3 skills/stockbee-exhaustion-hammer-screener/scripts/screen_exhaustion_hammer.py \
  --fmp-universe --max-symbols 300 --market-gate allowed --output-dir reports/
```
`--market-gate` 只接受 `allowed`／`neutral`／`restrictive` 三個值，餵進今天第 1 步斷路器與第一部 exposure 判斷的結論；`restrictive` 時市場分量直接歸零。產出：`reports/stockbee_exhaustion_hammer_<timestamp>.json` 與 `.md`，寫進 `exhaustion_hammer_candidates`。

**Step 5・CANSLIM（optional）** 這隊在找什麼：這波漲勢背後，公司基本面是不是真的在加速成長。
```bash
python3 skills/canslim-screener/scripts/screen_canslim.py --output-dir reports/
```
不傳 `--universe` 就是預設跑 S&P 500 市值前 40 大成分股。產出：`reports/canslim_screener_<timestamp>.json` 與 `.md`，寫進 `canslim_candidates`。

**Step 6・主題偵測交叉比對（optional）** 這隊在找什麼：前面幾支隊伍的候選，是不是都站在同一個正在發熱的主題裡——它本身不是主力偵查隊，是衛星，替其他候選再多加一層確認。
```bash
python3 skills/theme-detector/scripts/theme_detector.py --output-dir reports/
```
不傳任何 API key 也能跑，走 FINVIZ Public 爬蟲模式，只是每個產業只看得到前 20 檔、耗時拉到 5–8 分鐘。產出：`reports/theme_detector_<timestamp>.json` 與 `.md`，寫進 `theme_candidates`。

## 前置需求

Step 2、3、4、5 都需要 `FMP_API_KEY`——VCP 與 CANSLIM 沒有離線路徑，跳過就等於整步不跑；`stockbee-momentum-burst-screener` 與 `stockbee-exhaustion-hammer-screener` 各留了一條 `--prices-json` 離線路徑，餵進本地 OHLCV JSON 就能繞過 FMP，但預設的 `--fmp-universe` 全市場掃描仍然要靠這把 key。Step 6 的 `theme-detector` 是全章唯一不吃 FMP 的一步：FINVIZ Elite（`FINVIZ_API_KEY`）只是 optional 但建議設定的加速選項——沒有它就退回 Public 爬蟲模式，一樣能跑完；FMP 在這裡也只是 optional，只用來補 P/E 估值資料算 Lifecycle 的 Valuation 分量，沒有就退回 yfinance 的 `trailingPE`——換了一個資料源，更新時效跟著不一樣，不是同一份資料的兩種讀法。五支 script 都會自己建立 `--output-dir` 指定的資料夾，不用預先 `mkdir`。

## 產出解讀

五份候選清單長得不完全一樣，但四支股票型偵查隊（VCP、CANSLIM、動能爆發、衰竭反手）共用同一種骨架：`symbol`、一個 0–100 的合成分數、一個換算出來的等級或狀態。以 Step 2 的 `vcp_screener_<timestamp>.json` 為例（`results` 陣列裡的一筆）：
```json
{
  "symbol": "NVDA",
  "composite_score": 87.4,
  "rating": "Strong VCP",
  "execution_state": "Pre-breakout",
  "pattern_type": "Textbook VCP",
  "valid_vcp": true
}
```
`canslim_screener` 用一樣的 `symbol` 與 `composite_score`，但等級欄位叫 `rating`（Exceptional+／Exceptional／Strong 等七級），沒有 `execution_state` 這個概念；兩支 Stockbee 篩子把合成分數欄位改叫 `setup_score`，可買進狀態欄位叫 `state`（`ACTIONABLE_DAY1`／`MANUAL_REVIEW`／`WATCH_ONLY`／`REJECTED` 這類），頂層 JSON 的候選陣列叫 `candidates` 而不是 `results`。Step 6 的 `theme-detector` 結構性地不一樣——它篩的是主題，不是個股：頂層是 `themes.all` 陣列，每一筆是 `name`、`heat`（0–100）、`stage`（Emerging 到 Exhausting 五階段）、`confidence`（Low／Medium／High），底下才帶一份 `representative_stocks` 清單當佐證，不是候選本身。

不管哪一種骨架，`swing-opportunity-daily.yaml` 的 `manual_review` 立場一致：這是候選生成，不是訊號。分數再高、狀態再理想，都只代表這支腳本認為值得往下看；第 7 步的週線人工複核，才是真正決定留下誰的那一關。

## 收尾

候選離開這一章之後，走的是第三部實作章六步裡剩下的五步——第 1 步的斷路器，本章開場就已經回過 `TRADING_ALLOWED`，不用再過一次：第 7 步的圖表決策閘先淘汰週線結構不乾淨的候選，第 8 步算部位大小，第 9 步（optional）產進場計畫，第 10 步登記論點，第 11 步的紀律閘門在下單前做最後一次六項檢查。五支偵查隊在這裡吐出再多候選，沒有一個能跳過這五步直接變成一張券商訂單。

跟前面兩部立的場一樣：這一章給出的是可重跑、可稽核的候選清單，不是選股建議，更不是買進訊號。`vcp_candidates` 是唯一保證存在的那一份，其餘四份跳過也不影響流程——但不管跑了幾份，決定權從來不在分數，在第三部那道人工複核的閘。

## 延伸閱讀

- [`skills/vcp-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/vcp-screener/SKILL.md)
- [`skills/stockbee-momentum-burst-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-momentum-burst-screener/SKILL.md)
- [`skills/stockbee-exhaustion-hammer-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/stockbee-exhaustion-hammer-screener/SKILL.md)
- [`skills/canslim-screener/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/canslim-screener/SKILL.md)
- [`skills/theme-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/theme-detector/SKILL.md)
- [`workflows/swing-opportunity-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml)
