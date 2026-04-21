import streamlit as st
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.calculations import (
    calculate_age, calculate_federal_tax, calculate_rmd, calculate_ss_taxation,
    Account, IncomeStream, MonthlyProjection, calculate_rmd_irs_table
)

st.set_page_config(page_title="Retirement Dashboard", page_icon="📊", layout="wide")

INVESTMENT_TYPES = ["Brokerage", "Traditional IRA", "Roth IRA", "401k", "401k Roth", "Savings"]
OWNERS = ["Self", "Spouse", "Both"]

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
            min_date = date(1920, 1, 1)
            c1, c2 = st.columns(2)
            with c1:
                self_dob = st.date_input("Your Date of Birth", value=None, min_value=min_date, key="self_dob")
            with c2:
                spouse_dob = st.date_input("Spouse Date of Birth", value=None, min_value=min_date, key="spouse_dob")

            c3, c4, c5 = st.columns(3)
            with c3:
                target_age = st.number_input("Plan to Age", value=100, min_value=60, max_value=120, key="target_age")
            with c4:
                rmd_age = st.number_input("RMD Age", value=73, min_value=70, max_value=75, key="rmd_age")
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
                    st.session_state.acct_name = ""
                    st.session_state.acct_balance = 0.0
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
                    income_type = st.selectbox("Type", ["Pension", "Social Security", "Dividend", "Interest"], key="income_type")

                c3, c4 = st.columns(2)
                with c3:
                    owner = st.selectbox("Owner", ["Self", "Spouse"], key="income_owner")
                with c4:
                    monthly_amount = st.number_input("Monthly Amount ($)", min_value=0.0, step=100.0, key="monthly_amount")

                c5, c6 = st.columns(2)
                with c5:
                    start_age = st.number_input("Start Age", min_value=0, max_value=120, value=62, key="income_start_age")
                with c6:
                    end_age = st.number_input("End Age (0 = never ends)", min_value=0, max_value=120, value=0, key="income_end_age")

                c7, c8 = st.columns(2)
                with c7:
                    cola = st.checkbox("COLA Adjusted (Inflation Protected)?", value=True, key="cola")
                with c8:
                    pass

                submit3 = st.form_submit_button("Add Income")
                if submit3 and income_name:
                    st.session_state.incomes.append({
                        "name": income_name,
                        "type": income_type,
                        "owner": owner,
                        "monthly_amount": monthly_amount,
                        "start_age": start_age,
                        "end_age": end_age,
                        "cola": cola
                    })
                    st.session_state.income_name = ""
                    st.session_state.monthly_amount = 0.0
                    st.rerun()

            st.subheader("Your Income Streams")
            incomes = st.session_state.incomes

            if incomes:
                for i, inc in enumerate(incomes):
                    with st.expander(f"{inc['name']} - ${inc['monthly_amount']:,.0f}/mo"):
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
                    expense_name = st.text_input("Expense Name", key="expense_name")
                with c2:
                    expense_type = st.selectbox("Type", ["Monthly", "Annual", "One-time"], key="expense_type")

                c3, c4 = st.columns(2)
                with c3:
                    amount = st.number_input("Amount ($)", min_value=0.0, step=100.0, key="expense_amount")
                with c4:
                    start_age = st.number_input("Start Age", min_value=0, max_value=120, value=50, key="exp_start_age")

                c5, c6 = st.columns(2)
                with c5:
                    end_age = st.number_input("End Age (0 = never ends)", min_value=0, max_value=120, value=0, key="exp_end_age")
                with c6:
                    inflation_adj = st.checkbox("Inflation Adjusted?", value=True, key="exp_inf_adj")

                expense_date = None
                if expense_type == "One-time":
                    expense_date = st.date_input("Date", value=None, key="exp_date")

                submit2 = st.form_submit_button("Add Expense")
                if submit2 and expense_name:
                    st.session_state.expenses.append({
                        "name": expense_name,
                        "expense_type": expense_type,
                        "amount": amount,
                        "start_age": start_age,
                        "end_age": end_age,
                        "inflation_adj": inflation_adj,
                        "date": expense_date
                    })
                    st.rerun()

            st.subheader("Your Expenses")
            expenses = st.session_state.expenses

            if expenses:
                for i, exp in enumerate(expenses):
                    with st.expander(f"{exp['name']} - ${exp['amount']:,.0f}"):
                        if st.button("Delete Expense", key=f"delexp_{i}"):
                            expenses.pop(i)
                            st.rerun()
            else:
                st.info("No expenses added yet")

        with tab5:
            st.subheader("Projection Results")

            if not self_dob:
                st.warning("Please enter your birth date")
            elif not accounts:
                st.warning("Add investment accounts")
            else:
                accounts = st.session_state.accounts
                incomes = st.session_state.incomes
                expenses = st.session_state.expenses
                
                account_objs = [Account(a["name"], a["type"], a["owner"], a["balance"], a["return_rate"]) for a in accounts]
                income_objs = [IncomeStream(i["name"], i["type"], i["owner"], i["monthly_amount"], i["start_age"], i["end_age"], i["cola"]) for i in incomes]
                
                start_date = date.today()
                projection = MonthlyProjection(
                    account_objs, income_objs, expenses,
                    inflation_rate, filing_status, state_tax_rate,
                    start_date, target_age, rmd_age
                )
                
                m1, m2 = st.columns(2)
                with m1:
                    show_monthly = st.toggle("Show Monthly", value=False)
                with m2:
                    calculate_max = st.button("Calculate Max Sustainable Spend", type="secondary")
                
                if calculate_max:
                    with st.spinner("Calculating max sustainable spend..."):
                        max_spend = projection.find_max_sustainable_spend()
                    st.success(f"Max sustainable monthly spend: ${max_spend:,.0f}")
                
                default_spend = st.number_input("Monthly Spend to Project ($)", value=10000, min_value=0, step=500, key="monthly_spend")
                
                results = projection.run_projection(default_spend)
                
                if show_monthly:
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    yearly_df = []
                    for i in range(0, len(results), 12):
                        chunk = results[i:i+12]
                        if chunk:
                            yearly_df.append({
                                "year": chunk[0]["year"],
                                "age": chunk[0]["age"],
                                "income": sum(r["income"] for r in chunk),
                                "withdrawals": sum(r["withdrawals"] for r in chunk),
                                "rmd": sum(r["rmd"] for r in chunk),
                                "expenses": sum(r["expenses"] for r in chunk),
                                "federal_tax": sum(r["federal_tax"] for r in chunk),
                                "state_tax": sum(r["state_tax"] for r in chunk),
                                "after_tax": sum(r["after_tax"] for r in chunk),
                                "total_assets": chunk[-1]["total_assets"] if chunk else 0
                            })
                    df = pd.DataFrame(yearly_df)
                    display_df = df.copy()
                    for col in ["income", "withdrawals", "rmd", "expenses", "federal_tax", "state_tax", "after_tax", "total_assets"]:
                        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.subheader("Asset Balance Over Time")
                if results:
                    chart_data = []
                    for i in range(0, len(results), 12):
                        chunk = results[i]
                        if chunk:
                            chart_data.append({"year": chunk["year"], "age": chunk["age"], "assets": chunk["total_assets"]})
                    chart_df = pd.DataFrame(chart_data)
                    st.line_chart(chart_df.set_index("year")["assets"])
                
                if results and results[-1]["total_assets"] <= 0:
                    st.error("⚠️ Money runs out before target age!")
                else:
                    st.success(f"✓ Money lasts through age {target_age}")

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
            st.write(f"- {inc['name']}: ${inc['monthly_amount']:,.0f}/mo" + (" (COLA)" if inc.get("cola") else ""))

if __name__ == "__main__":
    main()