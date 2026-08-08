# 附錄 C：API 設定指南

## 哪裡需要鑰匙，哪裡不需要

本書五部實作章對付費資料的依賴程度並不一致，一段總覽先把地圖攤開。第一部`market-regime-daily`只有可選的Step 3（`market-top-detector`）碰到`FMP_API_KEY`，免費額度就夠；第二部`swing-opportunity-daily`篩選段裡，Step 2的`vcp-screener`是唯一必跑、也必須有`FMP_API_KEY`的一步，另外三支可選偵查隊多半也靠FMP，兩支Stockbee篩子留了`--prices-json`本地路徑當備援，Step 6的`theme-detector`則完全不吃FMP。2.5節的`cot-contrarian-detector`是全書唯一明確卡在付費層級的一步——COT端點需要FMP Premium+訂閱，免費層拿不到。第三部`swing-opportunity-daily`閘門段六步裡，只有Step 7的技術分析師備援腳本需要FMP，其餘五步完全離線；第四部`trade-memory-loop`三步同樣全部離線可跑，`FMP_API_KEY`只在Step 2的`signal-postmortem`用得上；第五部edge pipeline六個skill的整合欄位多半標`local_calculation`或`not_required`，唯一沾到FMP的`edge-candidate-agent`也只是可選的OHLCV來源，script本身不打任何FMP端點。Alpaca只被`portfolio-manager`一支skill用到，走的是序章提過的週六`core-portfolio-weekly`——本書五部的六個實作章，主線都沒有真的呼叫它。這個依賴程度的差異，`workflows/*.yaml`自己的`api_profile`欄位也標得清楚（附錄B已列全表）：`market-regime-daily`與`trade-memory-loop`都標`no-api-basic`，`swing-opportunity-daily`整條與`shapiro-contrarian`都標`fmp-required`，`core-portfolio-weekly`標`mixed`——`api_profile`看的是整條workflow有沒有必跑步驟碰到FMP，跟前面拆到「哪一步」不是同一個粒度，兩者要對著看，不能只認其中一個。

## FMP：依用量分層的主力資料源

Free tier一天250次呼叫，官方定位是足夠應付偶爾使用；免費層能跑到什麼程度，`dividend-growth-pullback-screener`的FMP-only模式是個具體例子——CLAUDE.md自己標注，受API用量限制，一次篩選建議上限約40檔股票（`--max-candidates 40`）。往上是Starter，每月29.99美元、每日750次呼叫；再往上是Professional，每月79.99美元、每日2,000次呼叫。COT資料是另一條線：`cot-contrarian-detector`讀CFTC期貨部位需要FMP Premium+等級，免費層拿不到，2.5節已經立過這條。Premium+是FMP產品線裡另一個正式名字——上游CLAUDE.md的定價表只列到Free、Starter、Professional三檔，沒有替Premium+標價，實際費率請查官方頁面。

設定優先用環境變數：

```bash
export FMP_API_KEY=your_key_here
```

沒設環境變數時，多數script也接受`--api-key`參數當備援。CLAUDE.md把這套行為定成所有吃FMP的script共用的模式：先查環境變數，沒有才退回`--api-key`，兩者都缺就印出清楚的錯誤訊息而不是靜靜失敗；遇到FMP限流，script也該用指數退避重試，而不是直接中斷整支流程。

## FINVIZ Elite：可選的加速器

FINVIZ Elite在多支screener裡都是`optional`定位。`value-dividend-screener`與`dividend-growth-pullback-screener`都把它標成建議、非必需——CLAUDE.md把這條兩階段篩選路線標成`RECOMMENDED`，比純FMP模式快70–80%；第二部篩選段的`theme-detector`不用它一樣能跑，只是退回FINVIZ Public爬蟲模式，每個產業只看得到前20檔，耗時拉到5–8分鐘。訂閱價格是每月39.50美元，或每年299.50美元（約合每月24.96美元）。

## Alpaca：本書主線用不到的一條線

Paper trading帳戶免費；live trading是免傭金的免費券商帳戶，股票與ETF交易不收手續費。Alpaca只被`portfolio-manager`用到，本書沒有任何一部的實作章走到它——序章提過週六的`core-portfolio-weekly`會用上它，但那條週末節奏不在本書五部的主線裡。想練手，先開paper帳戶，不涉及真實資金。CLAUDE.md列出的環境變數是三個：

```bash
export ALPACA_API_KEY="your_api_key_id"
export ALPACA_SECRET_KEY="your_secret_key"
export ALPACA_PAPER="true"
```

`ALPACA_PAPER`設`true`就是紙上帳戶；除了這三個變數，還得在Claude Code裡另外接上Alpaca MCP Server才能用，細節本附錄不重複。

## 免費路線：一毛不花能走多遠

把上面五部再對一次帳：第一部全程、第三部閘門段、第四部記憶迴圈、第五部研究管線，全部不需要付費訂閱就能跑完——用得到的FMP呼叫都停在免費層（第一部Step 3、第四部Step 2），其餘完全離線。真正卡住免費路線的只有兩處：第二部篩選段Step 2的`vcp-screener`一定要有`FMP_API_KEY`，`canslim-screener`同樣沒有離線路徑；2.5節的COT資料直接卡在Premium+，免費層過不去。兩支Stockbee篩子留了一條退路——`--prices-json`餵自己準備好的本地OHLCV，就能整支繞開FMP，但這不是預設路徑，`--fmp-universe`全市場掃描還是要靠key。換句話說，本書大多數紀律與研究流程零成本就能跑通，唯獨想篩選候選股或做COT逆勢分析，才真的要付費。

## 延伸閱讀

- [`CLAUDE.md`（API Key Management／API Pricing and Access／API Key Setup）](https://github.com/tradermonty/claude-trading-skills/blob/main/CLAUDE.md)
- [FMP 開發者文件與註冊頁](https://site.financialmodelingprep.com/developer/docs)
- [FINVIZ Elite 註冊頁](https://elite.finviz.com/)
- [Alpaca 註冊頁](https://alpaca.markets/)
