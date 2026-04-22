# Agent Instructions

## Read First
Before starting work, read:
- `handover.md` - Current state and what was being debugged
- `plan.md` - Overall project plan and phases

## Project Context
This is a retirement cashflow dashboard replacing an Excel spreadsheet. It's a Streamlit Python app.

## Current Priority
Debug Phase 1 max spend calculation. The test_spend_level() function is incorrectly returning True (passing) when it should return False.

## Key Files
- `app/calculations.py` - Core calculation engine
- `app/main.py` - Streamlit UI
- `dashboard_config.json` - Test data

## Test Command
```bash
cd /mnt/d/OneDrive/Projects/Open_Code/retirement_dashboard
uv run python -c "
from app.calculations import Account, IncomeStream, MonthlyProjection
from datetime import date
import json

with open('dashboard_config.json') as f:
    config = json.load(f)

proj = MonthlyProjection(
    [Account(acc['name'], acc['type'], acc['owner'], acc['balance'], acc['return_rate']) for acc in config['accounts']],
    [IncomeStream(inc['name'], inc['type'], inc['owner'], inc['monthly_amount'], inc['start_age'], inc['end_age'], inc['cola']) for inc in config['incomes']],
    config['expenses'],
    inflation_rate=config['personal']['inflation_rate']/100,
    filing_status=config['personal']['filing_status'],
    state_tax_rate=config['personal']['state_tax_rate'],
    start_date=date(2026, 4, 1),
    end_age=config['personal']['target_age'],
    rmd_age=config['personal']['rmd_age'],
    self_dob=date.fromisoformat(config['personal']['self_dob']),
    spouse_dob=date.fromisoformat(config['personal']['spouse_dob']),
    buffer_months=12,
    savings_rate=0.035
)

# This should FAIL but returns True
result = proj.test_spend_level(12000, 95, include_income=False)
print('Result:', result)
"
```

## Expected Behavior
Phase 1 (pre-59.5) with:
- 95 months
- $710K accessible
- ~3.4% real return
- $12K/mo spending

Should FAIL because $710K + growth can't sustain $12K/mo for 95 months.
