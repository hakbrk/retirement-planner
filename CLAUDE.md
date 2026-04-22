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

**Debug Phase 1 max spend calculation**. The `test_spend_level()` function incorrectly returns True when it should return False.

### Test Case
- Start date: April 2026
- Self DOB: Sept 1, 1974 → turns 59.5 in March 2034
- Months to 59.5: **95 months**
- Accessible funds (pre-59.5): $710K (Savings $223K + Brokerage $487K)
- Real return: ~3.4%/year
- Spending: $12K/mo

### Expected Behavior
Should FAIL because $710K + growth can't sustain $12K/mo for 95 months.

### Where to Debug
In `app/calculations.py`, the `test_spend_level()` method (line 544):
- Growth rate calculations may still be using nominal instead of real
- Savings growth might not be using real rate
- Withdrawal logic may not handle failure correctly

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