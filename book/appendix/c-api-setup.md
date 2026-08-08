# 附錄 C：API 設定指南

## 哪裡需要鑰匙，哪裡不需要

本書五部實作章對付費資料的依賴程度並不一致，一段總覽先把地圖攤開。第一部 `market-regime-daily` 只有可選的 Step 3（`market-top-detector`）碰到 `FMP_API_KEY`，免費額度就夠；第二部 `swing-opportunity-daily` 篩選段裡，Step 2 的 `vcp-screener` 是唯一必跑、也必須有 `FMP_API_KEY` 的一步，另外三支可選偵查隊多半也靠 FMP，兩支 Stockbee 篩子留了 `--prices-json` 本地路徑當備援，Step 6 的 `theme-detector` 不需要 FMP（FMP 只是選配的 P/E 估值補強）。2.5 節的 `cot-contrarian-detector` 是全書唯一明確卡在付費層級的一步——COT 端點需要 FMP Premium+ 訂閱，免費層拿不到。第三部 `swing-opportunity-daily` 閘門段六步裡，只有 Step 7 的技術分析師備援腳本需要 FMP，其餘五步完全離線；第四部 `trade-memory-loop` 三步同樣全部離線可跑，`FMP_API_KEY` 只在 Step 2 的 `signal-postmortem` 用得上；第五部 edge pipeline 六個 skill 的整合欄位多半標 `local_calculation` 或 `not_required`，唯一沾到 FMP 的 `edge-candidate-agent` 也只是可選的 OHLCV 來源，script 本身不打任何 FMP 端點。Alpaca 只被 `portfolio-manager` 一支 skill 用到，走的是序章提過的週六 `core-portfolio-weekly`——本書五部的六個實作章，主線都沒有真的呼叫它。這個依賴程度的差異，`workflows/*.yaml` 自己的 `api_profile` 欄位也標得清楚（附錄 B 已列全表）：`market-regime-daily` 與 `trade-memory-loop` 都標 `no-api-basic`，`swing-opportunity-daily` 整條與 `shapiro-contrarian` 都標 `fmp-required`，`core-portfolio-weekly` 標 `mixed`——`api_profile` 看的是整條 workflow 有沒有必跑步驟碰到 FMP，跟前面拆到「哪一步」不是同一個粒度，兩者要對著看，不能只認其中一個。

## FMP：依用量分層的主力資料源

Free tier 一天 250 次呼叫，官方定位是足夠應付偶爾使用；免費層能跑到什麼程度，`dividend-growth-pullback-screener` 的 FMP-only 模式是個具體例子——CLAUDE.md 自己標注，受 API 用量限制，一次篩選建議上限約 40 檔股票（`--max-candidates 40`）。往上是 Starter，每月 29.99 美元、每日 750 次呼叫；再往上是 Professional，每月 79.99 美元、每日 2,000 次呼叫。COT 資料是另一條線：`cot-contrarian-detector` 讀 CFTC 期貨部位需要 FMP Premium+ 等級，免費層拿不到，2.5 節已經立過這條。Premium+ 是 FMP 產品線裡另一個正式名字——上游 CLAUDE.md 的定價表只列到 Free、Starter、Professional 三檔，沒有替 Premium+ 標價，實際費率請查官方頁面。

設定優先用環境變數：

```bash
export FMP_API_KEY=your_key_here
```

沒設環境變數時，多數 script 也接受 `--api-key` 參數當備援。CLAUDE.md 把這套行為定成所有吃 FMP 的 script 共用的模式：先查環境變數，沒有才退回 `--api-key`，兩者都缺就印出清楚的錯誤訊息而不是靜靜失敗；遇到 FMP 限流，script 也該用指數退避重試，而不是直接中斷整支流程。

## FINVIZ Elite：可選的加速器

FINVIZ Elite 在多支 screener 裡都是 `optional` 定位。`value-dividend-screener` 與 `dividend-growth-pullback-screener` 都把它標成建議、非必需——CLAUDE.md 把這條兩階段篩選路線標成 `RECOMMENDED`，比純 FMP 模式快 70–80%；第二部篩選段的 `theme-detector` 不用它一樣能跑，只是退回 FINVIZ Public 爬蟲模式，每個產業只看得到前 20 檔，耗時拉到 5–8 分鐘。訂閱價格是每月 39.50 美元，或每年 299.50 美元（約合每月 24.96 美元）。

## Alpaca：本書主線用不到的一條線

Paper trading 帳戶免費；live trading 是免傭金的免費券商帳戶，股票與 ETF 交易不收手續費。Alpaca 只被 `portfolio-manager` 用到，本書沒有任何一部的實作章走到它——序章提過週六的 `core-portfolio-weekly` 會用上它，但那條週末節奏不在本書五部的主線裡。想練手，先開 paper 帳戶，不涉及真實資金。CLAUDE.md 列出的環境變數是三個：

```bash
export ALPACA_API_KEY="your_api_key_id"
export ALPACA_SECRET_KEY="your_secret_key"
export ALPACA_PAPER="true"
```

`ALPACA_PAPER` 設 `true` 就是紙上帳戶；除了這三個變數，還得在 Claude Code 裡另外接上 Alpaca MCP Server 才能用，細節本附錄不重複。

## 免費路線：一毛不花能走多遠

把上面五部再對一次帳：第一部全程、第三部閘門段、第四部記憶迴圈、第五部研究管線，全部不需要付費訂閱就能跑完——用得到的 FMP 呼叫都停在免費層（第一部 Step 3、第四部 Step 2），其餘完全離線。真正卡住免費路線的只有兩處：第二部篩選段 Step 2 的 `vcp-screener` 一定要有 `FMP_API_KEY`，`canslim-screener` 同樣沒有離線路徑；2.5 節的 COT 資料直接卡在 Premium+，免費層過不去。兩支 Stockbee 篩子留了一條退路——`--prices-json` 餵自己準備好的本地 OHLCV，就能整支繞開 FMP，但這不是預設路徑，`--fmp-universe` 全市場掃描還是要靠 key。換句話說，本書大多數紀律與研究流程零成本就能跑通，唯獨想篩選候選股或做 COT 逆勢分析，才真的要付費。

## 延伸閱讀

- [`CLAUDE.md`（API Key Management／API Pricing and Access／API Key Setup）](https://github.com/tradermonty/claude-trading-skills/blob/main/CLAUDE.md)
- [FMP 開發者文件與註冊頁](https://site.financialmodelingprep.com/developer/docs)
- [FINVIZ Elite 註冊頁](https://elite.finviz.com/)
- [Alpaca 註冊頁](https://alpaca.markets/)
