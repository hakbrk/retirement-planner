# Retirement Cashflow Dashboard - Project Plan

## Goal
Replace Hawkins_Cashflow_Tool_Full_Rev26.xlsm with a sophisticated, trustworthy web-based dashboard that works on desktop and mobile.

## Users
- Primary: You
- Secondary: Spouse (view on mobile)

## Repo
https://github.com/hakbrk/retirement-planner

---

## Task List

### Phase 1 - MVP (Complete)
- [x] Personal data input (DOB, target age, reserve years)
- [x] Account input form (Brokerage, IRA, 401k, Roth, Savings)
- [x] Income tab (Pension, Social Security with COLA)
- [x] Expense tracking (one-time with date, recurring with frequency)
- [x] Basic projection to target age
- [x] Account access + RMD rules
- [x] After-tax spend output (federal tax)
- [x] Responsive dashboard view

### Phase 2 - Current
- [ ] Save/load user data (localStorage or JSON file)
- [ ] Add scenario comparison (retire now vs later)
- [ ] Investment return defaults by type (Brokerage 7%, Savings 2%, etc.)

### Phase 3 - Risk & Stress Testing
- [ ] Risk tolerance selector (Aggressive/Moderate/Conservative return rates)
- [ ] Monte Carlo simulation
- [ ] Stress test results (best/expected/worst case)
- [ ] Band visualization

### Phase 4 - Advanced
- [ ] Roth conversion scenario
- [ ] Tax optimization suggestions
- [ ] Rebalancing automation rules
- [ ] Investment-level modeling
- [ ] Rebalancing events (home sale, etc.)

---

## Core Features

### 1. Investment Accounts
- Brokerage, Traditional IRA, Roth IRA, 401k, 401k Roth, Savings
- Fields: Account name, type, balance, owner, expected return rate

### 2. Income Streams
- Pension, Social Security
- Monthly amount, start age, COLA flag

### 3. Expenses
- One-time: amount, date
- Recurring: amount, start age, end age, frequency (every X years/months), inflation adj

### 4. Personal Data
- Date of birth (self + spouse)
- Target end age, reserve requirement
- Inflation rate, filing status, state tax rate

### 5. Projection Engine
- Age-based spending limits
- Account access rules (59.5, pension rules)
- RMD calculations
- After-tax spendable amounts
- Scenario comparison
- Risk tolerance bands

---

## Tech Stack
- Open source only
- Web app (Streamlit, browser-based)
- Python 3.12