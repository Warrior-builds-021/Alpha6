# PLAN — ALPHA6 FinTech Transformation

## Objective
Transform ALPHA6 into an app-grade quantitative investing and financial analysis platform inspired by Investo.in's modern UI/UX, powered by 6-Pillar institutional discipline, real-time technical terminal, and automated capital preservation.

## Phase 0: Survey & Discovery (Current)
- Dispatch 3 parallel Explorers:
  - Explorer 1: Frontend & UI/UX architecture, styling, components, Investo.in design tokens, chart terminal, autocomplete.
  - Explorer 2: Backend quantitative engine, 6 pillars, Piotroski F-Score, Altman Z-Score, position sizing, yfinance caching.
  - Explorer 3: Existing codebase inventory, dependencies, server harness, testing infrastructure, build/run scripts.
- Aggregate reports into PROJECT.md § Feature Inventory & Architecture.

## Phase 1: Dual-Track Architecture & Decomposition
- Track A: E2E Testing Orchestrator (Opaque-box test suite: Tiers 1-4, 10-suite regression, test runner, TEST_READY.md).
- Track B: Implementation Track (Decomposed across 3-5 modular milestones):
  - M1: Backend Engine & High-Performance Data Layer (6 pillars, Piotroski, Altman, ATR sizing, TTL caching, yfinance serverless cache).
  - M2: API Endpoints & Fast Search Autocomplete (FastAPI/Flask/etc. routes, JSON validation, sub-10ms NSE/BSE search).
  - M3: Modern App Shell & Investo.in UI (Obsidian dark theme, purple/indigo/magenta gradients, glassmorphism, 5 tabs, Plotly candlestick terminal).
  - M4: Integration & E2E Test Pass (100% pass on Tiers 1-4).
  - M5: Adversarial Hardening (Tier 5 challenger stress-testing, forensic integrity audit).

## Phase 2: Execution & Verification Gate
- Each milestone executes under strict gate: Explorer -> Worker -> Reviewer (x2) -> Challenger (x2) -> Forensic Auditor (x1).
- Non-negotiable binary audit veto.
- Pass 100% E2E tests and verify manual inspection at http://localhost:8000.
