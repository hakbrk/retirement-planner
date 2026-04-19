import streamlit as st
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Retirement Dashboard", page_icon="📊", layout="wide")

INVESTMENT_TYPES = ["Brokerage", "Traditional IRA", "Roth IRA", "401k", "401k Roth", "Savings"]
OWNERS = ["Self", "Spouse"]

def calculate_age(birth_date):
    if birth_date is None:
        return None
    today = date.today()
    return relativedelta(today, birth_date).years

def calculate_rmd(age, balance):
    rmd_table = {
        72: 27, 73: 26, 74: 25, 75: 24, 76: 23, 77: 22, 78: 21, 79: 20, 80: 19,
        81: 18, 82: 17, 83: 16, 84: 15, 85: 14, 86: 13, 87: 12, 88: 11, 89: 10,
        90: 9, 91: 8, 92: 7, 93: 6, 94: 5, 95: 4, 96: 3, 97: 2, 98: 1, 99: 1, 100: 1
    }
    divisor = rmd_table.get(age, 1)
    return balance / divisor if divisor > 0 else balance

def calculate_tax(income, filing_status="Married Filing Jointly"):
    brackets = [
        (23850, 0.10),
        (96950, 0.12),
        (206700, 0.22),
        (394400, 0.24),
        (501950, 0.32),
        (751600, 0.35),
        (float('inf'), 0.37)
    ] if filing_status == "Married Filing Jointly" else [
        (11950, 0.10),
        (48450, 0.12),
        (103350, 0.22),
        (197300, 0.24),
        (250950, 0.35),
        (677050, 0.37),
        (float('inf'), 0.37)
    ]
    tax = 0
    remaining = income
    prev_limit = 0
    for limit, rate in brackets:
        if remaining <= 0:
            break
        taxable = min(remaining, limit - prev_limit)
        if taxable > 0:
            tax += taxable * rate
            remaining -= taxable
        prev_limit = limit
    return tax

def main():
    st.title("📊 Retirement Cashflow Dashboard")
    st.markdown("---")

    if "accounts" not in st.session_state:
        st.session_state.accounts = []
    if "incomes" not in st.session_state:
        st.session_state.incomes = []
    if "expenses" not in st.session_state:
        st.session_state.expenses = []

    col1, col2 = st.columns([2, 1])

    with col1:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Personal", "💰 Accounts", "💵 Income", "📋 Expenses", "📈 Projection"])

        with tab1:
            st.subheader("Personal Information")
            c1, c2 = st.columns(2)
            with c1:
                self_dob = st.date_input("Your Date of Birth", value=None, key="self_dob")
            with c2:
                spouse_dob = st.date_input("Spouse Date of Birth", value=None, key="spouse_dob")

            c3, c4, c5 = st.columns(3)
            with c3:
                target_age = st.number_input("Plan to Age", value=100, min_value=60, max_value=120, key="target_age")
            with c4:
                reserve_years = st.number_input("Reserve Years at End", value=2, min_value=0, max_value=10, key="reserve_years")
            with c5:
                inflation_rate = st.number_input("Inflation Rate (%)", value=3.0, min_value=0.0, max_value=20.0, step=0.5, key="inflation_rate") / 100

            c6, c7 = st.columns(2)
            with c6:
                filing_status = st.selectbox("Filing Status", ["Married Filing Jointly", "Single"], key="filing_status")
            with c7:
                state_tax_rate = st.number_input("State Tax Rate (%)", value=0.0, min_value=0.0, max_value=15.0, step=0.5, key="state_tax_rate") / 100

            if self_dob:
                self_age = calculate_age(self_dob)
                st.success(f"You are {self_age} years old")
            if spouse_dob:
                spouse_age = calculate_age(spouse_dob)
                st.success(f"Spouse is {spouse_age} years old")

        with tab2:
            st.subheader("Add Investment Account")
            with st.form("add_account"):
                c1, c2 = st.columns(2)
                with c1:
                    acct_name = st.text_input("Account Name", key="acct_name")
                with c2:
                    acct_type = st.selectbox("Account Type", INVESTMENT_TYPES, key="acct_type")

                c3, c4 = st.columns(2)
                with c3:
                    owner = st.selectbox("Owner", OWNERS, key="acct_owner")
                with c4:
                    balance = st.number_input("Balance ($)", min_value=0.0, step=1000.0, key="acct_balance")

                c5 = st.columns(1)[0]
                with c5:
                    return_rate = st.number_input("Expected Annual Return (%)", value=6.0, min_value=0.0, max_value=20.0, step=0.5, key="acct_return") / 100

                submit = st.form_submit_button("Add Account")
                if submit and acct_name:
                    st.session_state.accounts.append({
                        "name": acct_name,
                        "type": acct_type,
                        "owner": owner,
                        "balance": balance,
                        "return_rate": return_rate
                    })
                    st.rerun()

            st.subheader("Your Investment Accounts")
            accounts = st.session_state.accounts

            if accounts:
                for i, acc in enumerate(accounts):
                    with st.expander(f"{acc['name']} ({acc['type']}) - ${acc['balance']:,.0f}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            new_balance = st.number_input("Balance", value=acc["balance"], min_value=0.0, key=f"bal_{i}")
                        with c2:
                            new_return = st.number_input("Return (%)", value=acc["return_rate"]*100, min_value=0.0, max_value=20.0, step=0.5, key=f"ret_{i}") / 100
                        if st.button("Update", key=f"upd_{i}"):
                            accounts[i]["balance"] = new_balance
                            accounts[i]["return_rate"] = new_return
                            st.rerun()
                        if st.button("Delete", key=f"del_{i}"):
                            accounts.pop(i)
                            st.rerun()
            else:
                st.info("No investment accounts added yet")

        with tab3:
            st.subheader("Add Income Stream")
            with st.form("add_income"):
                c1, c2 = st.columns(2)
                with c1:
                    income_name = st.text_input("Income Name", key="income_name")
                with c2:
                    income_type = st.selectbox("Type", ["Pension", "Social Security"], key="income_type")

                c3, c4 = st.columns(2)
                with c3:
                    owner = st.selectbox("Owner", OWNERS, key="income_owner")
                with c4:
                    monthly_amount = st.number_input("Monthly Amount ($)", min_value=0.0, step=100.0, key="monthly_amount")

                c5, c6 = st.columns(2)
                with c5:
                    start_age = st.number_input("Start Age", min_value=0, max_value=120, value=62, key="income_start_age")
                with c6:
                    cola = st.checkbox("COLA Adjusted (Inflation Protected)?", value=True, key="cola")

                submit3 = st.form_submit_button("Add Income")
                if submit3 and income_name:
                    st.session_state.incomes.append({
                        "name": income_name,
                        "type": income_type,
                        "owner": owner,
                        "monthly_amount": monthly_amount,
                        "start_age": start_age,
                        "cola": cola
                    })
                    st.rerun()

            st.subheader("Your Income Streams")
            incomes = st.session_state.incomes

            if incomes:
                for i, inc in enumerate(incomes):
                    with st.expander(f"{inc['name']} - ${inc['monthly_amount']:,.0f}/month starting age {inc['start_age']}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            new_amount = st.number_input("Monthly", value=inc["monthly_amount"], min_value=0.0, key=f"inc_{i}")
                        with c2:
                            new_start = st.number_input("Start Age", value=inc["start_age"], min_value=0, max_value=120, key=f"sta_{i}")
                        if st.button("Update Income", key=f"updinc_{i}"):
                            incomes[i]["monthly_amount"] = new_amount
                            incomes[i]["start_age"] = new_start
                            st.rerun()
                        if st.button("Delete Income", key=f"delinc_{i}"):
                            incomes.pop(i)
                            st.rerun()
            else:
                st.info("No income streams added yet")

        with tab4:
            st.subheader("Add Expense")
            with st.form("add_expense"):
                c1, c2 = st.columns(2)
                with c1:
                    expense_name = st.text_input("Expense Name", key="exp_name")
                with c2:
                    expense_amount = st.number_input("Annual Amount ($)", min_value=0.0, step=100.0, key="exp_amount")

                c3, c4 = st.columns(2)
                with c3:
                    start_age = st.number_input("Start Age", min_value=0, max_value=120, value=51, key="exp_start")
                with c4:
                    end_age = st.number_input("End Age", min_value=0, max_value=120, value=100, key="exp_end")

                c5 = st.columns(1)[0]
                with c5:
                    freq = st.selectbox("Frequency", ["Annual", "Monthly", "Every 5 Years", "One-time"], key="exp_freq")

                submit2 = st.form_submit_button("Add Expense")
                if submit2 and expense_name:
                    st.session_state.expenses.append({
                        "name": expense_name,
                        "amount": expense_amount,
                        "start_age": start_age,
                        "end_age": end_age,
                        "freq": freq,
                        "inflation_adj": True
                    })
                    st.rerun()

            st.subheader("Your Expenses")
            expenses = st.session_state.expenses

            if expenses:
                for i, exp in enumerate(expenses):
                    with st.expander(f"{exp['name']} - ${exp['amount']:,.0f}/year"):
                        if st.button("Delete Expense", key=f"delexp_{i}"):
                            expenses.pop(i)
                            st.rerun()
            else:
                st.info("No expenses added yet")

        with tab5:
            st.subheader("Projection Results")

            if not self_dob:
                st.warning("Please enter your birth date")
            elif not accounts and not incomes:
                st.warning("Add accounts or income streams")
            else:
                results = run_projection(
                    self_dob, spouse_dob, target_age, reserve_years,
                    accounts, incomes, expenses, inflation_rate, filing_status, state_tax_rate
                )
                display_results(results)

    with col2:
        st.subheader("Summary")
        
        total_investments = sum(a["balance"] for a in accounts)
        st.metric("Total Investments", f"${total_investments:,.0f}")
        
        total_income = sum(inc["monthly_amount"] * 12 for inc in incomes)
        if total_income > 0:
            st.metric("Annual Income", f"${total_income:,.0f}")

        st.write("**Investment Accounts:**")
        for acc in accounts:
            st.write(f"- {acc['name']}: ${acc['balance']:,.0f} ({acc['return_rate']*100:.1f}%)")

        st.write("**Income Streams:**")
        for inc in incomes:
            st.write(f"- {inc['name']}: ${inc['monthly_amount']:,.0f}/mo" + (" (COLA)" if inc["cola"] else ""))

def run_projection(self_dob, spouse_dob, target_age, reserve_years, accounts, incomes, expenses, inflation_rate, filing_status, state_tax_rate):
    from datetime import date

    results = []
    base_year = date.today().year

    self_age = calculate_age(self_dob)
    spouse_age = calculate_age(spouse_dob) if spouse_dob else None

    younger_age = min(self_age, spouse_age) if spouse_age else self_age

    account_balances = {i: a["balance"] for i, a in enumerate(accounts)}

    for year_offset in range(target_age - younger_age + 1):
        current_self_age = self_age + year_offset
        current_spouse_age = (spouse_age + year_offset) if spouse_age else None
        current_younger_age = younger_age + year_offset

        if current_younger_age > 100:
            break

        income_from_accounts = 0
        rmd_amount = 0

        for i, acc in enumerate(accounts):
            balance = account_balances.get(i, acc["balance"])
            return_rate = acc["return_rate"]

            growth = balance * return_rate
            account_balances[i] = balance + growth

            access_age = 59.5
            if current_self_age >= access_age or (current_spouse_age and current_spouse_age >= access_age):
                if acc["type"] in ["Traditional IRA", "401k"] and current_self_age >= 73:
                    rmd = calculate_rmd(current_self_age, account_balances[i])
                    rmd_amount += rmd
                    account_balances[i] -= rmd
                    income_from_accounts += rmd

        income_from_pensions = 0
        for inc in incomes:
            if inc["start_age"] <= current_younger_age:
                amount = inc["monthly_amount"] * 12
                if not inc.get("cola"):
                    amount *= (1 + inflation_rate) ** year_offset
                income_from_pensions += amount

        total_income = income_from_accounts + income_from_pensions

        total_expenses = 0
        for exp in expenses:
            if exp["start_age"] <= current_younger_age <= exp["end_age"]:
                amount = exp["amount"]
                if exp.get("inflation_adj", True):
                    amount *= (1 + inflation_rate) ** year_offset
                if exp["freq"] == "Monthly":
                    amount *= 12
                elif exp["freq"] == "Every 5 Years":
                    if year_offset % 5 == 0:
                        pass
                    else:
                        amount = 0
                elif exp["freq"] == "One-time" and year_offset > 0:
                    amount = 0
                total_expenses += amount

        gross_income = total_income - total_expenses
        if gross_income < 0:
            gross_income = 0
        elif gross_income < 14600:
            federal_tax = 0
        else:
            federal_tax = calculate_tax(gross_income, filing_status)
        state_tax = gross_income * state_tax_rate

        after_tax = gross_income - federal_tax - state_tax

        results.append({
            "year": base_year + year_offset,
            "age": current_younger_age,
            "investment_growth": income_from_accounts,
            "rmd": rmd_amount,
            "pension_ss": income_from_pensions,
            "expenses": total_expenses,
            "gross": gross_income,
            "federal_tax": federal_tax,
            "state_tax": state_tax,
            "after_tax": after_tax,
            "total_assets": sum(account_balances.values()),
        })

    return results

def display_results(results):
    if not results:
        return

    df = pd.DataFrame(results)
    df["year"] = df["year"].astype(int)
    df["age"] = df["age"].astype(int)

    st.subheader("Yearly After-Tax Spendable")

    cols = st.columns(2)
    with cols[0]:
        st.metric("Average Annual Spend", f"${df['after_tax'].mean():,.0f}")
    with cols[1]:
        st.metric("First Year Spend", f"${df.iloc[0]['after_tax']:,.0f}")

    st.subheader("Projected Spend Over Time")
    chart_data = df[["year", "after_tax", "age"]].copy()
    st.line_chart(chart_data.set_index("year")["after_tax"])

    st.subheader("Detailed Projection")
    display_df = df.copy()
    for col in ["investment_growth", "rmd", "pension_ss", "expenses", "gross", "federal_tax", "state_tax", "after_tax", "total_assets"]:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    years_negative = len(df[df["after_tax"] < 0])
    if years_negative > 0:
        st.error(f"⚠️ Projection goes negative in {years_negative} years!")
    else:
        st.success("✓ Money lasts through target age!")

if __name__ == "__main__":
    main()