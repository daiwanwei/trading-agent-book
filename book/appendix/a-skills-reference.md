<!-- generated: true -->
<!-- source: tradermonty/claude-trading-skills@f452ecb -->
# 附錄 A：Skills 速查表

共 71 個 skills，依分類排列。本頁由 `scripts/generate_appendix.py` 自動生成，請勿手動編輯。

## market-regime

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Breadth Chart Analyst](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/breadth-chart-analyst) | This skill should be used when analyzing market breadth charts, specifically the S&P 500 Breadth Index (200-Day MA based) and the US Stock Market Uptrend Stock Ratio charts. | daily | intermediate | chart_image（必需） |
| [COT Contrarian Detector](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/cot-contrarian-detector) | Detects crowded speculative (large-speculator) positioning in CFTC futures markets using Commitment of Traders data, implementing step 1 of Jason Shapiro's contrarian methodology. | weekly | intermediate | fmp（必需） |
| [Crypto Regime Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/crypto-regime-analyzer) | Quantifies crypto market regime health (0-100 composite, 100 = risk-on) from six components using free keyless public data. | daily | intermediate | coingecko（必需）、binance_funding（建議）、prices_json（可選） |
| [Downtrend Duration Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/downtrend-duration-analyzer) | Analyze historical downtrend durations and generate interactive HTML histograms showing typical correction lengths by sector and market cap. | research | intermediate | — |
| [Exposure Coach](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/exposure-coach) | Generate a one-page Market Posture summary with net exposure ceiling, growth-vs-value bias, participation breadth, and new-entry-allowed vs cash-priority recommendation by integrating signals from breadth, regime, and flow analysis skills. | daily | beginner | — |
| [FTD Detector](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/ftd-detector) | Detects Follow-Through Day (FTD) signals for market bottom confirmation using William O'Neil's methodology. | daily | intermediate | fmp（必需） |
| [IBD Distribution Day Monitor](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/ibd-distribution-day-monitor) | Detect IBD-style Distribution Days for QQQ/SPY (close down at least 0.2% on higher volume), track 25-session expiration and 5% invalidation, count d5/d15/d25 clusters, classify market risk (NORMAL/CAUTION/HIGH/SEVERE), and emit TQQQ/QQQ... | daily | intermediate | fmp（必需） |
| [Macro Regime Detector](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/macro-regime-detector) | Detect structural macro regime transitions (1-2 year horizon) using cross-asset ratio analysis. | weekly | advanced | yfinance_or_csv（建議） |
| [Market Breadth Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/market-breadth-analyzer) | Quantifies market breadth health using TraderMonty's public CSV data. | daily | beginner | public_csv（必需） |
| [Market Environment Analysis](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/market-environment-analysis) | Comprehensive market environment analysis and reporting tool. | daily | intermediate | websearch（必需）、chart_image（可選） |
| [Market News Analyst](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/market-news-analyst) | This skill should be used when analyzing recent market-moving news events and their impact on equity markets and commodities. | daily | intermediate | websearch（必需） |
| [Market Top Detector](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/market-top-detector) | Detects market top probability using O'Neil Distribution Days, Minervini Leading Stock Deterioration, and Monty Defensive Sector Rotation. | daily | intermediate | public_csv（必需） |
| [News Reaction Failure Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/news-reaction-failure-analyzer) | Judges whether a market failed to react to news favorable to a crowded speculative position, implementing step 2 of Jason Shapiro's contrarian methodology with a Monte-Carlo-verified drift-significance verdict test. | event-driven | intermediate | fmp（必需）、websearch（必需） |
| [Sector Analyst](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/sector-analyst) | This skill should be used when analyzing sector rotation patterns and market cycle positioning. | weekly | intermediate | chart_image（必需） |
| [Uptrend Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/uptrend-analyzer) | Analyzes market breadth using Monty's Uptrend Ratio Dashboard data to diagnose the current market environment. | daily | beginner | public_csv（必需） |
| [US Market Bubble Detector](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/us-market-bubble-detector) | Evaluates market bubble risk through quantitative data-driven analysis using the revised Minsky/Kindleberger framework v2.1. | weekly | intermediate | user_input（必需） |

## core-portfolio

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Dividend Growth Pullback Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/dividend-growth-pullback-screener) | Use this skill to find high-quality dividend growth stocks (12%+ annual dividend growth, 1.5%+ yield) that are experiencing temporary pullbacks, identified by RSI oversold conditions (RSI ≤40). | weekly | intermediate | fmp（必需）、finviz（建議） |
| [Kanchi Dividend Review Monitor](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/kanchi-dividend-review-monitor) | Monitor dividend portfolios with Kanchi-style forced-review triggers (T1-T5) and convert anomalies into OK/WARN/REVIEW states without auto-selling. | weekly | beginner | fmp（建議） |
| [Kanchi Dividend SOP](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/kanchi-dividend-sop) | Convert Kanchi-style dividend investing into a repeatable US-stock operating procedure. | weekly | intermediate | fmp（建議） |
| [Kanchi Dividend US Tax Accounting](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/kanchi-dividend-us-tax-accounting) | Provide US dividend tax and account-location workflow for Kanchi-style income portfolios. | event-driven | intermediate | — |
| [Portfolio Manager](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/portfolio-manager) | Comprehensive portfolio analysis using Alpaca MCP Server integration to fetch holdings and positions, then analyze asset allocation, risk metrics, individual stock positions, diversification, and generate rebalancing recommendations. | weekly | intermediate | alpaca（必需） |
| [Value Dividend Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/value-dividend-screener) | Screen US stocks for high-quality dividend opportunities combining value characteristics (P/E ratio under 20, P/B ratio under 2), attractive yields (3% or higher), and consistent growth (dividend/revenue/EPS trending up over 3 years). | weekly | intermediate | fmp（必需）、finviz（建議） |

## swing-opportunity

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Breakout Trade Planner](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/breakout-trade-planner) | Generate Minervini-style breakout trade plans from VCP screener output with worst-case risk calculation, portfolio heat management, and Alpaca-compatible order templates (stop-limit bracket for pre-placement, limit bracket for post-confi... | event-driven | intermediate | — |
| [CANSLIM Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/canslim-screener) | Screen US stocks using William O'Neil's CANSLIM growth stock methodology. | weekly | intermediate | fmp（必需） |
| [Finviz Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/finviz-screener) | Build and open FinViz screener URLs from natural language requests. | event-driven | beginner | finviz（可選） |
| [Stockbee Exhaustion Hammer Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/stockbee-exhaustion-hammer-screener) | Screen US stocks for Stockbee-style selling-exhaustion hammer candidates using quality/liquidity gates, prior momentum, pullback depth, undercut/reclaim, hammer geometry, volume confirmation, market gate, and risk-distance filters. | daily | intermediate | fmp（必需）、prices_json（可選）、profiles_json（可選） |
| [Stockbee Momentum Burst Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/stockbee-momentum-burst-screener) | Screen US stocks for Stockbee-style 3-5 day momentum burst candidates using 4% breakout, dollar breakout, range expansion, volume expansion, setup quality, and risk-distance filters. | daily | intermediate | fmp（必需）、prices_json（可選） |
| [Theme Detector](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/theme-detector) | Detect and analyze trending market themes across sectors. | weekly | intermediate | fmp（可選）、finviz（建議） |
| [VCP Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/vcp-screener) | Screen S&P 500 stocks for Mark Minervini's Volatility Contraction Pattern (VCP). | daily | intermediate | fmp（必需） |

## trade-planning

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Contrarian Setup Gate](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/contrarian-setup-gate) | Offline synthesis gate that combines COT crowding, news-reaction failure, and weekly price-action confirmation into one actionable setup_status via a fail-closed precedence state machine, implementing the decision center of Jason Shapiro's contrarian methodology. | event-driven | intermediate | — |
| [Drawdown Circuit Breaker](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/drawdown-circuit-breaker) | Account-level circuit breaker that reads trader-memory-core state and decides whether new trade risk is allowed today using daily loss limits, losing-streak cooldowns, and weekly/monthly drawdown halts. | daily | beginner | — |
| [Futures Position Sizer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/futures-position-sizer) | Calculate contract-based futures position sizes from a direction, entry, and stop-loss, using a verified 23-market contract-spec table (multiplier, tick size, tick value), implementing step 4 of Jason Shapiro's contrarian pipeline. | event-driven | intermediate | — |
| [Position Sizer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/position-sizer) | Calculate risk-based position sizes for long stock trades. | event-driven | beginner | — |
| [Pre-Trade Discipline Gate](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/pre-trade-discipline-gate) | Offline manual-execution checklist gate that blocks planless, oversized, revenge-risk, market-regime-blocked, or circuit-breaker-blocked entries and journals the result. | event-driven | intermediate | — |
| [Technical Analyst](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/technical-analyst) | This skill should be used when analyzing weekly price charts for stocks, stock indices, cryptocurrencies, or forex pairs. | event-driven | intermediate | chart_image（必需）、fmp（可選） |
| [US Stock Analysis](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/us-stock-analysis) | Comprehensive US stock analysis including fundamental analysis (financial metrics, business quality, valuation), technical analysis (indicators, chart patterns, support/resistance), stock comparisons, and investment report generation. | event-driven | intermediate | user_input（必需） |

## trade-memory

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Signal Postmortem](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/signal-postmortem) | Record and analyze post-trade outcomes for signals generated by edge pipeline and other skills. | event-driven | beginner | — |
| [Stockbee Setup Fluency Trainer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/stockbee-setup-fluency-trainer) | Build a Stockbee-style setup model book from momentum-burst screener candidates, then update 3-day and 5-day forward outcomes with MFE/MAE, stop-hit status, outcome tags, and cohort statistics. | daily | intermediate | prices_json（可選）、fmp（可選） |
| [Trade Hypothesis Ideator](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/trade-hypothesis-ideator) | Generate falsifiable trade strategy hypotheses from market data, trade logs, and journal snippets with ranked hypothesis cards and optional strategy.yaml export. | research | advanced | — |
| [Trade Performance Coach](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/trade-performance-coach) | Review closed trades, partial exits, and monthly aggregates for process adherence, risk discipline, execution quality, and evidence-based trading behavior patterns, then produce next-session operating rules. | event-driven | intermediate | — |
| [Trader Memory Core](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/trader-memory-core) | Track investment theses across their lifecycle — from screening idea to closed position with postmortem. | event-driven | beginner | fmp（可選） |
| [Weekly Performance Digest](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/weekly-performance-digest) | Generate a weekly performance summary from closed trades with win rate, expectancy, and pattern analysis. | weekly | beginner | — |

## strategy-research

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Backtest Expert](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/backtest-expert) | Expert guidance for systematic backtesting of trading strategies. | research | advanced | user_input（必需） |
| [Edge Candidate Agent](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-candidate-agent) | Generate and prioritize US equity long-side edge research tickets from EOD observations, then export pipeline-ready candidate specs for trade-strategy-pipeline Phase I. | research | advanced | fmp（可選） |
| [Edge Concept Synthesizer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-concept-synthesizer) | Abstract detector tickets and hints into reusable edge concepts with thesis, invalidation signals, and strategy playbooks before strategy design/export. | research | advanced | — |
| [Edge Hint Extractor](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-hint-extractor) | Extract edge hints from daily market observations and news reactions, with optional LLM ideation, and output canonical hints.yaml for downstream concept synthesis and auto detection. | research | intermediate | — |
| [Edge Pipeline Orchestrator](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-pipeline-orchestrator) | Orchestrate the full edge research pipeline from candidate detection through strategy design, review, revision, and export. | research | advanced | — |
| [Edge Signal Aggregator](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-signal-aggregator) | Aggregate and rank signals from multiple edge-finding skills (edge-candidate-agent, theme-detector, sector-analyst, institutional-flow-tracker) into a prioritized conviction dashboard with weighted scoring, deduplication, and contradicti... | research | advanced | — |
| [Edge Strategy Designer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-strategy-designer) | Convert abstract edge concepts into strategy draft variants and optional exportable ticket YAMLs for edge-candidate-agent export/validation. | research | advanced | — |
| [Edge Strategy Reviewer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/edge-strategy-reviewer) | Critically review strategy drafts from edge-strategy-designer for edge plausibility, overfitting risk, sample size adequacy, and execution realism. | research | advanced | — |
| [Residual Edge Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/residual-edge-analyzer) | Separate strategy return performance into declared baseline exposure and residual edge using HAC regression, rolling stability, baseline sensitivity, and regime diagnostics. | research | advanced | — |
| [Scenario Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/scenario-analyzer) | Analyze 18-month scenarios from news headlines via scenario-analyst agent with strategy-reviewer second opinion; outputs primary/secondary/tertiary impact analysis and stock picks. | event-driven | advanced | websearch（必需） |
| [Stanley Druckenmiller Investment](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/stanley-druckenmiller-investment) | Druckenmiller Strategy Synthesizer - Integrates 8 upstream skill outputs (Market Breadth, Uptrend Analysis, Market Top, Macro Regime, FTD Detector, VCP Screener, Theme Detector, CANSLIM Screener) into a unified conviction score (0-100),... | weekly | advanced | — |
| [Stockbee 20% Study](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/stockbee-20pct-study) | Build a daily Stockbee-style +20%/-20% mover event study, classify catalysts and setup context, update forward outcomes, and export evidence-backed edge hints without treating movers as buy/sell signals. | daily | advanced | fmp（必需）、prices_json（可選）、news_events_json（可選）、websearch（可選） |
| [Strategy Pivot Designer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/strategy-pivot-designer) | Detect backtest iteration stagnation and generate structurally different strategy pivot proposals when parameter tuning reaches a local optimum. | research | advanced | — |

## advanced-satellite

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Earnings Trade Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/earnings-trade-analyzer) | Analyze recent post-earnings stocks using a 5-factor scoring system (Gap Size, Pre-Earnings Trend, Volume Trend, MA200 Position, MA50 Position). | event-driven | intermediate | fmp（必需） |
| [Institutional Flow Tracker](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/institutional-flow-tracker) | Use this skill to track institutional investor ownership changes and portfolio flows using 13F filings data. | research | intermediate | fmp（必需） |
| [Options Strategy Advisor](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/options-strategy-advisor) | Options trading strategy analysis and simulation tool. | event-driven | advanced | fmp（可選） |
| [Pair Trade Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/pair-trade-screener) | Statistical arbitrage tool for identifying and analyzing pair trading opportunities. | research | advanced | fmp（必需） |
| [Parabolic Short Trade Planner](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/parabolic-short-trade-planner) | Screen US equities for parabolic exhaustion patterns and generate conditional pre-market short plans, then evaluate intraday trigger fires from live 5-min bars. | event-driven | advanced | fmp（必需）、alpaca（可選） |
| [PEAD Screener](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/pead-screener) | Screen post-earnings gap-up stocks for PEAD (Post-Earnings Announcement Drift) patterns. | event-driven | intermediate | fmp（必需） |
| [Stockbee Episodic Pivot Analyzer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/stockbee-episodic-pivot-analyzer) | Analyze Stockbee-style Day 1 Episodic Pivot candidates from earnings, guidance, M&A, FDA, analyst, contract, product, short-squeeze, and story/theme catalysts using catalyst quality, gap/range expansion, volume shock, neglect/revaluation context, liquidity, and EP-day-low risk. | event-driven | advanced | catalyst_events_json（必需）、fmp（可選） |

## meta

| Skill | 摘要 | 節奏 | 難度 | API |
|---|---|---|---|---|
| [Data Quality Checker](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/data-quality-checker) | Validate data quality in market analysis documents and blog articles before publication. | event-driven | beginner | — |
| [Dual Axis Skill Reviewer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/dual-axis-skill-reviewer) | Review skills in any project using a dual-axis method: (1) deterministic code-based checks (structure, scripts, tests, execution safety) and (2) LLM deep review findings. | research | intermediate | — |
| [Earnings Calendar](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/earnings-calendar) | This skill retrieves upcoming earnings announcements for US stocks using the Financial Modeling Prep (FMP) API. | event-driven | beginner | fmp（必需） |
| [Economic Calendar Fetcher](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/economic-calendar-fetcher) | Fetch upcoming economic events and data releases using FMP API. | event-driven | beginner | fmp（必需） |
| [FXMacroData Calendar](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/fxmacrodata-calendar) | Fetch official-source macro release-calendar events using FXMacroData for trade planning and event-risk filters. | event-driven | beginner | fxmacrodata（可選） |
| [Skill Designer](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/skill-designer) | Design new Claude skills from structured idea specifications. | research | intermediate | — |
| [Skill Idea Miner](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/skill-idea-miner) | Mine Claude Code session logs for skill idea candidates. | research | intermediate | — |
| [Skill Integration Tester](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/skill-integration-tester) | Validate multi-skill workflows defined in CLAUDE.md by checking skill existence, inter-skill data contracts (JSON schema compatibility), file naming conventions, and handoff integrity. | research | intermediate | — |
| [Trading Skills Navigator](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/trading-skills-navigator) | Recommend the right workflow, skillset, API profile, and setup path from a natural-language trading goal. | research | beginner | — |
