import streamlit as st
import pandas as pd
import requests
import os


menu = st.sidebar.selectbox("Menu", ["Home", "About", "Contact"])

if menu == "Home":
    st.title("🏠 Salary Advance Loan Calculator")

    with st.form("loan_form"):
        st.subheader("Loan Details")
        loan_amount = st.number_input("Enter Loan Amount", min_value=0)
        interest_rate = st.number_input(
            "Enter Interest Rate (%)", min_value=0.0, step=0.1
        )
        loan_term = st.number_input("Enter Loan Term (Months)", min_value=12, step=1)
        submit_button = st.form_submit_button("Calculate")
    if submit_button:
        if loan_amount > 0 and interest_rate >= 0 and loan_term > 0:
            backend_url = os.getenv("BACKEND_URL")
            # Make a POST request to the FastAPI backend
            response = requests.post(
                f"{backend_url}/calculate_loan",
                json={
                    "loan_amount": loan_amount,
                    "interest_rate": interest_rate,
                    "loan_term": loan_term,
                },
            )
            if response.status_code == 200:
                # df = pd.DataFrame([response.json()])
                # st.dataframe(df)
                st.dataframe(response.json())
            else:
                st.error("Error calculating loan details.")
        else:
            st.error("Please enter valid values for all fields.")
elif menu == "About":
    st.title("ℹ️ About")
elif menu == "Contact":
    st.title("📞 Contact")
