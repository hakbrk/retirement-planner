from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

def calculate_age(birth_date):
    if birth_date is None:
        return None
    today = date.today()
    return relativedelta(today, birth_date).years

def calculate_age_on_date(birth_date, target_date):
    if birth_date is None or target_date is None:
        return None
    return relativedelta(target_date, birth_date).years

def calculate_months_between(start_date, end_date):
    if start_date is None or end_date is None:
        return 0
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

def calculate_exact_age(birth_date, target_date):
    if birth_date is None or target_date is None:
        return None
    rd = relativedelta(target_date, birth_date)
    months = rd.months + rd.years * 12
    return rd.years + rd.months / 12

RMD_AGE_TABLE = {
    72: 27, 73: 26, 74: 25, 75: 24, 76: 23, 77: 22, 78: 21, 79: 20, 80: 19,
    81: 18, 82: 17, 83: 16, 84: 15, 85: 14, 86: 13, 87: 12, 88: 11, 89: 10,
    90: 9, 91: 8, 92: 7, 93: 6, 94: 5, 95: 4, 96: 3, 97: 2, 98: 1, 99: 1, 100: 1
}

def calculate_rmd(age, balance):
    divisor = RMD_AGE_TABLE.get(age, 1)
    return balance / divisor if divisor > 0 else balance

def calculate_rmd_irs_table(birth_year):
    life_expectancy_table = {
        1942: 83.4, 1943: 84.5, 1944: 85.3, 1945: 85.8, 1946: 86.2, 1947: 86.4, 1948: 86.5, 1949: 86.6,
        1950: 86.8, 1951: 87.0, 1952: 87.2, 1953: 87.4, 1954: 87.6, 1955: 87.8, 1956: 88.0, 1957: 88.2,
        1958: 88.4, 1959: 88.6, 1960: 88.8, 1961: 89.0, 1962: 89.2, 1963: 89.4, 1964: 89.6, 1965: 89.8,
        1966: 90.0, 1967: 90.4, 1968: 90.8, 1969: 91.2, 1970: 91.6, 1971: 92.0, 1972: 92.4, 1973: 92.8,
        1974: 93.2, 1975: 93.6, 1976: 94.0, 1977: 94.4, 1978: 94.8, 1979: 95.2, 1980: 95.6, 1981: 96.0,
        1982: 96.2, 1983: 96.4, 1984: 96.6, 1985: 96.8, 1986: 97.0, 1987: 97.2, 1988: 97.4, 1989: 97.6,
        1990: 97.8, 1991: 98.0, 1992: 98.2, 1993: 98.4, 1994: 98.6, 1995: 98.8, 1996: 99.0, 1997: 99.2,
        1998: 99.4, 1999: 99.6, 2000: 99.8, 2001: 100.0, 2002: 100.2, 2003: 100.4, 2004: 100.6, 2005: 100.8,
        2006: 101.0
    }
    le = life_expectancy_table.get(birth_year, 100)
    return max(1, le - 72 + (birth_year - 1942) * 0.2) if birth_year >= 1942 else 27

FEDERAL_BRACKETS_JOINT = [
    (23850, 0.10),
    (96950, 0.12),
    (206700, 0.22),
    (394400, 0.24),
    (501950, 0.32),
    (751600, 0.35),
    (float('inf'), 0.37)
]

FEDERAL_BRACKETS_SINGLE = [
    (11950, 0.10),
    (48450, 0.12),
    (103350, 0.22),
    (197300, 0.24),
    (250950, 0.35),
    (677050, 0.37),
    (float('inf'), 0.37)
]

LONG_TERM_CAPITAL_GAINS_BRACKETS = [
    (47025, 0.00),
        (518900, 0.15),
        (float('inf'), 0.20)
]

SHORT_TERM_CAPITAL_GAINS_BRACKETS = FEDERAL_BRACKETS_SINGLE

def calculate_federal_tax(income, filing_status="Married Filing Jointly"):
    if income <= 0:
        return 0
    brackets = FEDERAL_BRACKETS_JOINT if filing_status == "Married Filing Jointly" else FEDERAL_BRACKETS_SINGLE
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

def calculate_capital_gains_tax(gains, total_income, filing_status="Married Filing Jointly"):
    if gains <= 0:
        return 0
    brackets = LONG_TERM_CAPITAL_GAINS_BRACKETS
    taxable_gains = 0
    tax = 0
    prev_limit = 0
    for limit, rate in brackets:
        amount_in_bracket = limit - prev_limit
        if rate == 0.0:
            deductible = min(gains, amount_in_bracket)
            taxable_gains += deductible
            gains -= deductible
        else:
            taxable_gains += min(gains, amount_in_bracket)
        gains = max(0, gains - amount_in_bracket)
        prev_limit = limit
    return taxable_gains * 0.15

def ss_taxation_threshold(filing_status="Married Filing Jointly"):
    return 44000 if filing_status == "Married Filing Jointly" else 32000

def calculate_ss_taxation(ss_income, other_income, filing_status="Married Filing Jointly"):
    threshold = ss_taxation_threshold(filing_status)
    lesser_income = min(ss_income, other_income)
    if lesser_income <= 0:
        return 0
    taxable = min(0.5 * ss_income, 0.5 * lesser_income) if other_income > threshold else min(0.5 * ss_income, 0.5 * (other_income - threshold))
    return max(0, taxable) if other_income > threshold else 0

def is_tax_deferred(account_type):
    return account_type in ["Traditional IRA", "401k"]

def is_roth(account_type):
    return "Roth" in account_type

def is_taxable(account_type):
    return account_type in ["Brokerage", "Savings"]

def account_access_age(account_type):
    rules = {
        "Brokerage": 0,
        "Savings": 0,
        "Traditional IRA": 59.5,
        "Roth IRA": 59.5,
        "401k": 59.5,
        "401k Roth": 59.5,
    }
    return rules.get(account_type, 0)

def is_account_accessible(account_type, age):
    return age >= account_access_age(account_type)

ACCOUNT_WITHDRAWAL_ORDER = [
    ("Brokerage", "taxable"),
    ("Savings", "taxable"),
    ("Traditional IRA", "tax_deferred"),
    ("401k", "tax_deferred"),
    ("Roth IRA", "roth"),
    ("401k Roth", "roth"),
]

def get_withdrawal_priority(account_type):
    for i, (at, _) in enumerate(ACCOUNT_WITHDRAWAL_ORDER):
        if at == account_type:
            return i
    return 999

class Account:
    def __init__(self, name, account_type, owner, balance, return_rate):
        self.name = name
        self.account_type = account_type
        self.owner = owner
        self.balance = balance
        self.return_rate = return_rate
        self.growth = 0
        self.contributions = 0

    def apply_growth(self, monthly_rate):
        if self.balance > 0:
            self.growth = self.balance * monthly_rate
            self.balance += self.growth

    def withdraw(self, amount):
        available = min(self.balance, amount)
        self.balance -= available
        return available

    def deposit(self, amount):
        self.balance += amount

    def is_taxable(self):
        return is_taxable(self.account_type)

    def is_tax_deferred(self):
        return is_tax_deferred(self.account_type)

    def is_roth(self):
        return is_roth(self.account_type)


class SavingsAccount:
    def __init__(self, balance=0, rate=0.035):
        self.balance = balance
        self.rate = rate

    def apply_growth(self):
        self.balance *= (1 + self.rate)

    def withdraw(self, amount):
        available = min(self.balance, amount)
        self.balance -= available
        return available

    def deposit(self, amount):
        self.balance += amount

class IncomeStream:
    def __init__(self, name, income_type, owner, monthly_amount, start_age, end_age, cola):
        self.name = name
        self.income_type = income_type
        self.owner = owner
        self.monthly_amount = monthly_amount
        self.start_age = start_age
        self.end_age = end_age
        self.cola = cola
        self.current_amount = monthly_amount

    def update_for_inflation(self, inflation_rate, year_offset):
        if self.cola and year_offset > 0:
            self.current_amount *= (1 + inflation_rate) ** year_offset

class MonthlyProjection:
    def __init__(self, accounts, incomes, expenses, inflation_rate, filing_status, state_tax_rate,
                 start_date, end_age, rmd_age=73, self_dob=None, spouse_dob=None,
                 buffer_months=12, savings_rate=0.035):
        self.accounts = accounts
        self.incomes = incomes
        self.expenses = expenses
        self.inflation_rate = inflation_rate
        self.filing_status = filing_status
        self.state_tax_rate = state_tax_rate
        self.start_date = start_date
        self.end_age = end_age
        self.rmd_age = rmd_age
        self.self_dob = self_dob
        self.spouse_dob = spouse_dob
        self.buffer_months = buffer_months
        self.savings_rate = savings_rate
        self.monthly_inflation = (1 + inflation_rate) ** (1/12) - 1
        self.savings = SavingsAccount(balance=0, rate=savings_rate)

    def calculate_tax(self, annual_income):
        return calculate_federal_tax(annual_income, self.filing_status)

    def get_age_at_date(self, dob, target_date):
        if dob is None:
            return None
        return relativedelta(target_date, dob).years

    def get_exact_age(self, dob, target_date):
        if dob is None:
            return None
        rd = relativedelta(target_date, dob)
        return rd.years + rd.months / 12

    def get_month_date(self, month_offset):
        year = self.start_date.year + month_offset // 12
        month = self.start_date.month + month_offset % 12
        if month > 12:
            month -= 12
            year += 1
        return date(year, month if month > 0 else 12, 1)

    def calculate_monthly_income(self, month_offset, self_age, spouse_age):
        target_date = self.get_month_date(month_offset)
        income = {"self": 0, "spouse": 0}
        for inc in self.incomes:
            age = self_age if inc.owner == "Self" else spouse_age
            if age is None:
                age = self_age
            if inc.start_age <= age <= inc.end_age:
                inc.update_for_inflation(self.inflation_rate, month_offset // 12)
                income[inc.owner] += inc.current_amount
        return income

    def calculate_annual_expenses(self, year_offset):
        total = 0
        for exp in self.expenses:
            if exp["start_age"] <= year_offset:
                if exp["end_age"] == 0 or exp["end_age"] >= year_offset:
                    amount = exp["amount"]
                    if exp.get("inflation_adj", True):
                        amount *= (1 + self.inflation_rate) ** year_offset
                    total += amount
        return total

    def calculate_rmd_required(self, account, age):
        if age < self.rmd_age:
            return 0
        if is_tax_deferred(account.account_type):
            return calculate_rmd(age, account.balance)
        return 0

    def can_access(self, account, self_age, spouse_age):
        owner_age = self_age if account.owner in ["Self", "Both"] else spouse_age
        return is_account_accessible(account.account_type, owner_age)

    def get_accessible_balance(self, self_age, spouse_age):
        accessible = 0
        non_accessible = 0
        for acc in self.accounts:
            if self.can_access(acc, self_age, spouse_age):
                accessible += acc.balance
            else:
                non_accessible += acc.balance
        return accessible, non_accessible

    def withdraw_tax_efficient(self, amount_needed, self_age, spouse_age):
        if amount_needed <= 0:
            return {}

        available = {}
        remaining = amount_needed

        sorted_accounts = sorted(self.accounts, key=lambda a: get_withdrawal_priority(a.account_type))

        for acc in sorted_accounts:
            if not self.can_access(acc, self_age, spouse_age):
                continue
            if acc.balance <= 0:
                continue

            withdrawn = acc.withdraw(remaining)
            remaining -= withdrawn
            key = f"{acc.name}_{acc.account_type}"
            if key not in available:
                available[key] = 0
            available[key] += withdrawn

            if remaining <= 0:
                break

        return available

    def deposit_to_brokerage(self, amount):
        for acc in self.accounts:
            if acc.account_type == "Brokerage":
                acc.deposit(amount)
                return
        if self.accounts:
            self.accounts[0].deposit(amount)

    def rebalance_for_buffer(self, annual_expenses, prior_year_tax, self_age, spouse_age):
        target_savings = (annual_expenses + prior_year_tax) * (1 + self.buffer_months / 12)
        
        current_savings = self.savings.balance
        current_savings *= (1 + self.savings_rate)
        
        shortfall = max(0, target_savings - current_savings)
        
        if shortfall > 0:
            withdrawals = self.withdraw_tax_efficient(shortfall, self_age, spouse_age)
            for amount in withdrawals.values():
                self.savings.deposit(amount)
        
        excess = max(0, current_savings - target_savings)
        if excess > 0:
            self.savings.withdraw(excess)
            self.deposit_to_brokerage(excess)

    def run_projection(self, monthly_spend):
        results = []
        
        self_age = self.get_age_at_date(self.self_dob, self.start_date) if self.self_dob else calculate_age(self.start_date)
        spouse_age = self.get_age_at_date(self.spouse_dob, self.start_date) if self.spouse_dob else self_age - 2

        total_months = (self.end_age - self_age) * 12 if self_age else 600

        prior_year_income = 0
        prior_year_withdrawals = 0
        prior_year_tax = 0

        current_year = self.start_date.year

        for month in range(total_months):
            month_offset = month
            target_date = self.get_month_date(month_offset)
            
            current_self_age = self.get_exact_age(self.self_dob, target_date) if self.self_dob else self_age + month_offset / 12
            current_spouse_age = self.get_exact_age(self.spouse_dob, target_date) if self.spouse_dob else spouse_age + month_offset / 12

            if target_date.month == 1 and target_date.year > current_year:
                self.savings.apply_growth()
                annual_expenses = self.calculate_annual_expenses(target_date.year - self.start_date.year)
                self.rebalance_for_buffer(annual_expenses, prior_year_tax, current_self_age, current_spouse_age)
                current_year = target_date.year

            income = self.calculate_monthly_income(month_offset, current_self_age, current_spouse_age)
            income_total = income.get("self", 0) + income.get("spouse", 0)

            self.savings.deposit(income_total)

            expenses = monthly_spend
            savings_withdrawal = self.savings.withdraw(expenses)

            for acc in self.accounts:
                acc.apply_growth(self.monthly_inflation)

            rmd_total = 0
            for acc in self.accounts:
                rm_age = current_self_age if acc.owner in ["Self", "Both"] else current_spouse_age
                if rm_age and rm_age >= self.rmd_age:
                    rmd = self.calculate_rmd_required(acc, int(rm_age))
                    if rmd > 0:
                        acc.balance -= rmd
                        rmd_total += rmd

            taxable_income = income_total + rmd_total - 14600/12
            if taxable_income > 0:
                federal_tax = self.calculate_tax((income_total + rmd_total) * 12) / 12
            else:
                federal_tax = 0

            state_tax = (income_total + rmd_total) * self.state_tax_rate / 12
            after_tax = income_total + rmd_total - expenses - federal_tax - state_tax

            if target_date.month == 12:
                prior_year_income = income_total * 12
                prior_year_withdrawals = 0
                prior_year_tax = (federal_tax + state_tax) * 12

            accessible, non_accessible = self.get_accessible_balance(current_self_age, current_spouse_age)

            results.append({
                "month": month + 1,
                "year": target_date.year,
                "self_age": int(current_self_age) if current_self_age else None,
                "spouse_age": int(current_spouse_age) if current_spouse_age else None,
                "income": income_total,
                "savings_withdrawal": savings_withdrawal,
                "rmd": rmd_total,
                "expenses": expenses,
                "federal_tax": federal_tax,
                "state_tax": state_tax,
                "savings_balance": self.savings.balance,
                "accessible": accessible,
                "non_accessible": non_accessible,
                "total_assets": sum(a.balance for a in self.accounts),
            })

        return results

    def find_max_sustainable_spend(self, target_months=None):
        total_assets = sum(a.balance for a in self.accounts) + 240000
        if total_assets <= 0:
            return 0
            
        if target_months is None:
            if self.self_dob:
                current_age = self.get_age_at_date(self.self_dob, self.start_date)
            else:
                current_age = 50
            target_months = (self.end_age - current_age) * 12

        low = 0
        high = total_assets / (target_months / 12) * 0.5
        best = 0

        for _ in range(50):
            test_amount = (low + high) / 2
            if self.test_spend_level(test_amount, target_months):
                best = test_amount
                low = test_amount
            else:
                high = test_amount

        return best

    def test_spend_level(self, monthly_spend, months):
        temp_accounts = [Account(a.name, a.account_type, a.owner, a.balance, a.return_rate) for a in self.accounts]
        temp_incomes = [IncomeStream(i.name, i.income_type, i.owner, i.monthly_amount, i.start_age, i.end_age, i.cola) for i in self.incomes]
        temp_savings = SavingsAccount(balance=240000, rate=self.savings_rate)

        for month in range(months):
            month_offset = month
            target_date = self.get_month_date(month_offset)
            
            self_age = self.get_exact_age(self.self_dob, target_date) if self.self_dob else 50 + month_offset / 12
            spouse_age = self.get_exact_age(self.spouse_dob, target_date) if self.spouse_dob else 48 + month_offset / 12

            income = 0
            for inc in temp_incomes:
                age = self_age if inc.owner == "Self" else spouse_age
                if inc.start_age <= age <= inc.end_age:
                    income += inc.current_amount

            temp_savings.deposit(income)
            savings_withdrawal = temp_savings.withdraw(monthly_spend)

            for acc in temp_accounts:
                acc.apply_growth(acc.return_rate / 12)

            short_fall = monthly_spend - savings_withdrawal
            if short_fall > 0:
                sorted_accounts = sorted(temp_accounts, key=lambda a: get_withdrawal_priority(a.account_type))
                for acc in sorted_accounts:
                    if not self.can_access(acc, self_age, spouse_age):
                        continue
                    if acc.balance > 0:
                        available = acc.withdraw(short_fall)
                        short_fall -= available
                        temp_savings.deposit(available)
                        if short_fall <= 0:
                            break
                if short_fall > 0:
                    return False

            if target_date.month == 12:
                temp_savings.apply_growth()

        return temp_savings.balance > 0 or sum(a.balance for a in temp_accounts) > 0