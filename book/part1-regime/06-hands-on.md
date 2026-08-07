# 實作：market-regime-daily

06:31，離交棒給第二部的 07:30 還有一小時。這一章不再拆方法論，只做一件事：把第一部讀過的四個 skill 實際跑一遍，15 分鐘內走完 [`market-regime-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml) 的四個步驟，拿到今天的 `exposure_decision`。這也是全書「實作章」共用的格式——後面每一部收尾都照這個結構走一次。

15 分鐘不是隨口估的數字。這條 workflow 的 YAML 頭部自己宣告了 `cadence: daily`、`estimated_minutes: 15`、`difficulty: beginner`——一天跑一次、新手也能上手，這章的標題預算就是照著這三行寫的。`api_profile` 標成 `no-api-basic`：Step 3 雖然要用到 FMP key，但免費額度就夠，不影響這個整體分類。

## 兩種跑法

**(a) 在 Claude Code 對話中觸發。** 不用記指令，用一句話描述今天想確認的事，Claude 會自己找到對應的 skill：
- 「幫我看今天市場廣度健不健康」→ `market-breadth-analyzer`
- 「上升趨勢的參與度廣不廣」→ `uptrend-analyzer`
- 「頭部是不是近了，要不要減碼」→ `market-top-detector`
- 「現在該把多少資本投入股票部位」→ `exposure-coach`

**(b) 直接執行 script。** 下面 checklist 的四條指令，逐一對照四支 script 的 `--help` 輸出核對過旗標，在 repo 根目錄執行。兩種跑法背後執行的是同一支 script、算出同一份報告——差別只在於觸發的方式：對話式適合臨時起意的一次性提問，指令式適合排進 cron 或每天固定重跑的例行流程。

## 15 分鐘 checklist

第一次跑之前，先建目錄：`mkdir -p reports/`。`market-breadth-analyzer` 與 `market-top-detector` 都不會自動建立 `--output-dir` 指到的資料夾——目錄不存在，寫檔那一步會直接失敗；`uptrend-analyzer` 與 `exposure-coach` 才會自己 `makedirs`。四支 script 混著用，這個差異值得先記住。

**Step 1・廣度**（`decision_gate: false`）
```bash
python3 skills/market-breadth-analyzer/scripts/market_breadth_analyzer.py \
  --detail-url "https://tradermonty.github.io/market-breadth-analysis/market_breadth_data.csv" \
  --summary-url "https://tradermonty.github.io/market-breadth-analysis/market_breadth_summary.csv" \
  --output-dir reports/
```
`--output-dir` 預設是「目前所在目錄」，不是 `reports/`——四支 script 裡唯一一支需要手動補這個旗標。產出：`reports/market_breadth_<timestamp>.json` 與同名 `.md`。

**Step 2・上升趨勢參與度**（`decision_gate: false`）
```bash
python3 skills/uptrend-analyzer/scripts/uptrend_analyzer.py --output-dir reports/
```
不用任何 URL 旗標，`--output-dir` 預設本來就是 `reports/`。產出：`reports/uptrend_analysis_<timestamp>.json` 與 `.md`。

**Step 3・頭部風險（optional）**
```bash
python3 skills/market-top-detector/scripts/market_top_detector.py \
  --api-key $FMP_API_KEY \
  --breadth-50dma [VALUE] --breadth-50dma-date [YYYY-MM-DD] \
  --put-call [VALUE] --put-call-date [YYYY-MM-DD] \
  --output-dir reports/
```
`--breadth-50dma` 與 `--put-call` 是 SKILL.md 標成 `[REQUIRED]` 的兩項，script 本身不會自動抓，要先用 WebSearch 查到當天數字再填進 `[VALUE]`；200DMA 廣度預設自動從 TraderMonty CSV 抓。跳過這步，流程照樣往下走到 Step 4，只是少一份輸入。產出：`reports/market_top_<timestamp>.json` 與 `.md`。

**Step 4・收斂成姿態**（`decision_gate: true`）
```bash
python3 skills/exposure-coach/scripts/calculate_exposure.py \
  --breadth reports/market_breadth_<timestamp>.json \
  --uptrend reports/uptrend_analysis_<timestamp>.json \
  --top-risk reports/market_top_<timestamp>.json \
  --output-dir reports/
```
把前三步實際寫出的檔名代進去；跳過 Step 3 就不傳 `--top-risk`，script 一樣會跑，只是輸出的 `inputs_missing` 多一項。產出：`reports/exposure_posture_<timestamp>.json` 與 `.md`。

## 前置需求

Step 1、2 不需要任何 API key——兩支 script 讀的是公開 CSV，只要連得上 GitHub Pages。Step 3 需要 `FMP_API_KEY`（免費額度即可），而且 `--breadth-50dma`、`--put-call` 一定要靠 WebSearch 手動查、手動填；沒有 key 就無法產出 `top_risk_report`，只能整個 Step 3 跳過，不影響 Step 1、2、4 照跑。Step 4 本身是純計算，不碰任何付費 API，它吃的是前三步留下的 JSON 檔案路徑。`exposure-coach/SKILL.md` 的 Prerequisites 也列了 `FMP_API_KEY`，但那是給 optional 的 `institutional-flow-tracker` 輸入用的——這條每日 workflow 只傳 `--breadth`、`--uptrend`、`--top-risk` 三個路徑，用不到那把 key。

## 產出解讀

四份報告都落在 `reports/`（Step 1 要手動指定，其餘三步預設就是）。最後一份、也是唯一 `decision_gate: true` 的輸出，長相大致如下：

```json
{
  "exposure_ceiling_pct": 70,
  "bias": "GROWTH",
  "participation": "BROAD",
  "recommendation": "NEW_ENTRY_ALLOWED",
  "confidence": "LOW",
  "inputs_provided": ["breadth", "uptrend", "top_risk"],
  "inputs_missing": ["regime", "ftd", "theme", "sector", "institutional"]
}
```
`exposure_ceiling_pct` 是今天願意配置的股票倉位上限；`recommendation` 只有三個值——`NEW_ENTRY_ALLOWED`、`REDUCE_ONLY`、`CASH_PRIORITY`。`confidence` 值得先說破：`exposure_framework.md` 的門檻是「4–5 份輸入才到 MEDIUM，不到 4 份一律 LOW」，而這條每日 workflow 最多只餵三份（breadth、uptrend、top_risk）。也就是說，就算三步全部跑齊，`confidence` 也該預期停在 `LOW`，不要誤以為它有機會到 `MEDIUM` 或 `HIGH`。

同一個 timestamp 底下還會多一份 `.md`——是給人讀的一頁式摘要，開頭就是 Exposure Ceiling 與 Recommendation 兩行，適合直接貼進交易日誌；`calculate_exposure.py` 的 `--json-only` 旗標可以關掉它，只留 JSON，適合排進自動化流程。

## 收尾

`market-regime-daily.yaml` 的 `manual_review` 三條，親手跑完這 15 分鐘之後要再對照一次：這份輸出沒有被當成買賣訊號使用；今天的曝險該減、該維持還是該加，人已經看過、想過；如果 `recommendation` 落在 `REDUCE_ONLY` 或 `CASH_PRIORITY`，第二部的 `swing-opportunity-daily` 今天就先不跑。最後一條不是任何 script 會擋下來的行為——1.5 節已經說清楚，這是寫給人看的紀律，不是程式碼攔得住的東西：跨 workflow 的順序驗證器不查，四個指令跑完之後，沒有任何機制阻止你緊接著跑選股。姿態偏保守時願不願意真的按兵不動，是操作這整條 workflow 的人自己的責任。

這也是全書從第一部就要立的立場：這 15 分鐘給出的是一個可以重跑、可以稽核的姿態，不是一個保證獲利的公式。下一部要問的問題——該做什麼——只有在這裡先誠實回答「今天能不能做」之後，才有資格被問。

## 延伸閱讀

- [`workflows/market-regime-daily.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml)
- [`skills/market-breadth-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-breadth-analyzer/SKILL.md)
- [`skills/uptrend-analyzer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/uptrend-analyzer/SKILL.md)
- [`skills/market-top-detector/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/market-top-detector/SKILL.md)
- [`skills/exposure-coach/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/exposure-coach/SKILL.md)
