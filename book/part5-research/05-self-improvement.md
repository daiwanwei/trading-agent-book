# 5.5 Agent 改進自己的 skills

## 場景

凌晨 05:00，沒有人醒著。macOS 的 launchd 照著 `com.trade-analysis.skill-improvement` 這支排程把 `run_skill_improvement.sh` 叫起來，底下真正幹活的是 `scripts/run_skill_improvement_loop.py`。

它開工後的第一個動作不是評分，是先確認自己有沒有資格動手。第一關是一把以 PID 為憑的鎖檔：另一個實例還活著就直接退出，發現的是死掉的舊 PID 才把鎖清掉重寫。第二關是 git——工作區有變動時，只有 `reports/`、`logs/`、`state/` 底下的檔案算安全，未追蹤的新檔案不管放在哪裡一律擋下；當前分支不是 `main` 就中止；`git pull --ff-only` 拉不動同樣中止，日誌留一句下次再試。三關任一沒過，這一天的改進就不會發生——一個把自己也關在閘門外面的程式。

過了關，它列出 `skills/` 底下所有帶 `SKILL.md` 的目錄，照 `logs/.skill_improvement_state.json` 裡記著的輪替索引往下取一個。今天輪到誰，昨天那一輪就決定了。名單裡有 `vcp-screener`、有 `position-sizer`、有 `drawdown-circuit-breaker`、有 `pre-trade-discipline-gate`——前四部拿來當主角的那些工具，沒有一個享有豁免。

同一組鬧鐘還有兩個。每週六 06:00，另一支排程去挖新點子；每天 07:00，第三支拿挖到的點子生成全新的 skill。這一章講的就是這三個鬧鐘，以及各自被什麼擋住。

## 方法論

`dual-axis-skill-reviewer` 的名字已經把方法論說掉一半：同一份 skill 被兩把尺同時量。

第一把尺是確定性的。`scoring_rubric.md` 把 100 分拆成五類，每一類旁邊都附著為什麼是這個權重：`metadata_use_case` 20 分——frontmatter 寫壞、觸發條件模糊，這個 skill 就會在錯的時機被喚起；`workflow_coverage` 25 分——操作的人需要一條走得完的流程，缺章節等於留歧義；`execution_safety_reproducibility` 25 分——指令範例與路徑衛生決定結果重不重現得出來、安不安全；`supporting_artifacts` 10 分——scripts、references、tests 撐住基本的可維護性，但不該主導計分；`test_health` 20 分——測試會過，對自動化的信任才有依據。

第二把尺交給 LLM，量的正好是第一把量不到的部分。`llm_review_schema.md` 把審查焦點列成四項：驗證 `scripts/*.py` 的邏輯與行為、比對 `SKILL.md` 的說明跟腳本實際做的事有沒有出入、指出缺掉的測試與回歸風險、揪出會讓執行可靠度下降的模糊指示。輸出是一份 JSON，`score` 與 `summary` 之外是一串 findings，每一條都得帶嚴重度、問題陳述與具體修法。兩軸按權重合成最終分數，預設各佔一半。

真正值得停下來的是下一個決定：**要不要動手改，看的不是那個合成分數**。`run_skill_improvement_loop.py` 的門檻常數是 90，而它拿來比的是 auto 軸那一項；取這個數字的那一行旁邊寫著理由——用 auto 分是為了避開 LLM 合併帶進來的偏差。上游 `CLAUDE.md` 講的是同一件事的另一種說法：確定性、不受 LLM 影響，為的是可重現。

這個取捨的形狀跟第三部很像。LLM 軸看得深，卻不穩：同一份 skill 今天 82 分、明天 88 分都不奇怪；而扣下扳機的後果是動程式碼、開 PR。把扳機接在會抖的那一軸上，等於讓一件有後果的事聽命於一個每次都不太一樣的數字。看得深與量得準是兩種能力，該由哪一種決定「動不動手」，取決於誤判的代價落在誰身上。

改完之後還有一道對稱的關卡。腳本重新評一次分，而且這次把測試打開，新的 auto 分必須嚴格高於改之前那個；只要持平或更低，整條分支就地回滾。動手的條件是分數不夠，收手的條件是沒有變好——兩個判準各自獨立，中間沒有「都試到這裡了就先合進去吧」的空間。

## 機制

改進迴圈的一天長這樣。選定 skill 之後先跑一次 auto 評分，順手產出給 LLM 用的提示檔；接著呼叫 `claude -p` 跑 LLM 軸，單次預算卡在 0.50 美元，拿不到合格 JSON 就換一種輸出模式再來，每種模式各試三次。合成之後 auto 分若低於 90，才開一條叫 `skill-improvement/<日期>-<skill 名>` 的分支。

改進提示不是一句「請把這個 skill 變好」。腳本從報告裡取出 `improvement_items`，最多十條逐條列進提示，並要求最小幅度、針對性的修改，不准碰無關的程式碼；`improvement_items` 一條都沒有時直接放棄這一輪，日誌寫的理由是避免無指引的修改。改進本身預算 2.00 美元，逾時 600 秒。

回滾的理由有三種。第一種是前面說的重評分沒進步。第二種叫 code-faithfulness gate，守的是一個很具體的事故：評分器只獎勵 `## Prerequisites` 這個章節「存在」，從不驗證裡面寫了什麼，於是 LLM 大可從別的 skill 抄一段相依套件清單來把分數補齊。程式碼註解直接點名 PR #164——一個既沒 import `pandas`、也不跑在那個 Python 版本上的 skill，被補上了「Python 3.8+ with pandas and requests」。這道閘門因此拿宣告去對照該 skill 真正 import 的模組與 repo 的 `requires-python` 下限，而且只擋這次改進**新引入**的不實宣告，先前就欠著的舊帳不算在這一輪頭上。第三種是 pre-commit：先跑一趟讓它自動修，重新 stage 再跑一趟，還是紅的就回滾。

三關都過才 commit、push，然後 `gh pr create`。留在磁碟上的痕跡有三處：`logs/.skill_improvement_state.json` 記輪替索引與最近 60 筆歷史，`logs/skill_improvement.log` 保留 30 天，`reports/skill-improvement-log/` 底下每天一份以日期命名的摘要。

另一條管線問的是別的問題：這個 repo 還缺什麼。週六早上 `skill-idea-miner` 掃過去七天的 Claude Code session log，先跑五種確定性的訊號偵測——既有 skill 被引用的頻率、失敗的痕跡（非零 exit code、`is_error` 旗標、`Traceback` 這類字串）、重複的工具序列（三個以上工具組成的序列，在同一次 session 裡出現三次以上）、英日兩組自動化請求關鍵字，以及使用者說完話之後五分鐘內沒有任何工具動作的未解請求。訊號整理好才交給 Claude CLI 抽象成點子，而 `idea_extraction_rubric.md` 對這一步下了兩條硬規定：使用者訊息必須抽象化，不得逐字保留；沒有清楚的點子就回 0 個，不必湊數。

點子接著被打三個分數——novelty、feasibility、trading_value 各 0 到 100，合成分數是 `0.3 * novelty + 0.3 * feasibility + 0.4 * trading_value`。trading_value 權重最高的理由 rubric 自己寫了：這個 repo 首要服務的是投資人與交易者。去重用 Jaccard 比對，門檻 0.5，既比對現有 skill 的名稱與描述，也比對 backlog 裡已經躺著的點子。活下來的寫進 `logs/.skill_generation_backlog.yaml`。

每天 07:00 挑一個來做。`select_next_idea()` 先把 `trading_value` 低於 15 的整批剔除，再把 `pending` 排在可重試的前面，同組之內按合成分數由高到低。`design_failed` 與 `pr_failed` 各給一次重試；`review_failed` 沒有重試——那代表內容品質本身有問題，隔一天跑同一個點子不會得到不同結果。選定之後還有一道即時去重：`skills/<name>/SKILL.md` 已經在磁碟上就跳過。

設計交給 `skill-designer`。`build_design_prompt.py` 把點子 JSON、三份參考檔（結構指南、品質清單、SKILL.md 範本）與最多 20 個現有 skill 的清單組成提示，後者是為了防止生出重複的東西。新生的 skill 用同一支評分腳本審，門檻是 70 而不是 90——新生兒的標準比在役工具寬，但最多只給兩輪：第一輪先不跑測試，過了再開測試重評一次；沒過就改一次，第二輪是最後一輪。

還有一道別處沒有的檢查。設計完一次、改進完再一次，`_check_unexpected_changes()` 掃過整個工作區：只有 `skills/<name>/`、`reports/`，加上 `pyproject.toml` 與六份文件頁算合法變動。動到別的地方就停，而且**不回滾**——分支原樣留著，日誌附上怎麼看 diff、怎麼手動清掉的指令。其他失敗都自動打掃現場，只有這一種刻意把現場留給人看。

交易那一側怎麼跟這裡搭上線，答案在 `monthly-performance-review`。第 5 步的 `dual-axis-skill-reviewer`（4.3 點過名，說留給這一章）產出 `skill_review_findings` 匯進第 6 步，第 6 步再吐出那份可選的 `skill_improvement_backlog`。YAML 的 `final_outputs` 給它的描述只有一句：這是一份可選的回饋，收件人是 repo 這一側的改進迴圈，涵蓋的對象包含 skills，也包含 workflows。

## 判讀與誤用

那份 `skill_improvement_backlog`，名字聽起來像改進迴圈的輸入佇列。4.2 引過的 `feedback-integration.md` 把這個印象畫得更實：流程圖上明明白白一條 `skill_improvement_backlog.yaml --> skill improvement loop`，說明文字甚至寫了改進迴圈會讀 backlog 條目、按嚴重度與樣本數排序、替高嚴重度的問題開分支。但 `run_skill_improvement_loop.py` 從頭到尾沒有讀過任何一份 backlog 檔案，它挑 skill 的唯一依據是狀態檔裡那個輪替索引。文件那頭已經承諾，程式碼這頭還沒接上，中間那段路目前得由人自己走過去——這跟序章盤點過的那幾道只有散文撐著的接口是同一個品種，只是這一道剛好落在全書的最後一節。

輪替本身也該看清楚尺度。目前 `skills/` 底下有 71 個 skill，扣掉評分器自己不列入名單，輪替表上是 70 個，一天一個，繞完一圈要七十天。所以「每天都在改進」這句話得放回正確的量級來讀：每天被改進的是一個 skill，不是全部；同一個工具兩次被檢查之間，隔著兩個多月。

分數也不等於品質。auto 軸量的是 metadata、章節齊不齊、指令與路徑衛生、artifact 存不存在、測試過不過——全部是結構性指標。code-faithfulness gate 的存在本身就是最好的證據：一個章節「有沒有」跟裡面「寫得對不對」是兩件事，前者拿得到分，後者得另外補一道守衛才擋得住。90 分的定義是 production-ready 的基線，不是「這個 skill 的判斷值得相信」。

最後一件事，也是全書最後一次遇到同一種分工。兩條管線的終點都是 `gh pr create`，不是 merge。三道閘門擋得住改壞、擋得住亂改、擋得住抄來的樣板，擋不住「改得很漂亮但方向錯了」。斷路器算得出今天准不准做，單子還是人在券商敲；紀律閘門算得出 `GO`，按鈕還是人按；現在評分器算得出 82 分變成 88 分，要不要讓這個改動進 `main`，仍然是人的一次點擊。這套系統從第一章走到最後一章，只交出判斷，從不交出責任。

而這一章的主角也不例外。`skill-idea-miner` 與 `skill-designer` 同樣排在那份 70 個名字的名單上，隨時可能在某個凌晨被自己參與生產的流程重新評分；唯一被除名的是評分器本身——一把不量自己的尺，它要變好，只能走人的那條路。明天凌晨五點，同一支腳本會挑走名單上的某一個；某一天輪到的，可能正好是前面某一章的主角。所以這本書最後該留給讀者的不是 90 這個數字——數字是某一天的快照。該留下的是那個順序：先量，再改，改完重新量，沒有變好就退回去；而最後那一步，永遠留給願意承擔後果的人。

明天早上，它會比今天好一點。而按下那顆按鈕的，還是你。

## 延伸閱讀

- [`CLAUDE.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/CLAUDE.md)
- [`scripts/run_skill_improvement_loop.py`](https://github.com/tradermonty/claude-trading-skills/blob/main/scripts/run_skill_improvement_loop.py)
- [`scripts/run_skill_generation_pipeline.py`](https://github.com/tradermonty/claude-trading-skills/blob/main/scripts/run_skill_generation_pipeline.py)
- [`skills/dual-axis-skill-reviewer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/dual-axis-skill-reviewer/SKILL.md)
- [`skills/dual-axis-skill-reviewer/references/scoring_rubric.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/dual-axis-skill-reviewer/references/scoring_rubric.md)
- [`skills/dual-axis-skill-reviewer/references/llm_review_schema.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/dual-axis-skill-reviewer/references/llm_review_schema.md)
- [`skills/skill-idea-miner/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/skill-idea-miner/SKILL.md)
- [`skills/skill-idea-miner/references/idea_extraction_rubric.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/skill-idea-miner/references/idea_extraction_rubric.md)
- [`skills/skill-designer/SKILL.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/skill-designer/SKILL.md)
- [`skills/skill-designer/references/quality-checklist.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/skill-designer/references/quality-checklist.md)
- [`skills/signal-postmortem/references/feedback-integration.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/signal-postmortem/references/feedback-integration.md)
