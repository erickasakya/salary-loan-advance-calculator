from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel, Field
import pandas as pd

app = FastAPI()


class loan(BaseModel):
    loan_amount: int
    interest_rate: float
    loan_term: int


class advance(BaseModel):
    salary: float
    frequency: int
    loan_amount: float


@app.post("/calculate_advance")
def calculate_advance(item: advance):
    # You can only get 75%  of your salary as an advance loan
    monthly_salary = item.salary / item.frequency

    if item.salary <= 0 or item.frequency <= 0 or item.loan_amount <= 0:
        raise HTTPException(
            status_code=400, detail="Please enter valid values for all fields."
        )
    if item.loan_amount > 0.75 * monthly_salary:
        raise HTTPException(
            status_code=400,
            detail=f"You don't qualify for the loan amount {item.loan_amount:,.2f} requested. "
            "Loan amount cannot exceed 75% of your monthly salary.",
        )

    # If all checks pass, calculate the advance loan details
    max_loan_amount = 0.75 * monthly_salary
    return {
        "max_loan_amount": f"{max_loan_amount:,.2f}",
        "requested_loan_amount": f"{item.loan_amount:,.2f}",
    }


@app.post("/calculate_loan")
def calculate_loan(item: loan):
    principal = item.loan_amount
    interest_rate = item.interest_rate
    loan_term = item.loan_term

    if principal <= 0 or interest_rate < 0 or loan_term <= 0:
        raise ValueError("Please enter valid values for all fields.")

    monthly_interest_rate = interest_rate / 100 / 12
    payment = (
        principal
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term)
        / ((1 + monthly_interest_rate) ** loan_term - 1)
    )

    df = pd.DataFrame(index=range(1, loan_term + 1))
    df.index.name = "Payment #"
    df["Payment"] = round(payment, 2)
    balance = principal

    principal_paid_list = []
    interest_paid_list = []
    balance_list = []

    for _ in df.index:
        interest = balance * monthly_interest_rate
        principal_paid = payment - interest
        balance -= principal_paid

        if balance < 0.01:
            principal_paid += balance
            payment += balance
            balance = 0

        principal_paid_list.append(round(principal_paid, 2))
        interest_paid_list.append(round(interest, 2))
        balance_list.append(round(balance, 2))

    df["Principal Paid"] = principal_paid_list
    df["Interest Paid"] = interest_paid_list
    df["Remaining Balance"] = balance_list
    df["Cumulative Interest"] = df["Interest Paid"].cumsum()
    df["Cumulative Principal"] = df["Principal Paid"].cumsum()

    return df
