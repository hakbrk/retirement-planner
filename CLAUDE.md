# CLAUDE.md - Retirement Dashboard

## Project Overview

This is a retirement cashflow dashboard built with Streamlit and Python 3.12. It replaces an Excel spreadsheet (Hawkins_Cashflow_Tool_Full_Rev26.xlsm) with a sophisticated web-based retirement planning tool.

**Repo**: https://github.com/hakbrk/retirement-planner

## Tech Stack

- Python 3.12
- Streamlit (web framework)
- pandas (data handling)
- dateutil (date calculations)

## Running the App

```bash
cd /mnt/d/OneDrive/Projects/Open_Code/retirement_dashboard
uv run streamlit run app/main.py
```

Open http://localhost:8501 in your browser.

## Key Files

| File | Description |
|------|-------------|
| `app/main.py` | Streamlit UI |
| `app/calculations.py` | Core engine (Account, IncomeStream, MonthlyProjection) |
| `dashboard_config.json` | User data (gitignored) |
| `pyproject.toml` | Project config |

## Current Development Priority

**Phase 4**: Audit tab and scenario comparison. The two-phase max spend calculation has been overhauled and should now be producing realistic results. Next step is to run the app and verify outputs before building the audit tab.

## Max Spend Calculation — Design Notes

The two-phase max spend logic in `find_max_sustainable_spend()` works as follows:

### Phase Boundary
`get_primary_unlock_months()` finds the phase boundary by scanning all locked accounts (IRA, 401k, Roth) and determining which owner — Self or Spouse — holds the larger total locked balance. The phase split occurs when that owner turns 59.5. Smaller unlocks that happen mid-phase are handled naturally inside `test_spend_level()` via `can_access()`.

### Joint Optimization
Phase 1 and Phase 2 are optimized jointly via `test_two_phase_spend()`. The binary search finds the maximum base spend sustainable across **both** phases — this prevents Phase 1 from over-spending and stranding Phase 2. Phase 2 is then separately optimized upward from the Phase 1 ending balance; it will be >= Phase 1 by construction, and higher when income (pension, SSI) kicks in.

### Key Bugs Fixed (April 2026)
- `_binary_search_spend`: double-counted Savings balance in upper bound (inflated search range)
- `start_balance_phase_2`: used hardcoded $240K savings instead of actual balance
- `start_balance_phase_2`: grew accounts at nominal rate instead of real rate
- `start_balance_phase_2`: incorrectly credited income during Phase 1 simulation (Phase 1 runs with `include_income=False`)
- Phase boundary used youngest person's 59.5 instead of the owner with the largest locked balance

## Project Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | Complete | MVP - accounts, incomes, expenses, basic projection |
| 2 | Complete | Monthly cashflow engine with tax-efficient withdrawal |
| 3 | Complete | Buffer model, rebalancing, 59.5 access rules |
| 4 | In Progress | Audit tab, scenario comparison |
| 5 | Pending | Risk testing, Monte Carlo |
| 6 | Pending | Roth conversion, tax optimization |

## Core Classes

- `Account`: Investment accounts (Brokerage, IRA, 401k, Roth, Savings)
- `IncomeStream`: Pension, Social Security, Dividend, Interest
- `MonthlyProjection`: Main projection engine with two-phase max spend

## Configuration

User data is stored in `dashboard_config.json`:
- Personal: DOB, target age, RMD age, inflation, filing status
- Accounts: balance, type, owner, return rate
- Incomes: amount, type, owner, start/end age, COLA
- Expenses: amount, start/end age, inflation adjustment