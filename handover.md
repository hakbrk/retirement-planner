# Handover - April 21, 2026

## What We Fixed
1. **Projection uses youngest age** - Plan now ends based on youngest person (spouse), not Self
2. **Two-phase max spend** - Now calculates pre-59.5 and post-59.5 separately
3. **Added taxes** - Brokerage withdrawals now calculate capital gains tax

## Current Problem: Phase 1 Calculation Still Wrong

### Issue
Phase 1 (pre-59.5) is showing ~$12,500/mo but math says it should fail.

### Test Case
- Start date: April 2026
- Self DOB: Sept 1, 1974 → turns 59.5 in March 2034
- Months to 59.5: **95 months** (not 186)
- Accessible: $710K (Savings $223K + Brokerage $487K)
- Real return: ~3.4%/year

### Math Check
- $710K at 3.4% for 95 months = ~$929K
- At $12K/mo × 95 = $1.14M needed
- **Short by ~$211K** → should FAIL

### Where Debugging Stopped
The test_spend_level() function returns True (passes) when it should return False (fail).
Likely issues:
1. Growth rate might still be using nominal instead of real
2. Savings growth might not be using real rate
3. Something in withdrawal logic isn't working as expected

## What Needs Fixing

1. **Verify phase 1 duration**: Should use Self's age (59.5) not youngest, because Self has the locked retirement funds
2. **Debug growth rates**: Ensure both accounts and savings use real return (nominal - inflation)
3. **Fix test_spend_level**: Add debug prints to trace why it passes when it should fail
4. **Verify withdrawal logic**: Make sure it correctly fails when money runs out

## Files Modified
- `app/calculations.py` - Main calculation engine
- `app/main.py` - Streamlit UI (updated to show two phases)

## Test Data
Config file: `dashboard_config.json`
- Self: DOB 1974-09-01
- Spouse: DOB 1980-06-09
- Accessible: $710K
- Locked: $1.58M
