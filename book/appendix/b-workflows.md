<!-- generated: true -->
<!-- source: tradermonty/claude-trading-skills@7a5457f -->
# 附錄 B：Workflows 對照表

共 11 條 workflow。本頁由 `scripts/generate_appendix.py` 自動生成，請勿手動編輯。

## Core Portfolio Weekly（`core-portfolio-weekly`）

- 節奏：weekly｜預估 60 分鐘｜難度：beginner｜API profile：mixed
- 何時執行：Once per week, typically on Saturday or Sunday before next week's market open. Reviews long-term holdings, dividend positions, and overall allocation.
- 何時不執行：Do not run as a daily routine. Daily portfolio churn defeats the long-term framing of this workflow.
- 必要 skills：`portfolio-manager`、`trader-memory-core`
- 可選 skills：`kanchi-dividend-review-monitor`、`value-dividend-screener`、`kanchi-dividend-us-tax-accounting`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Fetch holdings snapshot | `portfolio-manager` |  |
| 2 | Review allocation and concentration | `portfolio-manager` | ✅ |
| 3 | Check dividend health (T1-T5 anomaly check)（可選） | `kanchi-dividend-review-monitor` |  |
| 4 | Decide rebalance actions | `portfolio-manager` | ✅ |
| 5 | Journal the weekly review | `trader-memory-core` |  |

## Kanchi Dividend Weekly（`kanchi-dividend-weekly`）

- 節奏：weekly｜預估 60 分鐘｜難度：intermediate｜API profile：mixed
- 何時執行：Weekly, to source and underwrite new US-listed dividend candidates using Kanchi's 5-step method: screen for yield/quality, deep-dive the strongest names, and register a fully-documented candidate thesis before any entry. v1 covers US-listed dividend stocks only.
- 何時不執行：Not for Japanese or other non-US-listed dividend stocks -- this workflow neither covers nor implies support for them in v1. Not a claim that Kanchi-style screening is a profitable strategy; it is a disciplined candidate-sourcing routine, not a signal to buy. Not for maintaining an existing holding -- that is core-portfolio-weekly's job (this workflow is for finding and underwriting NEW candidates). No order is ever placed automatically; every buy is entered manually at the broker.
- 必要 skills：`kanchi-dividend-sop`、`trader-memory-core`
- 可選 skills：`value-dividend-screener`、`dividend-growth-pullback-screener`、`kanchi-dividend-us-tax-accounting`、`kanchi-dividend-review-monitor`
- 前置 workflow：`core-portfolio-weekly`（需要 artifact `holdings_snapshot`）

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Screen for high-yield candidates（可選） | `value-dividend-screener` |  |
| 2 | Screen for dividend-growth pullbacks（可選） | `dividend-growth-pullback-screener` |  |
| 3 | Run the Kanchi 5-step underwriting | `kanchi-dividend-sop` | ✅ |
| 4 | Check US tax and account-location treatment（可選） | `kanchi-dividend-us-tax-accounting` |  |
| 5 | Check existing-holding review triggers（可選） | `kanchi-dividend-review-monitor` |  |
| 6 | Register the candidate thesis | `trader-memory-core` | ✅ |

## Market Regime Daily（`market-regime-daily`）

- 節奏：daily｜預估 15 分鐘｜難度：beginner｜API profile：no-api-basic
- 何時執行：Before considering new swing-trade risk for the day. Run before market open or in the first 30 minutes after.
- 何時不執行：Do not use this output as a standalone buy/sell signal. The exposure_decision is a posture (allow / restrict / cash-priority), not a directive.
- 必要 skills：`market-breadth-analyzer`、`uptrend-analyzer`、`exposure-coach`
- 可選 skills：`market-top-detector`、`macro-regime-detector`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Analyze market breadth | `market-breadth-analyzer` |  |
| 2 | Analyze uptrend participation | `uptrend-analyzer` |  |
| 3 | Check market top risk（可選） | `market-top-detector` |  |
| 4 | Decide exposure posture | `exposure-coach` | ✅ |

## Monthly Performance Review（`monthly-performance-review`）

- 節奏：monthly｜預估 90 分鐘｜難度：intermediate｜API profile：no-api-basic
- 何時執行：First weekend of each month, reviewing the prior month's closed positions, open thesis health, and process improvements. Closes the Plan -> Trade -> Record -> Review -> Improve loop.
- 何時不執行：Do not skip this review even in losing months — that is when it matters most. Do not run weekly; the monthly cadence is intentional to filter noise.
- 必要 skills：`trader-memory-core`、`signal-postmortem`
- 可選 skills：`trade-performance-coach`、`backtest-expert`、`dual-axis-skill-reviewer`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Aggregate the month's trades and theses | `trader-memory-core` |  |
| 2 | Pattern-level postmortem across the month | `signal-postmortem` | ✅ |
| 3 | Coach monthly process, risk, and behavior patterns（可選） | `trade-performance-coach` | ✅ |
| 4 | Re-validate hypotheses via backtest（可選） | `backtest-expert` |  |
| 5 | Review which skills helped or hurt（可選） | `dual-axis-skill-reviewer` |  |
| 6 | Produce decision log and rule changes | `trader-memory-core` | ✅ |

## Multi-Asset Opportunity Daily（`multi-asset-opportunity-daily`）

- 節奏：daily｜預估 45 分鐘｜難度：intermediate｜API profile：mixed
- 何時執行：Only after market-regime-daily has produced a non-restrictive exposure decision. Sweeps macro + themes + news to surface multi-asset ideas (equities, commodities-via-equity-proxies, options expressions) and synthesizes them into ranked hypothesis cards.
- 何時不執行：Do not run when the latest market-regime-daily exposure_decision is cash-priority. Do not treat hypothesis cards as buy/sell signals — they carry manual_review_required and must pass human sign-off before any capital moves. Forex output is research-only; never feed it into a broker.
- 必要 skills：`macro-regime-detector`、`theme-detector`、`trade-hypothesis-ideator`、`position-sizer`、`trader-memory-core`
- 可選 skills：`market-news-analyst`、`market-environment-analysis`、`sector-analyst`、`scenario-analyzer`、`stanley-druckenmiller-investment`
- 前置 workflow：`market-regime-daily`（需要 artifact `exposure_decision`）

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Refresh macro regime context | `macro-regime-detector` |  |
| 2 | Detect hot themes + sector rotation | `theme-detector` |  |
| 3 | Scan news + catalyst landscape（可選） | `market-news-analyst` |  |
| 4 | Synthesize ranked hypothesis cards | `trade-hypothesis-ideator` | ✅ |
| 5 | Apply risk-based sizing to hypothesis cards | `position-sizer` |  |
| 6 | Persist as IDEA / ENTRY_READY entries | `trader-memory-core` | ✅ |

## Shapiro COT Contrarian（`shapiro-contrarian`）

- 節奏：weekly｜預估 60 分鐘｜難度：advanced｜API profile：fmp-required
- 何時執行：Weekly, after the CFTC Commitment of Traders report publishes (Friday ~3:30pm ET, carrying Tuesday's positioning). Screens roughly 65 futures markets for crowded speculative extremes and, only where a news-failure and a weekly price-action reversal both confirm, produces a contract-sized contrarian fade plan.
- 何時不執行：Do not run intraday or more than weekly — COT data updates once a week and the edge is positioning-driven, not intraday. Do not act on a crowding extreme alone; the gate must reach READY_FOR_PLAN (crowding, news failure, and price action all CONFIRMED) before any sizing. Not for equities — COT covers CFTC futures markets only.
- 必要 skills：`cot-contrarian-detector`、`news-reaction-failure-analyzer`、`technical-analyst`、`contrarian-setup-gate`、`futures-position-sizer`、`trader-memory-core`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Screen COT crowding | `cot-contrarian-detector` | ✅ |
| 2 | Check for news-reaction failure | `news-reaction-failure-analyzer` | ✅ |
| 3 | Confirm weekly price-action reversal | `technical-analyst` | ✅ |
| 4 | Synthesize the contrarian setup gate | `contrarian-setup-gate` | ✅ |
| 5 | Size the futures position | `futures-position-sizer` |  |
| 6 | Register the contrarian thesis | `trader-memory-core` | ✅ |

## Stockbee 20% Study Daily（`stockbee-20pct-study-daily`）

- 節奏：daily｜預估 30 分鐘｜難度：advanced｜API profile：mixed
- 何時執行：Run after the US market close, or during historical research backfills, to identify +20%/-20% movers, classify event context, update matured outcomes, and accumulate a model book of explosive market moves.
- 何時不執行：Do not use as a buy/sell signal workflow or automatic execution system. Do not promote new rules from small samples, current-only universes, or events without survivorship-bias and data-quality notes.
- 必要 skills：`stockbee-20pct-study`
- 可選 skills：`trader-memory-core`、`edge-candidate-agent`、`edge-hint-extractor`、`stockbee-episodic-pivot-analyzer`、`theme-detector`、`backtest-expert`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Scan daily +20% and -20% movers | `stockbee-20pct-study` |  |
| 2 | Classify catalyst, chart context, theme cluster, and risk flags | `stockbee-20pct-study` |  |
| 3 | Update matured forward outcomes for prior 20% study records | `stockbee-20pct-study` |  |
| 4 | Summarize cohorts and export edge hints | `stockbee-20pct-study` | ✅ |
| 5 | Log accepted lessons（可選） | `trader-memory-core` | ✅ |

## Stockbee EP Daily（`stockbee-ep-daily`）

- 節奏：daily｜預估 40 分鐘｜難度：advanced｜API profile：mixed
- 何時執行：Run on earnings/news-heavy days after the market-regime workflow allows new risk, or ad hoc when a game-changing catalyst appears. Use this workflow to classify Day 1 Episodic Pivot candidates and decide whether they are actionable today, delayed-EP watchlist names, or PEAD handoff candidates.
- 何時不執行：Do not run as a blind stock screener without catalyst inputs. Do not use it to bypass market-regime gates, chart validation, position sizing, or manual catalyst review.
- 必要 skills：`drawdown-circuit-breaker`、`stockbee-episodic-pivot-analyzer`、`technical-analyst`、`position-sizer`、`trader-memory-core`、`pre-trade-discipline-gate`
- 可選 skills：`earnings-trade-analyzer`、`stockbee-momentum-burst-screener`、`pead-screener`、`theme-detector`、`breakout-trade-planner`
- 前置 workflow：`market-regime-daily`（需要 artifact `exposure_decision`）

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Check account circuit breaker | `drawdown-circuit-breaker` | ✅ |
| 2 | Optional earnings candidate scan（可選） | `earnings-trade-analyzer` |  |
| 3 | Optional momentum confirmation scan（可選） | `stockbee-momentum-burst-screener` |  |
| 4 | Analyze Day 1 Episodic Pivot candidates | `stockbee-episodic-pivot-analyzer` | ✅ |
| 5 | Validate EP chart quality | `technical-analyst` | ✅ |
| 6 | Calculate EP position size | `position-sizer` |  |
| 7 | Build optional EP trade plan（可選） | `breakout-trade-planner` |  |
| 8 | Register EP thesis or watchlist entry | `trader-memory-core` | ✅ |
| 9 | Run EP manual execution discipline gate | `pre-trade-discipline-gate` | ✅ |

## Stockbee Setup Fluency Loop（`stockbee-fluency-loop`）

- 節奏：daily｜預估 20 分鐘｜難度：intermediate｜API profile：no-api-basic
- 何時執行：After stockbee-momentum-burst-screener produces candidate reports, and again after 3/5 trading-day windows have matured. Builds a model book of Stockbee Momentum Burst examples so the trader can improve setup recognition.
- 何時不執行：Do not use as an execution workflow or signal service. Do not change trading rules from tiny samples; require enough matured examples and manual chart review before promoting or filtering a setup tag.
- 必要 skills：`stockbee-setup-fluency-trainer`
- 可選 skills：`trader-memory-core`、`signal-postmortem`、`backtest-expert`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Ingest latest Stockbee momentum burst candidates | `stockbee-setup-fluency-trainer` |  |
| 2 | Update matured 3-day and 5-day outcomes | `stockbee-setup-fluency-trainer` |  |
| 3 | Summarize setup cohorts and rule candidates | `stockbee-setup-fluency-trainer` | ✅ |
| 4 | Log accepted lessons（可選） | `trader-memory-core` | ✅ |

## Swing Opportunity Daily（`swing-opportunity-daily`）

- 節奏：daily｜預估 40 分鐘｜難度：intermediate｜API profile：fmp-required
- 何時執行：Only after market-regime-daily has produced a non-restrictive exposure decision. Identifies swing trade candidates and builds entry plans.
- 何時不執行：Do not run when the latest market-regime-daily exposure_decision is cash-priority or restrictive. Do not use as a standalone screener without the regime gate.
- 必要 skills：`vcp-screener`、`drawdown-circuit-breaker`、`technical-analyst`、`position-sizer`、`trader-memory-core`、`pre-trade-discipline-gate`
- 可選 skills：`stockbee-momentum-burst-screener`、`stockbee-exhaustion-hammer-screener`、`canslim-screener`、`breakout-trade-planner`、`theme-detector`
- 前置 workflow：`market-regime-daily`（需要 artifact `exposure_decision`）

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Check account circuit breaker | `drawdown-circuit-breaker` | ✅ |
| 2 | Run VCP screener | `vcp-screener` |  |
| 3 | Run Stockbee momentum burst screener（可選） | `stockbee-momentum-burst-screener` |  |
| 4 | Run Stockbee exhaustion hammer screener（可選） | `stockbee-exhaustion-hammer-screener` |  |
| 5 | Run CANSLIM screener（可選） | `canslim-screener` |  |
| 6 | Theme detection cross-check（可選） | `theme-detector` |  |
| 7 | Validate setups on weekly chart | `technical-analyst` | ✅ |
| 8 | Calculate position size | `position-sizer` |  |
| 9 | Build entry plan（可選） | `breakout-trade-planner` |  |
| 10 | Register thesis in journal | `trader-memory-core` | ✅ |
| 11 | Run manual execution discipline gate | `pre-trade-discipline-gate` | ✅ |

## Trade Memory Loop（`trade-memory-loop`）

- 節奏：ad-hoc｜預估 30 分鐘｜難度：beginner｜API profile：no-api-basic
- 何時執行：Every time a position is closed (full or partial exit). Records the outcome, generates a postmortem, (optionally) coaches process / risk / execution / behavior patterns, and (optionally) re-validates the original hypothesis via backtest.
- 何時不執行：Do not run before a position is closed — use trader-memory-core directly to update an open thesis instead. Do not skip this loop after a closed trade, even on winners.
- 必要 skills：`trader-memory-core`、`signal-postmortem`
- 可選 skills：`trade-performance-coach`、`backtest-expert`

| # | 步驟 | Skill | 決策閘 |
|---|---|---|---|
| 1 | Record closed trade outcome | `trader-memory-core` |  |
| 2 | Generate postmortem | `signal-postmortem` | ✅ |
| 3 | Coach process, risk, and behavior patterns（可選） | `trade-performance-coach` | ✅ |
| 4 | Re-validate hypothesis via backtest（可選） | `backtest-expert` |  |
| 5 | Append lessons to journal | `trader-memory-core` |  |
