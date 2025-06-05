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
    balance = principal
    schedule = []

    for n in range(1, loan_term + 1):
        interest = balance * monthly_interest_rate
        principal_paid = payment - interest
        balance -= principal_paid

        if n == loan_term and abs(balance) < 0.01:
            principal_paid += balance
            payment += balance
            balance = 0

        schedule.append(
            {
                "Payment #": n,
                "Payment": round(payment, 2),
                "Principal Paid": round(principal_paid, 2),
                "Interest Paid": round(interest, 2),
                "Remaining Balance": round(balance, 2),
            }
        )
    return schedule
