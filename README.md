# 一個 AI 交易 Agent 的一週

繁體中文策展書：以「一個 AI 交易 Agent 如何運作」為敘事主軸，導讀
[tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)
的 71 個交易 Claude Skills。

- 線上閱讀：（GitBook URL，Git Sync 設定後補上）
- 書的內容在 `book/`（GitBook root）
- 設計文件：`docs/specs/`；實作計畫：`docs/plans/`

## 附錄重新生成

附錄 A（skills 速查）與 B（workflows 對照）由腳本從上游 repo 自動生成：

```bash
pip install -r requirements-dev.txt
python3 scripts/generate_appendix.py --upstream ~/Projects/wade/math/claude-trading-skills
python3 scripts/check_book.py --upstream ~/Projects/wade/math/claude-trading-skills
```

生成頁開頭有 `<!-- generated: true -->` 標記，請勿手動編輯。

## 進度

| 部分 | 狀態 |
|---|---|
| 序章 + 第一部 | ✅ 已完成 |
| 第三部（風險與紀律） | ✅ 已完成 |
| 第二部（五大流派） | ✅ 已完成 |
| 第四、五部（M4）→ 附錄 C/D（M5） | 🚧 依序進行中 |

## 本書立場

本書與上游專案相同：所有工具輸出是**姿態不是訊號**，不提供投資建議，不自動下單。
