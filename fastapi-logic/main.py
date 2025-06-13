from fastapi import FastAPI
from typing import Annotated
from pydantic import BaseModel, Field
import pandas as pd

ap = FastAPI()


class Item(BaseModel):
    loan_amount: int
    interest_rate: float
    loan_term: int


@ap.post("/calculate_loan")
def calculate_loan(item: Item):
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
